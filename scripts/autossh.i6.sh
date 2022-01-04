#!/bin/bash

# OSX install:
#   link autossh.i6.launchd.plist to ~/Library/LaunchAgents
#   launchctl load ~/Library/LaunchAgents/autossh.i6.launchd.plist
#   launchctl start autossh.i6
#   for changes, do:
#     launchctl stop autossh.i6
#     launchctl unload ~/Library/LaunchAgents/autossh.i6.launchd.plist
#   https://www.launchd.info/

autossh -M 20000 -D 8888 i6 -N
