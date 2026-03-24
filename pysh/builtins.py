"""
Built-in commands for pysh.

Built-in commands are handled directly by the shell, rather than by
running an external program. For example, 'cd' must be a built-in
because changing directory needs to affect the shell process itself.

Each built-in is a function that takes a list of string arguments.
Look at builtin_pwd below as a complete example to follow.
"""

import os
import sys
import psutil

# ---------------------------------------------------------------------------
# Example built-in: pwd
# ---------------------------------------------------------------------------


def builtin_pwd(args):
    """
    Print the current working directory.

    Uses os.getcwd() which asks the operating system for the current
    working directory of this process.

    Example usage:
        pysh /home/student $ pwd
        /home/student
    """
    print(os.getcwd())


# ---------------------------------------------------------------------------
# Example built-in: exit
# ---------------------------------------------------------------------------


def builtin_exit(args):
    """
    Exit the shell.

    Raises SystemExit which is caught by the main loop in shell.py
    to break out of the loop cleanly.
    """
    sys.exit(0)


# ---------------------------------------------------------------------------
# TODO: Implement the remaining built-in commands below.
#       Each function receives a list of string arguments.
#       Look at builtin_pwd above as an example to follow.
# ---------------------------------------------------------------------------

def builtin_echo(args):
    if len(args) == 0:
        print("Error: echo requires at least one argument")
        print("Usage: echo <text>")
        return
    print(" ".join(args))
 
 
#-------------------------------------------------------------------------------
 
def builtin_cd(args):
    if len(args) == 0:
        print("cd: Missing argument")
        path = os.path.expanduser("~")
    else:
        path = args[0]
    try:
        os.chdir(path)
    except FileNotFoundError:
        print(f"cd: directory not found {path}")
    except PermissionError:
        print(f"cd: permission restricted {path}")

 
#-------------------------------------------------------------------------------


def builtin_help(args):
    """
    Display available built-in commands.
    """

    print("Available commands:\n")

    print("pwd    - show's current directory")
    print("cd     - change current directory")
    print("echo   - print's text")
    print("exit   - exit the shell")
    print("help   - you should know this one")
    print("procinfo <pid> - show process information")

#-------------------------------------------------------------------------------

def builtin_procinfo(args):

    if len(args) != 1:
        print("UseCase: procinfo <pid>")
        return

    try:
        pid = int(args[0])
        process = psutil.Process(pid)

        print(f"PID: {process.pid}")
        print(f"Status: {process.status()}")
        print(f"Parent PID: {process.ppid()}")

        cpu = process.cpu_times()
        print(f"CPU Time (User): {cpu.user}")
        print(f"CPU Time (System): {cpu.system}")

        memory = process.memory_info()
        print(f"Memory Usage: {memory.rss} Bytes")

    except ValueError:
        print("procInfo: PID Has to be a number")

    except psutil.NoSuchProcess:
        print(f"procInfo: process {args[0]} Not Found")

