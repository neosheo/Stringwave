import sys
from mutagen.oggopus import OggOpus

file = OggOpus(sys.argv[1])

file['title'] = sys.argv[1].split('/')[3]
file['artist'] = sys.argv[2]
file["config"] = sys.argv[3]
file.save()


