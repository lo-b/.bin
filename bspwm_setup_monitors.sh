#!/bin/bash

# Thanks to Miika Nissi
# https://miikanissi.com/blog/hotplug-dual-monitor-setup-bspwm/

# Get names of internal (primary) monitor and external monitor.
INTERNAL_MONITOR=$(xrandr -q | grep 'primary' | awk '{print $1}')
EXTERNAL_MONITOR=$(xrandr -q | grep 'HDMI' | grep ' connected ' | awk '{print $1}')

# Add the first five workspaces to the external monitor, remove the default
# desktop and reorder monitors.
function monitor_add() {
  for desktop in $(bspc query -D --names -m "$INTERNAL_MONITOR" | sed 5q); do
    bspc desktop "$desktop" --to-monitor "$EXTERNAL_MONITOR"
  done

  bspc desktop Desktop --remove
  bspc wm -O "$EXTERNAL_MONITOR" "$INTERNAL_MONITOR"
}

function monitor_remove() {
  # Add default temp desktop because a minimum of one desktop is required per monitor
  bspc monitor "$EXTERNAL_MONITOR" -a Desktop

  # Move all desktops except the last default desktop to internal monitor
  for desktop in $(bspc query -D -m "$EXTERNAL_MONITOR"); do
    bspc desktop "$desktop" --to-monitor "$INTERNAL_MONITOR"
  done

  # delete default desktops
  bspc desktop Desktop --remove

  # reorder desktops
  bspc monitor "$INTERNAL_MONITOR" -o I II III IV V VI VII VIII IX X
}

if [[ -n "${EXTERNAL_MONITOR}" ]]; then
  # If an HDMI screen is connected, put it above the primary screen
  mons -e top
  if [[ $(bspc query -D -m "${EXTERNAL_MONITOR}" | wc -l) -ne 5 ]]; then
    monitor_add
  fi

  bspc wm -O "$EXTERNAL_MONITOR" "$INTERNAL_MONITOR"
else
  # Otherwise, use the primary screen only
  mons -o

  # Move all workspaces from the external monitor back to primary monitor
  if [[ $(bspc query -D -m "${INTERNAL_MONITOR}" | wc -l) -ne 10 ]]; then
    monitor_remove
  fi
fi
