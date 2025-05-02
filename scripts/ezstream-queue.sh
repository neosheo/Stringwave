#!/usr/bin/env bash

# argument one is the station
# argument two is either 0 or 1 for play now
# all subsequent arguments are file names to be queued
station=$1
play_now=$2
ezstream_pid="$(cat /stringwave/.pid-$station)"
playlist="/stringwave/radio/$station/.playlist"
queued_tracks=("${@:3}")

# clear playlist
> $playlist

# when ezstream rereads the playlist it will not start from the beginning
# if the currently playing song is in the playlist
# check the currently playing song and put it first on the queue
# so ezstream will play the queued song after it

# ONLY ISSUE THAT COULD EXIST IS IF THE TRACK ENDS BETWEEN WHEN IT IS EXTRACTED
# AND WHEN THE REREAD IS SENT
# THIS WOULD BE A VERY RARE OCCURRENCE BUT MAY BE ABLE TO BE 
# AVOIDED BY CHECKING THE TMUX OUTPUT FOR THE TRACK'S TIME INFO
# DETERMINING HOW MUCH IS LONGER IN THE SONG AND IF IT IS UNDER 1 SECOND
# SLEEPING FOR 1 SECOND THEN WRITING THE PLAYLIST 
currently_playing_file="$(python /stringwave/scripts/return_now_playing_file_path.py $station)"
echo "$currently_playing_file" >> $playlist

# write tracks passed to script as first tracks in the playlist
for track in "${queued_tracks[@]}"
do
    echo "./$track" >> $playlist
done

# add the rest of the tracks to the playlist in a shuffled order
find radio/$station -name "*.opus" | grep -vF -f <(printf "%s\n" "${queued_tracks[@]}") | shuf | sed "s|radio/$station|.|g" >> $playlist

# reread playlist
kill -SIGHUP $ezstream_pid

# needed or else the skip next will not read the new playlist
sleep 1

# skip to first track in queue if play_now is set to true
if [ "$play_now" = "1" ] ; then
    kill -SIGUSR1 $ezstream_pid
    # kill -SIGUSR1 $ezstream_pid
fi
