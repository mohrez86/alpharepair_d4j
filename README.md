# Running AlphaRepair on Defects4J

## Download AlphaRepair's Replication Package

[AlphaRepair's replication package](https://zenodo.org/records/6819444)
is on Zenodo. I have already downloaded Version 2 and
included it in this repository. To do so, I downloaded `code.zip` and
extracted its content into the root directory.
The `correct_patches.zip` file is not needed for this setup.

## Installing Defects4J

AlphaRepair is a dynamic analysis tool written in Python.
It needs Defects4J to run tests and to validate patches.
So, you need to install Defects4J on your machine.
The original version of the replication package is developed
to work with Defects4j versions 1.2 and 2.0.
I recommend using version 1.2 as the current replication
package of AlphaRepair includes fault localization
information only for subjects 
in Defects4j version 1.2 (see [the location directory](location)).

To install Defects4J 1.2 on your machine, follow
the instructions provided
[here](https://github.com/rjust/defects4j/tree/v1.2.0).
Do not forget to checkout the correct repo version, and
make sure to add Defects4J's executables to your PATH
as described in step 3 of Defects4J's installation process.

## Python Environment Dependencies

AlphaRepair is a Python project. However, its replication
package does not include information about
its dependencies.
So I added the [requirements.txt](requirements.txt) file,
which contains the requirements for running AlphaRepair on CPU (not GPU).
I have only tested it on CPU. If you have GPU, let me know
so that I can prepare another `requirements.txt` that supports
GPU 
([more information on installing the Transformers library](https://huggingface.co/docs/transformers/en/installation)).

1. Create a conda environment. I tested everything using Python 3.11,
but other Python versions should also work.

```bash
conda create -n alpharepair3.11 python=3.11
```

2. Activate the environment we just created:

```bash
conda activate alpharepair3.11
```

3. Install AlphaRepair's dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running AlphaRepair

Due to a bug in AlphaRepair, you must create a directory named `codebert_result`
in the root directory to prevent AlphaRepair from crashing.
I have already added this directory to the root for your convenience.

AlphaRepair supports the following command line arguments:

- **--bug_id:**
Defects4J bug id. For instance, `Lang-1` refers to bug #1 from the Lang project.
To see the list of supported bug ids for perfect fault localization,
see directory [location/groundtruth](location/groundtruth).
For bug ids supported for Ochiai-based fault localization,
see directory [location/ochiai](location/ochiai).

- **--uniapr:** Indicates whether to use uniapr. According to the paper,
using uniapr speeds up patch validation. If
it does not work, simply do not use it.

- **--output_folder:** The directory to store the patches.
The default is `codebert_result`. Because of the bug and workaround
mentioned above, use the default by not setting this parameter.

- **--skip_v:** Indicates whether to skip patch validation.
Do not set it.

- **--re_rank:**: Indicates whether to re-rank patches produced by
the beam search. Set it.

- **--beam_width:** Determines the size of the beam search.
In the paper, it is set to 25.

- **--perfect:** Indicates whether to use perfect fault localization or Ochiai.
Set it.

- **--top_n_patches:** Indicates the number of candidate patches to return.
Set it to -1 to return all patches.
 
For example, to run AlphaRepair on bug Lang-1, use the following
command:

```bash
python experiment.py --bug_id Lang-1 --re_rank --beam_width 1 --perfect --top_n_patches -1
```
