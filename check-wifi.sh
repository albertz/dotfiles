#!/bin/bash

wifi=UPC2544C39

# turn on wifi if it's turned 'Off'
if [ $(networksetup -getairportpower en1 | grep -c 'Off') = '1' ]; then
  echo "Network is off:"
  networksetup -getairportpower en1
  echo "Enabling..."
  networksetup -setairportpower en1 on
  echo "Wait..."
  sleep 10
fi

# cycle wifi power if missing 'IP address'
if [ $(networksetup -getinfo Wi-Fi | grep -c 'IP address:') = '1' ]; then
  echo "No IP:"
  networksetup -getinfo Wi-Fi
  echo "Disconnect..."
  networksetup -setairportpower en1 off
  echo "Wait..."
  sleep 5
  echo "Reconnect..."
  network setup -setairportpower en1 on
fi

# initiate connection if not connected to the correct network
if [ $(networksetup -getairportnetwork en1 | grep -c "$wifi") = 0 ]; then
  echo "Wrong network: $(networksetup -getairportnetwork en1)"
  echo "Connect to $wifi ..."
  networksetup -setairportnetwork en1 "$wifi"
  echo "Wait..."
  sleep 5
fi

