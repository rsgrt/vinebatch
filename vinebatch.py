import os
import sys
import shutil
import argparse
import lang_list
import subprocess


class color:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

#parser
parser = argparse.ArgumentParser(description='vine-batch v0.4.4 - r3n@RSG generic batch widevine ripper')
parser.add_argument('-of','--openfile', type=str.lower, metavar='', required=True, help="file to open, put file extension")
parser.add_argument('-vr','--resolution', metavar='', help="resolution to get. 1080p, 720p, 480p, sd, worst - default: best video")
parser.add_argument('-ch','--check', type=str.lower, metavar='', help="add 'y' to check file after mux. default: not checking")
parser.add_argument('-ar','--aria', type=str.lower, metavar='', help="add 'n' to disable aria2c. default: use aria2c")
parser.add_argument('-kf','--keepfile', type=str.lower, metavar='', help="add 'y' to keep raw encrypted+decrypted files")
parser.add_argument('-sl','--sleep', type=str.lower, metavar='', help="add 'y' to sleep windows when done. default: no sleep")
parser.add_argument('-md','--usemp4d', type=str.lower, metavar= '', help="add 'y' to use mp4decrypt. default: use shaka-packager")
parser.add_argument('-s','--subtitle', type=str.lower, metavar='', help="add 'y' to mux srt subs")

args = parser.parse_args()
source = args.openfile
reso = args.resolution
sleep = args.sleep
chk = args.check
aria = args.aria
subs = args.subtitle
keep = args.keepfile
use_mp4decrypt = args.usemp4d

cd = os.getcwd()

#intro screen
                                                                                                    
print('''
                ███                      █████                █████             █████     
     r3n@RSG   ░░░                      ░░███       v0.4.4   ░░███             ░░███      
   █████ █████ ████  ████████    ██████  ░███████   ██████   ███████    ██████  ░███████  
  ░░███ ░░███ ░░███ ░░███░░███  ███░░███ ░███░░███ ░░░░░███ ░░░███░    ███░░███ ░███░░███ 
   ░███  ░███  ░███  ░███ ░███ ░███████  ░███ ░███  ███████   ░███    ░███ ░░░  ░███ ░███ 
   ░░███ ███   ░███  ░███ ░███ ░███░░░   ░███ ░███ ███░░███   ░███ ███░███  ███ ░███ ░███ 
    ░░█████    █████ ████ █████░░██████  ████████ ░░████████  ░░█████ ░░██████  ████ █████
     ░░░░░    ░░░░░ ░░░░ ░░░░░  ░░░░░░  ░░░░░░░░   ░░░░░░░░    ░░░░░   ░░░░░░  ░░░░ ░░░░░ 
                        BATCH DOWNLOAD-DECRYPT-MUX PROTECTED STREAMS\n                                                                      
''')

if not os.path.exists(f'{cd}\\binaries'):
    sys.exit(f"\n>binaries folder doesn't exist. exiting.")

#temp/out folder check
TEMP_PATH = 'temp'
OUT_PATH = 'decrypted_mkv'
if not os.path.exists(TEMP_PATH) and not os.path.exists(OUT_PATH):
    os.makedirs(TEMP_PATH)
    os.makedirs(OUT_PATH)
    print('\n>needed folder does not exist yet!\n created temp and decrypted_mkv folder.')
elif os.path.exists(TEMP_PATH) and not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)
    print('\n>temp folder already exists!\n created decrypted_mkv folder.')
elif not os.path.exists(TEMP_PATH) and os.path.exists(OUT_PATH):
    os.makedirs(TEMP_PATH)
    print('\n>decrypted_mkv folder already exists!\n created temp folder.')
else:
    print('\n>temp and decrypted_mkv folder already exists!')

#subtitle folder check
SUB_PATH = 'subs'
RAWS_PATH = 'raws'
if not os.path.exists(SUB_PATH) and not os.path.exists(RAWS_PATH):
    os.makedirs(RAWS_PATH)
    os.makedirs(SUB_PATH)
    print('>subs and raws folder created.')
elif os.path.exists(SUB_PATH) and not os.path.exists(RAWS_PATH):
    os.makedirs(RAWS_PATH)
    print('\n>subs folder already exists!\n created raws folder.')
