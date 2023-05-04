import os
import sys

station = sys.argv[1]

radio_path = f'/stringwave/radio/{station}'

def remove_white_spaces_in_track_filenames():
	for old_file_name in os.listdir():
		new_file_name = old_file_name.replace(' ', '_')
		os.rename(old_file_name, new_file_name)

if __name__ == '__main__':
	os.chdir(radio_path)
	remove_white_spaces_in_track_filenames()
