#!/bin/bash

session="radio"
window=0
tmux new-session -d -s $session
tmux rename-window -t $session:$window "radio"
tmux send-keys -t $session:$window "cd stringwave" C-m
tmux send-keys -t $session:$window "/bin/monitor_port &" C-m
tmux send-keys -t $session:$window "./ezstream.sh || pkill monitor_port" C-m
#session="metadata"
#tmux new-session -d -s $session
#tmux rename-window -t $session:$window "metadata"
#sleep 5 
#tmux send-keys -t $session:$window "cd stringwave/Radio && python stringwave/scripts/get_track_info.py" C-m