elif not os.path.exists(SUB_PATH) and os.path.exists(RAWS_PATH):
    os.makedirs(SUB_PATH)
    print('\n>raws folder already exists!\n created subs folder.')
else:
    print('>subs and raws folder already exists!')
    
source_file = open(f"{source}", "r", encoding='latin-1')

#file paths
ytdlp = f'{cd}\\binaries\\yt-dlp.exe'
aria2c = f'{cd}\\binaries\\aria2c.exe'
mp4decrypt = f'{cd}\\binaries\\mp4decrypt.exe'
mkvmerge = f'{cd}\\binaries\\mkvmerge.exe'
ffmpeg = f'{cd}\\binaries\\ffmpeg.exe'
shaka_packager = f'{cd}\\binaries\\shaka-packager.exe'
mp4info = f'{cd}\\binaries\\mp4info.exe'

#reso check from args
if reso == None:
    reso_code = '-f bv+ba'
    print('Script will download the best resolution from server based on MPD.')
elif reso == '1080p':
    reso_code = '-f bv[height=1080]+ba'
    print('1080p resolution chosen.')
elif reso == '720p':
    reso_code = '-f bv[height=720]+ba'
    print('720p resolution chosen.')
elif reso == '480p':
    reso_code = '-f bv[height=480]+ba'
    print('480p resolution chosen.')
elif reso == 'sd':
    reso_code = '-S "height:480"'
    print('SD (less than 480p) resolution chosen.')
elif reso == 'worst':
    reso_code = '-S "+size,+br,+res,+fps"'
    print('Worst quality selected.')

# keeping this else clause in comment for now    
#else:
#    print("Quality chosen not on list of accepted input.\nAccepted options: 1080p, 720p, 480p, sd, worst.\n"
#          "There's also option to download specific IDs. Format ID_one+ID_two")

#functions define
def rename():
    # logic check temp folder if decrypted file name exists (not adding this anytime soon). check KID of files then go to decrypt if encrypted only
    print(f'{color.OKGREEN}Renaming files..{color.ENDC}')
    for filename in os.listdir(TEMP_PATH):
        if filename.endswith(".mp4"):
            if os.path.exists(f'{TEMP_PATH}\\{name}_encrypted_video.mp4'):
                print('Encrypted VIDEO already exists.')
            else:
                os.rename(f'{TEMP_PATH}\\{filename}', f'{TEMP_PATH}\\{name}_encrypted_video.mp4')

        if filename.endswith(".m4a"):
            if os.path.exists(f'{TEMP_PATH}\\{name}_encrypted_audio.m4a'):
                print('Encrypted AUDIO already exists.')
            else:
                os.rename(f'{TEMP_PATH}\\{filename}', f'{TEMP_PATH}\\{name}_encrypted_audio.m4a')


def mp4decrypt_video():
    subprocess.call(f'{mp4decrypt} {sep.join(mp4decrypt_keys_list)}{sep}{cd}\\{TEMP_PATH}\\{name}_encrypted_video.mp4 {cd}\\{TEMP_PATH}\\{name}_decrypted_video.mp4')

def mp4decrypt_audio():
    subprocess.call(f'{mp4decrypt} {sep.join(mp4decrypt_keys_list)}{sep}{cd}\\{TEMP_PATH}\\{name}_encrypted_audio.m4a {cd}\\{TEMP_PATH}\\{name}_decrypted_audio.m4a')

