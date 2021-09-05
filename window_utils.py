"""Window utils using linux commands.
"""

import subprocess
from subprocess import PIPE, STDOUT
from typing import Optional

ENCODING = 'UTF-8'


def get_active_nodes() -> list[str]:
    """Get active nodes using bspc.

    Get all the active nodes/windows their (hex) ids.

    Returns:
        list[str]: A list of node ids.
    """

    p = subprocess.Popen(["bspc", "query", "-N", "-n", ".leaf"],
                         stdout=PIPE,
                         stderr=STDOUT)

    stdout, _ = p.communicate()

    active_nodes = stdout.decode(ENCODING)

    p.terminate()

    return active_nodes.splitlines()


def get_node_name(node: str) -> str:
    """Get the WM_STRING name of the window using xprop.

    Args:
        node (str): Id (in hex) of the node.

    Returns:
        str: The WM_CLASS line of the xprop output.
    """

    xprop_out = subprocess.Popen(["xprop", "-id", node],
                                 stdout=PIPE,
                                 stderr=STDOUT)

    grep_out = subprocess.Popen(["grep", "WM_CLASS"],
                                stdin=xprop_out.stdout,
                                stdout=PIPE,
                                stderr=STDOUT)

    stdout, _ = grep_out.communicate()

    return stdout.decode('utf-8')


def get_node_pid(hex_id: str) -> int:
    """Get the process ID of hex node.

    Gets the process id of the node's hex representation by using `xprop -id`

    Args:
        hex_id (str): hex_id of the node.

    Returns:
        int: the pid of the node
    """

    xprop_put = subprocess.Popen(["xprop", "-id", str(hex_id)],
                                 stdout=PIPE,
                                 stderr=STDOUT)

    grep_out = subprocess.Popen(["grep", "_WM_PID"],
                                stdin=xprop_put.stdout,
                                stdout=PIPE,
                                stderr=STDOUT)

    stdout, _ = grep_out.communicate()

    return int(stdout.decode('utf-8').split()[2])


def get_all_buffers(nvim_server: str) -> list[str]:
    """Get all open buffer.

    Use neovim remote (nvr) to get buffers of a (nvim) server/instance.

    Args:
        nvim_server (str): nvim instance to get buffers from

    Returns:
        list[str]: list of open buffers
    """

    nvr_out = subprocess.Popen([
        "nvr", "--servername", nvim_server, "--remote-expr",
        "join(GetActiveBuffers())"
    ],
                               stdout=PIPE,
                               stderr=STDOUT)

    stdout, _ = nvr_out.communicate()

    return stdout.decode(ENCODING).split()


def get_nvim_servernames() -> list[str]:
    """Get all nvim servers.

    Use nvr to get all nvim servers running.

    Returns:
        list[str]: list of running servers
    """

    nvr_out = subprocess.Popen(["nvr", "--serverlist"],
                               stdout=PIPE,
                               stderr=STDOUT)

    stdout, _ = nvr_out.communicate()

    return stdout.decode(ENCODING).split()


def get_nvim_pid(server_name: str) -> int:
    """Get process ID of nvim.

    Send remote expression to get the pid for nvim server to execute and return
    the value.

    Args:
        server_name (str): servername

    Returns:
        int:
    """

    nvr_out = subprocess.Popen([
        "nvr", "--servername", server_name, "--remote-expr", "getpid()",
        "--nostart"
    ],
                               stdout=PIPE,
                               stderr=STDOUT)

    stdout, _ = nvr_out.communicate()

    return int(stdout.decode(ENCODING).replace('\n', ''))


def get_children_pids(node_pid: int, out: list[str]):
    """Get all children PIDs of node PID.

    Use `pgrep` to recursively search for child process ids.

    Args:
        node_pid (int): process id to get children of
        out (list[str]): list of pids which are children of `node_pid`
    """

    pgrep_out = subprocess.Popen(["pgrep", "-P", str(node_pid)],
                                 stdout=PIPE,
                                 stderr=STDOUT)

    stdout, _ = pgrep_out.communicate()

    children_pids = stdout.decode(ENCODING).replace('\n', '').split()

    if len(children_pids) > 0:
        for child in children_pids:
            out.append(child)
            get_children_pids(int(child), out)


def get_node_from_pid(pid: int, all_nodes: list[str]) -> Optional[str]:
    """Get node id in hex format.

    Recursively search `all_nodes` to see if it contains `pid`.

    Args:
        pid (int): pid to search for
        all_nodes (list[str]): all (bspwm) nodes to switch to

    Returns:
        Optional[str]: the found hex id or `None` if it couldn't be found
    """

    for node in all_nodes:
        if "kitty" in get_node_name(node):
            node_pid = get_node_pid(node)
            children_pids = []
            get_children_pids(node_pid, children_pids)

            if str(pid) in children_pids:
                return node
