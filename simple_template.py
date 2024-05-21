import json

import javalang
import javalang.tokenizer
import regex as re


def match_conditional_expression(code):
    ret = []
    if re.match(r"if\s?\(.+\)\s?{$", code):
        s_code = code.split(")")
        pre_code = ")".join(s_code[:-1])
        post_code = ")" + s_code[-1]
        ret.append((pre_code + ' &&', post_code))
        ret.append((pre_code + ' ||', post_code))

    return ret


def match_calling_function(code, tokenizer):
    ret = []
    matches = re.finditer(r"[^)(\s]+\([^)(]+\)", code)
    for match in matches:
        matched_code = match.group()
        sc = code.split(matched_code)
        if len(sc) != 2:
            continue
        matched_code.split("(")
        ret.append((sc[0] + "<mask>" + "(" + "".join(matched_code.split("(")[1:]) + sc[1],
                    tokenizer(matched_code.split("(")[0], return_tensors='pt')['input_ids'].size()[1] - 2))

    return ret


def match_function_api_call(code, tokenizer):  # lowest level
    ret = []
    matches = re.finditer(r"\([^)(]+\)", code)
    for match in matches:  # Match single function api print(abc)
        matched_code = match.group()
        sc = code.split(matched_code)
        new_code = "(<mask>)".join(sc)

        if new_code not in [v[0] for v in ret]:
            ret.append((new_code, tokenizer(matched_code[1:-1], return_tensors='pt')['input_ids'].size()[1] - 2))

    return ret


def _match_function_multi_input_api_call_generate_template(matched_code, tokenizer):
    ret = []
    parameters = matched_code.split(",")
    max = 0
    for parameter in parameters:
        size = tokenizer(parameter, return_tensors='pt')['input_ids'].size()[1] - 2
        if size > max:
            max = size

    ret.append(("(<mask>, " + matched_code + ")", max))  # add variable in beginning
    ret.append(("(" + matched_code + ",<mask>" + ")", max))  # add variable in end

    for index, parameter in enumerate(parameters):
        new_code = "("
        for jindex in range(len(parameters)):
            add_code = "<mask>"
            if index != jindex:
                add_code = parameters[jindex]

            if jindex != 0:
                new_code += "," + add_code
            else:
                new_code += add_code
        new_code += ")"
        ret.append((new_code, max))

    return ret


def match_function_multi_input_api_call(code, tokenizer):  # lowest level

    ret = []
    matches = re.finditer(r"\([^)(]+,[^)(]+\)", code)
    for match in matches:  # Match single function api print(abc)
        matched_code = match.group()
        sc = code.split(matched_code)
        if len(sc) != 2:
            continue
        matched_code = matched_code[1:-1]
        for p_code in _match_function_multi_input_api_call_generate_template(matched_code, tokenizer):
            ret.append((sc[0] + p_code[0] + sc[1], p_code[1]))
    return ret


def match_simple_operator(code, tokenizer):
    u_operator = ['!=', '>=', '<=', '==', '<', '>' '%=', '^=', '|=', '&=', '/=', '*=', '-=', '+=']
    ret = [""]

    try:
        tokens = list(javalang.tokenizer.tokenize(code))
    except:
        return []
    current_index = 1
    for token in tokens:
        while current_index < token.position[1]:
            current_index += 1
            ret = [v + " " for v in ret]

        if token.__class__.__name__ == 'Operator':
            for index in range(1, len(ret)):
                ret[index] = ret[index] + token.value
            ret.append(ret[0] + "2mask2")
            ret[0] = ret[0] + token.value

        current_index += len(token.value)
        if not token.__class__.__name__ == 'Operator':
            ret = [v + token.value for v in ret]

    ret = [v.replace(" 2mask2", "<mask>") for v in ret]
    ret = [v.replace("2mask2", "<mask>") for v in ret]
    ret = ret[1:]
    print("Simple Operator Templates:")
    return ret


def generate_match_template(code, tokenizer):
    ret = []

    # Not very smart templates
    ret.extend(match_function_api_call(code, tokenizer))
    ret.extend(match_function_multi_input_api_call(code, tokenizer))
    ret.extend(match_calling_function(code, tokenizer))
    print("Match Templates:")
    return ret


def parse_code_file(code):
    # print(code)
    tokens = javalang.tokenizer.tokenize(code)
    parser = javalang.parser.Parser(tokens)
    tree = parser.parse()
    for path, node in tree:
        print(node)
        print(node.position)


def parse_code_begin(code):
    ret_list = []
    string_builder = ""
    try:
        tokens = list(javalang.tokenizer.tokenize(code))
    except:
        return ret_list
    current_index = 1
    for token in tokens:
        while current_index < token.position[1]:
            current_index += 1
            string_builder += " "

        if string_builder != "":
            ret_list.append(string_builder)

        string_builder += token.value
        current_index += len(token.value)

    return ret_list


def parse_code_end(code):
    ret_list = []
    string_builder = ""
    try:
        tokens = list(javalang.tokenizer.tokenize(code))
    except:
        return ret_list
    tokens.reverse()
    current_index = len(code) + 1

    for token in tokens:
        current_index -= len(token.value)
        if string_builder != "":
            ret_list.append(string_builder)

        while current_index > token.position[1]:
            current_index -= 1
            string_builder = " " + string_builder

        string_builder = token.value + string_builder

    return ret_list


def remove_redudant(ret):
    real_ret = []
    past_code = set()
    for c in ret:
        patch_code = c[0].replace(" ", "").replace("#", "").replace("\n", "").replace("\t", "")
        if patch_code in past_code:
            continue

        past_code.add(patch_code)
        real_ret.append(c)

    return real_ret


def generate_template(code):
    ret = []

    for pre_code in parse_code_begin(code):
        ret.append((pre_code, ""))

    for post_code in parse_code_end(code):
        ret.append(("", post_code))

    ret.extend(match_conditional_expression(code))
    print("Front and Back Templates:")
    print(ret)
    return ret


def generate_middle_template(code):
    ret_list = []
    tokens = list(javalang.tokenizer.tokenize(code))
    for token in tokens:

        if token.__class__.__name__ != "Separator":
            ret_list.append(token.value)

    print(ret_list)

    return ret_list
