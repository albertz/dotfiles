#!/bin/bash

set -ex

# https://www.cultofmac.com/222200/customize-mission-control-to-show-only-windows-from-current-desktop-space-os-x-tips/
defaults write com.apple.dock wvous-show-windows-in-other-spaces -bool FALSE
# Do `killall Dock` to enable.
