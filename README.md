# vinebatch
batch-downloader tool for widevine

---
This script is for automating the ripping process of protected streams. It's like widevine-dl (https://github.com/WHTJEON/widevine-dl) but the use case is a generic batch downloader.

This tool only works on windows and is NOT for getting widevine keys. Don't bother asking.

If you have to ask what this tool is for, it's probably not for you. NOT for total noobs.

---
Requirements:
- latest python https://www.python.org/downloads/
- latest yt-dlp https://github.com/yt-dlp/yt-dlp/releases
- aria2c https://github.com/aria2/aria2/releases
- mp4decrypt and mp4info https://www.bento4.com/downloads/
- shaka-packager https://github.com/shaka-project/shaka-packager/releases (rename to shaka-packager.exe after downloading)
- latest mkvmerge https://www.fosshub.com/MKVToolNix.html
- latest ffmpeg https://www.gyan.dev/ffmpeg/builds/
---
Instructions:
- Edit the script to put the path of .exe for yt-dlp, aria2c, mp4decrypt, mp4info, mkvmerge, ffmpeg, shaka-packager. Make sure that the actual script is located in a path with no spaces (e.g. D:\vinebatch\vinebatch.py). When editing the script, use double slash (e.g. D:\\ffmpeg\\ffmpeg.exe)
- Run from cmd or terminal (wt)
```
usage: vinebatch.py [-h] -of  [-vr] [-ch] [-ar] [-kf] [-sl] [-md] [-s]

vinebatch v0.4.3 - r3n@RSG generic batch widevine ripper

options:
  -h, --help           show this help message and exit
  -of , --openfile     file to open, put file extension
  -vr , --resolution   resolution to get. 1080p, 720p, 480p, sd, worst - default: best video
  -ch , --check        add 'y' to check file after mux. default: not checking
  -ar , --aria         add 'n' to disable aria2c. default: use aria2c
  -kf , --keepfile     add 'y' to keep raw encrypted+decrypted files
  -sl , --sleep        add 'y' to sleep windows when done. default: no sleep
  -md , --usemp4d      add 'y' to use mp4decrypt. default: use shaka-packager
  -s , --subtitle      add 'y' to mux srt subs
```

Sample: py vinebatch.py -of tvserie.txt -vr 720p -ch y

The text file to be opened is named tvserie.txt and the resolution to fetch is 720p. Checking via ffmpeg after download is enabled. The format for every line on text file is:
```
video_1;MPD_LINK;KID:KEY
video_2;MPD_LINK;KID:KEY
video_3;MPD_LINK;KID:KEY
````
If you have multiple keys, you need to put a '+' after each set of KID:KEY. Sample format:
```
video_1;MPD_LINK;KID1:KEY1+KID2:KEY2+KID3:KEY3+KID4:KEY4
video_2;MPD_LINK;KID1:KEY1+KID2:KEY2+KID3:KEY3+KID4:KEY4
```
This script is not smart (it has only few exception handling.. if you can call it like that).

----
Additional notes:
- Temp files will downloaded to 'temp' and will be decrypted there. 'decrypted_mkv' is the final output folder. If needed folder doesn't exist yet, script will create them for you.
- Decryption by default will be done via shaka-packager. You can still use mp4decrypt if you prefer to or if you encounter issues with shaka-packager.
- Make sure that your temp folder is always empty after you kept encrypted+decrypted raws (move them somewhere else idk).
- Multiple pair of KID:KEY now supported. Please follow new formatting for the file to be fed to script. We assume you know what you're doing and not feeding the script with fake KID:keys. You will get a corrupted file output anyway and the script will crash.
- Added Checking KID of files before decrypting (only for shaka-packager), you usually don't need that on mp4decrypt.
- Added muxing of single subtitle file that should have the same name as the final file name. (i.e. if you set 'bunnydownload' as filename on the text file to open, you will need to put the 'bunnydownload.srt' on subs folder.
- Output file should NOT have spaces in file name.
---
This is a public release. Any future updates/improvements may or may not be available publicly.

USE AT YOUR OWN RISK.
