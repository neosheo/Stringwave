import sys
from mutagen.oggopus import OggOpus
import os
import re

sys.path.append("..")
from webapp import pf_logger as logger  # noqa: E402


def update_track_data(track, artist, video_title):
    # sometimes download script includes debug information in name
    # cut this off it it is included
    logger.debug(f"This the path before clipping {track}")
    new_radio_path = "/stringwave/radio/new/"
    if new_radio_path in track:
        # sometimes download information is included in stdout which is passed as the file path
        # if you split the file path by the new_radio_path you will get the actual title
        # you will cut off the download information, then add the path back
        track = f"{new_radio_path}{track.split(new_radio_path)[1].strip()}"
    else:
        track = track
    logger.debug(f"Attempting to update track data for {track}")
    logger.debug(f"Artist is {artist}")
    logger.debug(f"Video title is {video_title}")
    try:
        old_filename = f"{track[:-4]}opus"
        if old_filename == "opus":
            logger.error('Received filename of "opus"')
            return new_radio_path + old_filename, video_title
        logger.info("Changing file name...")
        # replace multiple whitespaces in a row with one space
        new_filename = re.sub(r"\s{2,}", " ", old_filename)
        # remove leading and trailing underscores
        new_filename = re.sub(r"(^_|_$)", "", new_filename)
        # swap spaces for underscores
        new_filename = new_filename.replace(" ", "_")
        # to remove no breaking spaces
        new_filename = new_filename.replace("\xa0", "")
        new_filename = new_filename.strip()
        # replace multiple underscores in a row with one underscore
        new_filename = re.sub(r"_+", "_", new_filename)
        logger.debug(f"Checking filename of {new_filename}")
        if old_filename != "" or old_filename != "opus":
            logger.debug("Filename check passed!")
            os.rename(old_filename, new_filename)
            logger.info("Done!")
            logger.info("Updating metadata...")
            file = OggOpus(new_filename)
            file["title"] = video_title
            file["artist"] = artist
            file["config"] = 0
            file["album"] = ""
            file["data"] = ""
            file["language"] = ""
            file["description"] = ""
            file["encoder"] = ""
            file["synopsis"] = ""
            file["compatible_brands"] = ""
            file["creation_time"] = ""
            file["handler_name"] = ""
            file["major_brand"] = ""
            file["minor_version"] = ""
            file.save()
            logger.info("Done!")
            logger.debug(
                f"New track added to database\nfile path: {new_filename}\nTitle: {video_title}"
            )
            # in order to filter out possible debug info in filename we had to clip out the radio path
            # if this is the case add it back
            if new_radio_path not in new_filename:
                logger.debug(f"Adding radio path to file {new_filename}")
                new_filename = new_radio_path + new_filename
                logger.debug(f"Updated path is {new_filename}")
            return new_filename, video_title
    except (OSError, FileNotFoundError) as e:
        logger.error(f"An error occurred when updating metadata: {e}")
        return new_radio_path + old_filename, video_title
