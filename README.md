In this repo I will play around with plotting the POES and 
FIREBIRD data during a conjunction.

# Installation
1. Download and install IRBEM on your machine. Go to
``` https://sourceforge.net/p/irbem/code/HEAD/tree/trunk/ ```
and download the code. First you must install the 
fortan IRBEM using commands that are specified in 
README.install. For example, to install on a Linux
machine run

```
make OS=linux64 ENV=gnu64 all
make install
make test
```

2. Now install the Python wrapper. Change into the ```python/```
directory and run
``` sudo python3 setup.py install ```

# Use
I currently only have the code to generate the magnetic ephemeris 
using T89 and it is located in ```make_poes_magephem.py```.

Before you generate the magnetic ephemeris you need to download the
kp index. Simply run ```python python3 downloadKp 2018``` to download
kp for 2018 and save it to a csv file in the ```./data/``` directory.
It will raise an error if the dirctory does not exist. You can also
run ```python python3 downloadKp 2018 -dir KP_PATH``` to specify a 
different path to save the data to. Also you can run 
```python python3 downloadKp -h``` to get help on the command line 
arguments.

Once you have downloaded the kp index you can generate the magnetic
ephemeris. Run make_poes_magephem.py. An example script calls functions
in the ```python if __name__ == '__main__': ''' block. The top-level 
function calls are:

```netCDF4.Dataset() -> convert_time() -> run_irbem() -> save_magephem()```