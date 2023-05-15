#!/bin/bash

tmux kill-session -t icecast
tmux kill-session -t ezstream-new
tmux kill-session -t ezstream-main
#tmux kill-session -t metadata
pkill ezstream
