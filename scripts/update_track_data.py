import sys
from mutagen.oggopus import OggOpus
import os
import re
import traceback
sys.path.append("..")
from webapp import logger  # noqa: E402


def update_track_data(track, artist, video_title):
	# sometimes download script includes debug information in name
	# cut this off it it is included
	if "/stringwave/radio/new/" in track:
		track = track.split("/stringwave/radio/new/")[1].strip()
	else:
		track = track
	print(f"TRACK={track}")
	logger.debug(f"ATTEMPTING TO UPDATE TRACK DATA FOR {track}")
	logger.debug(f"ARTIST IS {artist}")
	logger.debug(f"VIDEO TITLE IS {video_title}")
	try:
		old_filename = f"{track[:-4]}opus"
		if old_filename == "opus":
			logger.error('Received filename of "opus"')
			return old_filename, video_title
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
		if old_filename != "opus" or old_filename != "":
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
			file["config"] = "pf"
			file.save()
			print("Done!")
			logger.debug(f"NEW TRACK ADDED TO DATABASE\nFILE PATH: {new_filename}\nTITLE: {video_title}")
			return new_filename, video_title
	except (OSError, FileNotFoundError):
		return old_filename, video_title
