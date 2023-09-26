from pathlib import Path
import os
import re
from mutagen.oggopus import OggOpus


def update_track_data(track, artist):
    old_filename = f'{track[:-3]}opus'
    print('Changing file name...')
    new_filename = re.sub(r'\s{2,}', ' ', old_filename)
    new_filename = re.sub(r'(^_|_$)', '', new_filename)
    new_filename = new_filename.replace(' ', '_')
    # to remove no breaking spaces
    new_filename = new_filename.replace(u'\xa0', '')
    new_filename = new_filename.strip()
    new_filename = re.sub(r'_+', '_', new_filename)
    os.rename(old_filename, new_filename)
    print('Done!')
    
    print('Updating metadata...')
    file = OggOpus(new_filename)
    title = re.sub(r'_+', ' ', Path(new_filename).stem)
    file['title'] = title
    file['artist'] = artist
    file['album'] = ''
    file['data'] = ''
    file['language'] = ''
    file['description'] = ''
    file['encoder'] = ''
    file['synopsis'] = ''
    file['compatible_brands'] = ''
    file['creation_time'] = ''
    file['handler_name'] = ''
    file['major_brand'] = ''
    file['minor_version'] = ''
    file['config'] = 'pf'
    file.save()
    print('Done!')

    return new_filename, title
