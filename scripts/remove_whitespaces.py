import os

def remove_white_spaces_in_track_filenames():
    for old_file_name in os.listdir():
        new_file_name = old_file_name.replace(' ', '_')
        os.rename(old_file_name, new_file_name)

if __name__ == '__main__':
	remove_white_spaces_in_track_filenames()
