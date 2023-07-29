from pathlib import Path
import os
import re

tracks = os.listdir('/stringwave/radio/new')
for track in tracks:
	if track == '.playlist':
		del track
		continue
tracks_with_path = [ f'/stringwave/radio/new/{track}' for track in tracks ]
latest_track = Path(max(tracks_with_path, key=os.path.getctime)).stem

new_filename = re.sub(r'_+', '_', latest_track)
new_filename = re.sub(u'\s{2,}', ' ', latest_track)
new_filename = new_filename.replace(u'\xa0', '')
os.rename(f'/stringwave/radio/new/{latest_track}.opus', f'/stringwave/radio/new/{new_filename}.opus')

