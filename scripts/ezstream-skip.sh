#!/bin/bash

station=$1
pid="$(cat /stringwave/.pid-$station)"

# reread in case playlist has changed
# cat /stringwave/.pid-$station | xargs kill -SIGHUP
kill -SIGHUP $pid

# wait to allow reread to take effect
# sleep 1

# cat /stringwave/.pid-$station | xargs kill -SIGUSR1
kill -SIGUSR1 $pid