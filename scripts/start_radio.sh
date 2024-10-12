#!/bin/bash

session="ezstream-new"
tmux new-session -d -s $session
tmux rename-window -t $session:$window "ezstream-new"
tmux send-keys -t $session:$window "cd /stringwave" C-m
tmux send-keys -t $session:$window "/bin/monitor_port 5801 &" C-m
tmux send-keys -t $session:$window "./scripts/ezstream.sh new || pkill monitor_port && touch .pid-new" C-m
# tmux send-keys -t $session:$window "./scripts/ezstream.sh new" C-m

session="ezstream-main"
tmux new-session -d -s $session
tmux rename-window -t $session:$window "ezstream-main"
tmux send-keys -t $session:$window "cd /stringwave" C-m
tmux send-keys -t $session:$window "/bin/monitor_port 5802 &" C-m
tmux send-keys -t $session:$window "./scripts/ezstream.sh main || pkill monitor_port && touch .pid-main" C-m
# tmux send-keys -t $session:$window "./scripts/ezstream.sh new" C-m

session="metadata-new"
tmux new-session -d -s $session
tmux rename-window -t $session:$window "metadata-new"
tmux send-keys -t $session:$window "sleep 30" C-m
tmux send-keys -t $session:$window "python scripts/grab_now_playing.py new" C-m
tmux send-keys -t $session:$window "./scripts/ezstream.sh new" C-m

session="metadata-main"
tmux new-session -d -s $session
tmux rename-window -t $session:$window "metadata-main"
tmux send-keys -t $session:$window "sleep 30" C-m
tmux send-keys -t $session:$window "python scripts/grab_now_playing.py main" C-m
tmux send-keys -t $session:$window "./scripts/ezstream.sh new" C-m