def decrypt():
    if os.path.exists(f'{cd}\\{TEMP_PATH}\\{name}_encrypted_video.mp4') and os.path.exists(f'{cd}\\{TEMP_PATH}\\{name}_encrypted_audio.m4a'):
        
        # LOGIC CHECK BEFORE DOWNLOADING SHOULD BE ADDED LIKE THIS
        if os.path.exists(f'{cd}\\{TEMP_PATH}\\{name}_decrypted_video.mp4') and os.path.exists(f'{cd}\\{TEMP_PATH}\\{name}_decrypted_audio.m4a'):
            print(f'{color.WARN}Decrypted video and audio already exists. Skipping decryption.{color.ENDC}')
        else:
            if use_mp4decrypt == 'y':
                print(f'{color.WARN}Decrypting files using mp4decrypt (may take some time)..{color.ENDC}')
                mp4decrypt_video()
                mp4decrypt_audio()
            else:
                print(f'{color.OKGREEN}Decrypting files via shaka-packager (may take some time)..\nIgnore warnings/messages if final file passes ffmpeg check.{color.ENDC}')

                kid_list = []
                key_list = []

                for shaka in multi_keys_split:
                    kid_list.append(shaka.split(":")[0])
                    key_list.append(shaka.split(":")[1])

                multi_keys_dict = dict(zip(kid_list, key_list))

                os.system(f'{mp4info} --verbose --fast {cd}\\{TEMP_PATH}\\{name}_encrypted_video.mp4 > {cd}\\{TEMP_PATH}\\{name}_encrypted_video.mp4.dmp')
                os.system(f'{mp4info} --verbose --fast {cd}\\{TEMP_PATH}\\{name}_encrypted_audio.m4a > {cd}\\{TEMP_PATH}\\{name}_encrypted_audio.m4a.dmp')

                with open(f'{cd}\\{TEMP_PATH}\\{name}_encrypted_video.mp4.dmp', 'r') as dmp_video:
                    for dmp_line_video in dmp_video:
                        if 'default_KID' in dmp_line_video:
                            extracted_kid_video = dmp_line_video.replace(' ', '').replace('[', '').replace(']', '').replace('default_KID=', '').strip()
                            print(f'{color.OKCYAN}Extracted video KID: {extracted_kid_video}{color.ENDC}')

                            if extracted_kid_video in multi_keys_dict:
                                subprocess.call(f'{shaka_packager} --quiet in={cd}\\{TEMP_PATH}\\{name}_encrypted_video.mp4,stream=video,output={cd}\\{TEMP_PATH}\\{name}_decrypted_video.mp4 -enable_raw_key_decryption -keys key={multi_keys_dict[extracted_kid_video]}:key_id={extracted_kid_video} --temp_dir {cd}\\temp')
                            else:
                                print(f'{color.FAIL}Either wrong keys or non-matching KID for {name} VIDEO.\nTrying mp4decrypt fallback for video.{color.ENDC}')
                                mp4decrypt_video()
                        else:
                            extracted_kid_video = None
                dmp_video.close()

                if extracted_kid_video == None and os.path.exists(f'{TEMP_PATH}\\{name}_encrypted_video.mp4') and not os.path.exists(f'{TEMP_PATH}\\{name}_decrypted_video.mp4'):
                    os.rename(f'{TEMP_PATH}\\{name}_encrypted_video.mp4', f'{TEMP_PATH}\\{name}_decrypted_video.mp4')
                    print(f'{color.WARN}Looks like {name} VIDEO is not encrypted.{color.ENDC}')

                with open(f'{cd}\\{TEMP_PATH}\\{name}_encrypted_audio.m4a.dmp', 'r') as dmp_audio:
                    for dmp_line_audio in dmp_audio:
                        if 'default_KID' in dmp_line_audio:
                            extracted_kid_audio = dmp_line_audio.replace(' ', '').replace('[', '').replace(']', '').replace('default_KID=', '').strip()
                            print(f'{color.OKCYAN}Extracted audio KID: {extracted_kid_audio}{color.ENDC}')  

                            if extracted_kid_audio in multi_keys_dict:
                                subprocess.call(f'{shaka_packager} --quiet in={cd}\\{TEMP_PATH}\\{name}_encrypted_audio.m4a,stream=audio,output={cd}\\{TEMP_PATH}\\{name}_decrypted_audio.m4a -enable_raw_key_decryption -keys key={multi_keys_dict[extracted_kid_audio]}:key_id={extracted_kid_audio} --temp_dir {cd}\\temp')
                            else:
                                print(f'{color.FAIL}Either wrong keys or non-matching KID for {name} AUDIO.\nTrying mp4decrypt fallback for audio.{color.ENDC}')  
                                mp4decrypt_audio()
                        else:
                            extracted_kid_audio = None
                dmp_audio.close()

                if extracted_kid_audio == None and os.path.exists(f'{TEMP_PATH}\\{name}_encrypted_audio.m4a') and not os.path.exists(f'{TEMP_PATH}\\{name}_decrypted_audio.m4a'):
                    os.rename(f'{TEMP_PATH}\\{name}_encrypted_audio.m4a', f'{TEMP_PATH}\\{name}_decrypted_audio.m4a')
                    print(f'{color.WARN}Looks like {name} AUDIO is not encrypted.{color.ENDC}')


                os.remove(f'{cd}\\{TEMP_PATH}\\{name}_encrypted_video.mp4.dmp')
                os.remove(f'{cd}\\{TEMP_PATH}\\{name}_encrypted_audio.m4a.dmp')

    else:
        print(f'\n{color.WARN}No video and audio downloaded. Script will move to the next video (if there is any).{color.ENDC}\n')
        # possibly put this outside this block of code (?)


