import os
import sys
import shutil
import re


def clean_radio(station):
    radio_path ="/stringwave/radio"
    for file in os.listdir(f'{radio_path}/{station}'):
        # sometimes downloads fail and create a directory with a file inside, this cleans them up
        if os.path.isdir(f'{radio_path}/{station}/{file}'):
            shutil.rmtree(f'{radio_path}/{station}/{file}')
            continue
        # delete files that cause segmentation fault in ezstream and duplicate values in database
        regex = r'.+(?<!\.temp)\.opus$'
        if not re.match(regex, file):
            os.remove(f'{radio_path}/{station}/{file}')
            continue    
        # remove non-breaking spaces from file names
        if u'\xa0' in file:
            new_name = file.replace(u'\xa0', '')
            os.rename(f'{radio_path}/{station}/{file}', f'{os.getcwd()}/radio/{station}/{new_name}')


if __name__ == "__main__":
    station = sys.argv[1]
    clean_radio(station)
