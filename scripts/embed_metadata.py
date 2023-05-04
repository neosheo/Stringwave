import sys
from mutagen.oggopus import OggOpus

file = OggOpus(sys.argv[1])
config_id = sys.argv[2]

file["CONFIG"] = config_id
file.save()


