#!/usr/bin/env bash

# Script to lock screen in bspwm. Creates a printscreen, blurs it and slaps an
# icon on top of it.

icon="$HOME/images/lock_icon.png"
tmpbg='/tmp/screen.png'

(( $# )) && { icon=$1; }

scrot -o "$tmpbg"
convert "$tmpbg" -scale 10% -scale 1000% "$tmpbg"
convert "$tmpbg" "$icon" -gravity center -composite -matte "$tmpbg"
i3lock -u -i "$tmpbg"
