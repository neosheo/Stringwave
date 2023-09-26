import sys
from mutagen.oggopus import OggOpus


def embed_metadata(track):
    # clip off path and extension
    print('Setting metadata...')
    track['title'] = sys.argv[2]
    track['artist'] = sys.argv[3]
    track['config'] = sys.argv[4]
    track['album'] = ''
    track['data'] = ''
    track['language'] = ''
    track['description'] = ''
    track['encoder'] = ''
    track['synopsis'] = ''
    track['compatible_brands'] = ''
    track['creation_time'] = ''
    track['handler_name'] = ''
    track['major_brand'] = ''
    track['minor_version'] = ''
    track.save()
    print('Done!')


if __name__ == '__main__':
    embed_metadata(OggOpus(sys.argv[1]))
