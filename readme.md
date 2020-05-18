## Requirements

Several packages are required to read the csv file, produce images, and handle the command line interface. The easiest way to set up a python enviornment is with conda. An almost minimally sufficient conda environment file is included at `conda_environment.yml`, and a new environment can be generated with the follow command (replacing `MY_NEW_ENVIRONMENT` with the name you want):

```
conda env create -f conda_environment.yml --name MY_NEW_ENVIRONMENT
```

## Usage

The tool is easiest to use from the command line. 
Given a filename at `data.csv`, the simplest use is:
```
python make_thumbnails.py -f data.csv
```
A number of options are available through the command line interface.

## Notes

The font locations assume MacOS defaults and would need to be updated for any other system.

Inspired by the thumbnails used by [Empirical China](https://github.com/empiricalchina).

Code is under the MIT License.
