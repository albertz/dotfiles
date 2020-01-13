#!/bin/bash

export PATH="/usr/local/bin:/usr/local/sbin:$PATH"
#export PATH="$PATH:/opt/subversion/bin"
export PATH="/Users/az/.gem/ruby/1.8/bin:$PATH"
export PATH="/Users/az/.cargo/bin:$PATH"
export PATH="/Users/az/.local/bin:$PATH"
export PATH="/Users/az/Programmierung/system-tools/bin:$PATH"
export PATH="/usr/local/kde4/bin:$PATH"
export PATH="$PATH:/Users/az/Library/Python/3.7/bin:/Users/az/Library/Python/2.7/bin"

alias m="/Applications/MPlayer\ OSX\ Extended.app/Contents/Resources/Binaries/mpextended.mpBinaries/Contents/mpextended.mpBinaries/Contents/MacOS/mplayer"
#alias m="/Applications/MPlayer\ OSX\ Extended.app/Contents/Resources/External_Binaries/mplayer.app/Contents/MacOS/mplayer"
#alias m="/Applications/MPlayer\ OSX.app/Contents/Resources/External_Binaries/mplayer.app/Contents/MacOS/mplayer"
#alias sshfs="/Applications/sshfs.app/Contents/Resources/sshfs-static-10.5"

#test -r /sw/bin/init.sh && . /sw/bin/init.sh

export LANG=en_US.UTF-8


#export PYTHONPATH=/Library/Frameworks/Python.framework/Versions/Current/lib/python2.5/site-packages/PIL
#export PYTHONPATH="/usr/local/lib/python2.7/site-packages/:/Library/Python/2.7/site-packages/"

alias dosbox=/Applications/Spiele/DOSBox.app/Contents/MacOS/DOSBox

# Note that Sage fails to build with this:
#export ARCHFLAGS="-arch x86_64"

export CC=cc
export CXX=c++

#export CFLAGS="-isysroot /Developer/SDKs/MacOSX10.6.sdk -DMAC_OS_X_VERSION_MIN_REQUIRED=1060"

export PYTHONPATH=/usr/local/lib/python:$PYTHONPATH

# TODO: this more general
#export PYTHONPATH=~/Programmierung/mechanize:$PYTHONPATH
#export PYTHONPATH=~/Programmierung/pybrain:$PYTHONPATH
#export PYTHONPATH=~/Programmierung/scikit-learn:$PYTHONPATH
#export PYTHONPATH=~/Programmierung/requests:$PYTHONPATH
#export PYTHONPATH=~/Programmierung/py_better_exchook:$PYTHONPATH
#export PYTHONPATH=~/Programmierung:$PYTHONPATH

export NODE_PATH=/usr/local:/usr/local/lib/node:/usr/local/lib/node_modules

# for installing camliststore, it needs `pkg-config --cflags sqlite3` to work.
export PKG_CONFIG_PATH=/usr/local/opt/sqlite/lib/pkgconfig/


# For Octave.
# http://stackoverflow.com/questions/13786754/octave-gnuplot-aquaterm-error-set-terminal-aqua-enhanced-title-figure-1-unk
# http://www.mac-forums.com/forums/os-x-apps-games/242997-plots-octave-dont-work.html
# https://github.com/mxcl/homebrew/issues/14647
export GNUTERM=x11


export NUPIC=~/Programmierung/nupic
export NTA=$NUPIC/build


export PATH="$HOME/.cargo/bin:$PATH"


# https://github.com/mobile-shell/mosh/issues/98
# might need locale-gen?
export LC_CTYPE="en_US.UTF-8"
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8


