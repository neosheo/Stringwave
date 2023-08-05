from pathlib import Path
import os
import re
from mutagen.oggopus import OggOpus


tracks = os.listdir('/stringwave/radio/new')
tracks.remove('.playlist')
tracks_with_path = [ f'/stringwave/radio/new/{track}' for track in tracks ]
latest_track = Path(max(tracks_with_path, key=os.path.getctime)).stem
print(f'THE LATEST TRACK IS: {latest_track}')


new_filename = re.sub(r'_+', '_', latest_track)
new_filename = re.sub(u'\s{2,}', ' ', new_filename)
new_filename = new_filename.strip()
# to remove no breaking spaces
new_filename = new_filename.replace(u'\xa0', '')
os.rename(f'/stringwave/radio/new/{latest_track}.opus', f'/stringwave/radio/new/{new_filename}.opus')

file = OggOpus(f'/stringwave/radio/new/{new_filename}.opus')
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