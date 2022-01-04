#!/bin/bash

# OSX install:
#   https://stackoverflow.com/questions/58442951/how-to-fix-operation-not-permitted-when-i-use-launchctl
#   link autossh.i6.launchd.plist to ~/Library/LaunchAgents
#   launchctl load ~/Library/LaunchAgents/autossh.i6.launchd.plist
#   launchctl start autossh.i6
#   check:
#     launchctl list | grep autossh
#     ps ax | grep autossh
#   for changes, do:
#     launchctl stop autossh.i6
#     launchctl unload ~/Library/LaunchAgents/autossh.i6.launchd.plist
#   launchctl/launchd docs: https://www.launchd.info/

autossh -M 20000 -D 8888 i6 -N
