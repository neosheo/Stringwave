import os
import sys

station = sys.argv[1]

def remove_white_spaces_in_track_filenames():
	for old_file_name in os.listdir():
		new_file_name = old_file_name.replace(' ', '_').replace('\n', '_').replace('\t', '_')
		os.rename(old_file_name, new_file_name)

if __name__ == '__main__':
	os.chdir(f'/stringwave/radio/{station}')
	remove_white_spaces_in_track_filenames()
