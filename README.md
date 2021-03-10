# txt to nc

## _A land-sea mask converter_

This repository hosts a very simple txt to netcdf converter aimed at transforming land-sea masks to netcdf.
A set of example input files are provided.

## Usage

The script can be invoked with:

```
python txt_to_nc.py --input=inputFile.txt --output=outputFile.nc --mapping=mapping.txt
```

where:
* `input` is the input file to convert (every line is lat,lon,depthLevel)
* `output` is the name of the output file
* `mapping` is the name of the mapping file where every line is composed by the number of the level and the correspondent depth in meters.

## Future work

Exception handling needs to be done. 

## About

For every information contact fabio<dot>viola<at>cmcc<dot>it.