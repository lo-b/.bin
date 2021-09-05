#!/usr/bin/env python3
"""Nested Node Switcher
"""

from window_utils import (get_active_nodes, get_node_from_pid,
                          get_nvim_servernames, get_nvim_pid, get_all_buffers,
                          ENCODING)
import subprocess
from subprocess import PIPE, STDOUT

PROMPT = "Fly to window 🐦"

active_nodes = get_active_nodes()


def add_nvim_buffers(entry_to_info: dict[str, dict[str, str]],
                     rofi_input: list[bytes]) -> list[bytes]:
    """Add open neovim buffers to list of rofi options.

    Fills `entry_to_info` foor lookup of selection and add open vim buffers to
    `rofi_input` rofi options.

    Args:
        entry_to_info (dict[str, dict[str, str]]): data structure that contains
        lookup when an entry is selected as an option
        rofi_input (list[bytes]): list of options to pass to rofi

    Returns:
        list[str]: rofi_input with nvim buffers appended
    """

    # Fill lookup table
    for nvim_server in get_nvim_servernames():
        server_pid = get_nvim_pid(nvim_server)
        buffers = get_all_buffers(nvim_server)
        for buffer in buffers:
            node = get_node_from_pid(server_pid, active_nodes)

            if "term" not in buffer:
                entry_to_info[buffer] = {}
                if node is not None:
                    entry_to_info[buffer]["node"] = node

                entry_to_info[buffer]["servername"] = nvim_server

    # Add buffers to rofi options
    for key in entry_to_info.keys():
        rofi_input.append(key.encode(ENCODING))

    return icon_setter(rofi_input)


def icon_setter(rofi_input: list[bytes]) -> list[bytes]:
    """Adds icons to rofi input options.

    Checks per option to see what extension it has; add the
    corresponsding icon in `/usr/share/icons`.

    Args:
        rofi_input (list[bytes]): current rofi input options.

    Returns:
        list[bytes]: options with icons
    """

    rofi_input_icons: list[bytes] = [b"" for _ in range(len(rofi_input))]
    for i in range(len(rofi_input)):
        print(i)
        if b'.py' in rofi_input[i]:
            rofi_input_icons[i] = rofi_input[i] + b"\0icon\x1fpython"
        elif b'.rs' in rofi_input[i]:
            rofi_input_icons[i] = rofi_input[i] + b"\0icon\x1ftext-rust"
        else:
            rofi_input_icons[i] = rofi_input[i] + b"\0icon\x1fnvim"

    assert len(rofi_input_icons) == len(rofi_input)

    return rofi_input_icons


def switch_to_node(node: str):
    """Switch to node using bspc command.

    Execute `bspc` program to focus `node` passed in as an argument.

    Args:
        node (str): node to focus
    """

    subprocess.Popen(["bspc", "node", entry_to_info[node]["node"], "--focus"],
                     stdout=PIPE,
                     stderr=STDOUT)


def focus_nvim_buffer(buffer: str):
    """Focus a nvim buffer using nvr.

    Use neovim remote to focus `buffer`.

    Args:
        buffer (str): buffer to focus
    """

    buffer = buffer.replace("\'", "")
    subprocess.Popen([
        "nvr", "--servername", entry_to_info[selected_decoded]["servername"],
        "--remote", buffer
    ])


rofi_input = []
entry_to_info: dict[str, dict[str, str]] = {}
rofi_input = add_nvim_buffers(entry_to_info, rofi_input)

rofi_process = subprocess.Popen([
    "rofi", "-icon-theme", "Papirus", "-terminal", "kitty", "-theme",
    "gruvbox-dark", "-font", "JetBrainsMono Nerd Font 15", "-dmenu",
    "-show-icons", "-p", PROMPT
],
                                stdin=PIPE,
                                stdout=PIPE,
                                stderr=STDOUT)

# Run rofi with all options set above
selected, _ = rofi_process.communicate(b"\n".join(rofi_input))

# Selected option cleaned for lookup
selected_decoded = selected.decode(ENCODING).replace("\n", "")

switch_to_node(selected_decoded)

focus_nvim_buffer(selected_decoded)