def mux():
    mux_prep = []
    sub_count = []
    sub_ext_list = ['ass', 'srt', 'vtt', 'ssa']
    sub_dir = os.listdir(f'{cd}\\{SUB_PATH}')


    if subs == 'y' and os.path.exists(f'{cd}\\{SUB_PATH}'):
        print(f'{color.OKGREEN}Muxing decrypted files with subs..{color.ENDC}')

        for lang in lang_list.mkvtoolnix_languages:

            audio_lang = name.split('.')[-1]
            if audio_lang in lang.lower().split('|')[1:]:
                mux_prep.insert(0, f"--language 0:{audio_lang} --track-name 0:{lang.split('|')[0]} ( {cd}\\{TEMP_PATH}\\{name}_decrypted_audio.m4a ) ")

            for sub in sub_dir:
                if sub.split('.')[-1] in sub_ext_list and name.split('.')[0] in sub.strip().split('.') and sub.split('.')[-2] in lang.lower().split('|')[1:]:
                    sub_count.append(sub)
                    mux_prep.append(f"--language 0:{sub.lower().split('.')[-2]} --track-name 0:{lang.split('|')[0]} ( {cd}\subs\{sub} ) ")
        
        track_order = [f'{item}:0,' for item in range(0, len(sub_count)+2)]
        os.system(f'''{mkvmerge} --quiet --ui-language en --output {cd}\\{OUT_PATH}\\{name}_mux_.mkv --language 0:und ( {cd}\\{TEMP_PATH}\\{name}_decrypted_video.mp4 ) {"".join(mux_prep)} --track-order {"".join(track_order).rstrip(',')}''')                    
    
    else:
        print(f"{color.WARN}No subtitle or '--subtitle y' not set. Muxing as normal.")
        os.system(f'{mkvmerge} --quiet --ui-language en --output {cd}\\{OUT_PATH}\\{name}_mux_.mkv --language 0:und ( {cd}\\{TEMP_PATH}\\{name}_decrypted_video.mp4 ) --language 0:und ( {cd}\\{TEMP_PATH}\\{name}_decrypted_audio.m4a ) --track-order 0:0,1:0')


def delete_temp():
    if keep == 'y':
        print(f'{color.OKGREEN}Keeping encrypted+decrypted raws.{color.ENDC}')
        shutil.move(f'{cd}\\temp\\{name}_encrypted_video.mp4', f'{cd}\\raws\\{name}_encrypted_video.mp4')
        shutil.move(f'{cd}\\temp\\{name}_encrypted_audio.m4a', f'{cd}\\raws\\{name}_encrypted_audio.m4a')
        shutil.move(f'{cd}\\temp\\{name}_decrypted_video.mp4', f'{cd}\\raws\\{name}_decrypted_video.mp4')
        shutil.move(f'{cd}\\temp\\{name}_decrypted_audio.m4a', f'{cd}\\raws\\{name}_decrypted_audio.m4a')
    else:
        files_in_directory = os.listdir(f'{cd}\\{TEMP_PATH}')
        filtered_files = [file for file in files_in_directory if file.endswith(".mp4") or file.endswith(".m4a")]
        print(f'{color.WARN}Deleting encrypted+decrypted raws.{color.ENDC}')
        for file in filtered_files:
            path_to_file = os.path.join(f'{cd}\\{TEMP_PATH}', file)
            os.remove(path_to_file)

