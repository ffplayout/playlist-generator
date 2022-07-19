# playlist-generator

**This generator is not necessery anymore, because the ffplayout engine has now one included.** 

This script loop over ramdomized files in given folder, and generate a playlist from it.


Options:

```
optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        file path to ffplayout.yml
  -d DATE [DATE ...], --date DATE [DATE ...]
                        playlist date (yyyy-mm-dd)
  -t LENGTH, --length LENGTH
                        set length in "hh:mm:ss", default 24:00:00
  -i INPUT, --input INPUT
                        input folder
  -o OUTPUT, --output OUTPUT
                        output folder

```

When no options are set, the script uses the settings from **ffplayout.yml**

**--date** paramter can be a list, or a range: **2021-01-01 - 2021-01-31**

Example command:

```
./generate-playlist.py -d 2021-01-01 - 2021-01-31 -t 24:00:00 -i /opt/tv-media -o /opt/playlists
```
