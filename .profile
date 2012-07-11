#!/bin/bash

export PATH="/usr/local/bin:$PATH"
#export PATH="$PATH:/opt/subversion/bin"
export PATH="/Users/az/.gem/ruby/1.8/bin:$PATH"
export PATH="/Users/az/.local/bin:$PATH"

alias m="/Applications/MPlayer\ OSX\ Extended.app/Contents/Resources/Binaries/mpextended.mpBinaries/Contents/mpextended.mpBinaries/Contents/MacOS/mplayer"
#alias m="/Applications/MPlayer\ OSX\ Extended.app/Contents/Resources/External_Binaries/mplayer.app/Contents/MacOS/mplayer"
#alias m="/Applications/MPlayer\ OSX.app/Contents/Resources/External_Binaries/mplayer.app/Contents/MacOS/mplayer"
#alias sshfs="/Applications/sshfs.app/Contents/Resources/sshfs-static-10.5"

#test -r /sw/bin/init.sh && . /sw/bin/init.sh

export LANG=en_US.UTF-8


#export PYTHONPATH=/Library/Frameworks/Python.framework/Versions/Current/lib/python2.5/site-packages/PIL
export PYTHONPATH="/Library/Python/2.7/site-packages/:/usr/local/lib/python2.7/site-packages/"

alias dosbox=/Applications/Spiele/DOSBox.app/Contents/MacOS/DOSBox

export ARCHFLAGS="-arch x86_64"
export PYTHONPATH=/usr/local/lib/python:$PYTHONPATH

# TODO: this more general
export PYTHONPATH=~/Programmierung/mechanize:$PYTHONPATH
export PYTHONPATH=~/Programmierung/pybrain:$PYTHONPATH
export PYTHONPATH=~/Programmierung/scikit-learn:$PYTHONPATH
export PYTHONPATH=~/Programmierung/requests:$PYTHONPATH

export NODE_PATH=/usr/local:/usr/local/lib/node:/usr/local/lib/node_modules
