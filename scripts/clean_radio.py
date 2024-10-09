import os
import sys
import shutil
import re

# make sure the webapp is accessible before importing
sw_in_path = False
for dir in sys.path:
    if dir == "/stringwave":
        sw_in_path = True
if not sw_in_path:
    sys.path.append("/stringwave")
from webapp import sw_logger as logger

def clean_track(station: str, file_name: str):
    radio_path = f"/stringwave/radio/{station}/"
    #for file in os.listdir(radio_path):
    safe_file = delete_broken_file(file_name, radio_path)
    if safe_file is None:
        return
    logger.debug(f"{file_name} IS NOT A BROKEN FILE")
    new_file_name = clean_file_name(safe_file, radio_path)
    logger.debug(f"NEW_FILENAME: {new_file_name}")
    return new_file_name

# deletes files that will break the radio
# returns a safe file names
def delete_broken_file(file_name: str, radio_path: str):
    # don't try to add hidden files
    regex = r'^\.[^\.].+'
    if re.match(regex, file_name):
        return

    # sometimes downloads fail and create a directory with a file inside, this cleans them up
    file_path = f"{radio_path}/{file_name}"
    if os.path.isdir(file_path):
        logger.debug(f"FOUND BROKEN FILE: {file_name}")
        shutil.rmtree(file_path)
        return

    # delete broken files that cause segmentation fault in ezstream
    # and duplicate values in database
    regex = r'.+(?<!\.temp)\.opus$'
    if not re.match(regex, file_name):
        logger.debug(f"FOUND BROKEN FILE: {file_name}")
        os.remove(file_path)
        return

    return file_name


# cleans up a file's file name
# returns new name
def clean_file_name(file_name: str, radio_path: str):
    # remove non-breaking spaces from file names
    if u"\xa0" in file_name:
        new_name = file_name.replace(u"\xa0", "")
        logger.debug(f"FOUND NON-BREAKING SPACE IN: {file_name}")
        os.rename(f"{radio_path}/{file_name}", f"{radio_path}/{new_name}")
        return new_name
    return file_name


# running clean_radio.py from a shell or subprocess just
# deletes broken files
if __name__ == "__main__":
    station = sys.argv[1]
    radio_path = f"/stringwave/radio/{station}"
    for file_name in os.listdir(radio_path):
        delete_broken_file(file_name, radio_path)
