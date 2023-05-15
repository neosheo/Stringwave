#!/bin/bash

session="icecast"
window=0
tmux new-session -d -s $session
tmux rename-window -t $session:$window "icecast"
tmux send-keys -t $session:$window "icecast2 -c config/icecast.xml" C-m
sleep 5
session="ezstream-new"
tmux new-session -d -s $session
tmux rename-window -t $session:$window "ezstream-new"
tmux send-keys -t $session:$window "cd /stringwave" C-m
tmux send-keys -t $session:$window "/bin/monitor_port &" C-m
tmux send-keys -t $session:$window "./scripts/ezstream.sh new || pkill monitor_port && touch .pid-new" C-m
session="ezstream-main"
tmux new-session -d -s $session
tmux rename-window -t $session:$window "ezstream-main"
tmux send-keys -t $session:$window "cd /stringwave" C-m
tmux send-keys -t $session:$window "/bin/monitor_port &" C-m
tmux send-keys -t $session:$window "./scripts/ezstream.sh main || pkill monitor_port && touch .pid-main" C-m
#session="metadata"
#tmux new-session -d -s $session
#tmux rename-window -t $session:$window "metadata"
#sleep 5 
#tmux send-keys -t $session:$window "cd stringwave/Radio && python stringwave/scripts/get_track_info.py" C-m
