import sys
from mutagen.oggopus import OggOpus

file = OggOpus(sys.argv[1])

# clip off path and extension
file['title'] = sys.argv[1].split('/')[3][:-5]
file['artist'] = sys.argv[2]
file['config'] = sys.argv[3]
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
file.save()