def ffmpeg_check():
    if chk == 'y':
        print(f'{color.OKGREEN}Checking the final mux file via ffmpeg.{color.ENDC}')

        if os.path.exists(f'{cd}\\{OUT_PATH}\\{name}_mux_.mkv'):

            os.system(f'{ffmpeg} -v error -i {OUT_PATH}\\{name}_mux_.mkv -f null - 2>{OUT_PATH}\\{name}_mux_.mkv.log')

            size = os.path.getsize(f'{cd}\\{OUT_PATH}\\{name}_mux_.mkv.log')

            if size == 0:
                print(f'{color.OKGREEN}Found no error in muxed MKV.{color.ENDC}')
                os.remove(f'{cd}\\{OUT_PATH}\\{name}_mux_.mkv.log')
            else:
                print(f'{color.WARN}Possible error in muxed MKV. Check the .log file and re-rip.{color.ENDC}')
                os.remove(f'{cd}\\{OUT_PATH}\\{name}_mux_.mkv')

                print(f'{color.WARN}Adding failed entry to {source}_redownload.txt{color.ENDC}')
                redownload = open(f"{source}_redownload.txt", "w", encoding='utf-8')
                print(line, file=redownload)
                redownload.close()
        else:
            print(f"{color.WARN}Looks like final mux file doesn't exist. Skipping checking.")
    else:
        print(f'{color.WARN}Not checking the final mux file.{color.ENDC}')

# actual script starts running here
for line in source_file:
    fields = line.split(";")
    name = fields[0]
    mpd_retrieve = fields[1]
    key_pair = fields[2]

    multi_keys_list = []
    multi_keys_split = key_pair.split("+")

    #mp4decrypt keys preparation
    mp4decrypt_keys_list = []
    for key in multi_keys_split:
        mp4decrypt_keys_list.append(f'--key {key}')
    sep = ' '

    reso_list = ['1080p', '720p', '480p', 'sd', 'worst']

    #check if file name is already on output folder
    if os.path.exists(f'{cd}\\{OUT_PATH}\\{name}_mux_.mkv'):
        print(f'{color.WARN}Looks like {name} was already ripped.\nSkipping for now, please check decrypted_mkv folder.{color.ENDC}')
    else:
        print(f'{color.OKCYAN}\n{name} is OK for download.{color.ENDC}')

        if reso != None and reso not in reso_list and '+' in reso:
            print("Downloading custom IDs from link.")
            os.system(f'{ytdlp} -o "{TEMP_PATH}/{name}_encrypted_.%(ext)s" --no-warnings --external-downloader {aria2c} --allow-u --no-check-certificate -f {reso} "{mpd_retrieve}"')
            rename()
            decrypt()
            mux()
            delete_temp()
            ffmpeg_check()
        elif reso != None and reso not in reso_list or reso == 'F':
            print(f'\n{color.FAIL}Quality chosen for {name} not on list of acceptable input for download.{color.ENDC}\nRequesting available options on the server:\n')
            os.system(f'{ytdlp} --no-warnings --allow-unplayable-formats --no-check-certificate -F {mpd_retrieve}')
        elif aria == 'n':
            print(f'{color.OKGREEN}Downloading without aria2c.{color.ENDC}')
            os.system(f'{ytdlp} -o "{TEMP_PATH}/{name}_encrypted_.%(ext)s" --no-warnings --allow-u --no-check-certificate {reso_code} "{mpd_retrieve}"')
            rename()
            decrypt()
            mux()
            delete_temp()
            ffmpeg_check()
        elif aria != None and aria != 'no':
            print(f"{color.FAIL}Please put '-ar no' if you don't want to use aria2c.{color.ENDC}")
        else:
            print(f'{color.OKGREEN}Downloading {name}..{color.ENDC}')
            os.system(f'{ytdlp} -o "{TEMP_PATH}/{name}_encrypted_.%(ext)s" --no-warnings --external-downloader {aria2c} --allow-u --no-check-certificate {reso_code} "{mpd_retrieve}"')
            rename()
            decrypt()
            mux()
            delete_temp()
            ffmpeg_check()


if sleep == 'y':
    print(f'{color.FAIL}Press any key if you want to cancel sleep!{color.ENDC}\n')
    os.system("timeout /t 30")


#add export report on files not downloaded or log of the whole cmd window
