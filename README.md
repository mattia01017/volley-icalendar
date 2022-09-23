# Volley iCalendar
iCalendar generator for FIPAV volleyball online calendars

## Setup
Python interpreter is required. It's recommended the use of `pip` for the installation of needed modules:

MacOS/Linux:
```shell
python -m pip install -r requirements.txt
```

Windows:
```batch
py -m pip install -r requirements.txt
```

## Usage
```
start.py [-h] [-o [FILE ...]] [-a] [-s] URL [URL ...]

positional arguments:
  URL                   URLs of tournaments

options:
  -h, --help            show this help message and exit
  -o [FILE ...], --output [FILE ...]
                        Name the output files with the given values 
                        ("calendar.ics" by default). If option -s is
                        present, if you use this option you can specify
                        all names or a name for all files
  -a, --all             Include every team of the specified tournaments in the output calendars
  -s, --split           Create a different file for each tournament
```
If `-a` option is not specified, it will be asked which teams to include in output files

## License
The project is under MIT license and it's in no way affiliated with FIPAV