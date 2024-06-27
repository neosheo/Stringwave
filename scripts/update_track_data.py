import sys
from mutagen.oggopus import OggOpus
import os
import re
sys.path.append("..")
from webapp import pf_logger as logger  # noqa: E402


def update_track_data(track, artist, video_title):
	# sometimes download script includes debug information in name
	# cut this off it it is included
	print(f"THIS THE PATH BEFORE CLIPPING {track}")
	new_radio_path = "/stringwave/radio/new/"
	if new_radio_path in track:
        # sometimes download information is included in stdout which is passed as the file path
        # if you split the file path by the new_radio_path you will get the actual title
        # you will cut off the download information, then add the path back
		track = f"{new_radio_path}{track.split(new_radio_path)[1].strip()}"
	else:
		track = track
	logger.debug(f"ATTEMPTING TO UPDATE TRACK DATA FOR {track}")
	logger.debug(f"ARTIST IS {artist}")
	logger.debug(f"VIDEO TITLE IS {video_title}")
	try:
		old_filename = f"{track[:-4]}opus"
		if old_filename == "opus":
			logger.error('Received filename of "opus"')
			return new_radio_path + old_filename, video_title
		print("Changing file name...")
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
		logger.debug(f"CHECKING FILENAME OF {new_filename}")
		if old_filename != "" or old_filename != "opus":
			logger.debug("FILENAME CHECK PASSED!")
			os.rename(old_filename, new_filename)
			print("Done!")
			print("Updating metadata...")
			file = OggOpus(new_filename)
			file["title"] = video_title
			file["artist"] = artist
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
			# file["config"] = "pf"
			file.save()
			print("Done!")
			logger.debug(f"NEW TRACK ADDED TO DATABASE\nFILE PATH: {new_filename}\nTITLE: {video_title}")
			# in order to filter out possible debug info in filename we had to clip out the radio path
			# if this is the case add it back
			if new_radio_path not in new_filename:
				logger.debug(f"ADDING RADIO PATH TO FILE {new_filename}")
				new_filename = new_radio_path + new_filename
				logger.debug(f"UPDATED PATH IS {new_filename}")
			return new_filename, video_title
	except (OSError, FileNotFoundError) as e:
		logger.error(f"AN ERROR OCCURRED WHEN UPDATING METADATA: {e}")
		return new_radio_path + old_filename, video_title
