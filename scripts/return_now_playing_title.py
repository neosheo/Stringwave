from grab_now_playing import grab_now_playing
import sys

def return_now_playing_title(station):
    now_playing = grab_now_playing(station, False)
    title = now_playing.split(" - ")[1]
    return title

if __name__ == "__main__":
    station = sys.argv[1]
    currently_playing_title = return_now_playing_title(station)
    print(currently_playing_title)
