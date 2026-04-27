"""
pysh — A minimal shell built in Python.

This is the main module. It runs the shell loop:
  1. Display a prompt
  2. Read a line of input
  3. Parse it into a command and arguments
  4. Execute the command
  5. Repeat
"""

import grp
import os
import subprocess

from pysh.builtins import builtin_exit, builtin_pwd, builtin_cd, builtin_echo, builtin_help, builtin_procinfo, builtin_cat, builtin_head, builtin_wc, builtin_sysinfo, builtin_download
from pysh.colors import BLUE, GREEN, RESET


def prompt():
    """Return the shell prompt string showing the current directory."""
    cwd = os.getcwd()
    user = os.environ.get("USER")
    group = grp.getgrgid(os.getgid()).gr_name

    return f"{GREEN}{user}@{group}{RESET}:{BLUE}{cwd}{RESET}$ "


def parse(line):
    """
    Parse a line of input into a command name and a list of arguments.

    Example:
        parse("echo hello world") returns ("echo", ["hello", "world"])
        parse("") returns (None, [])
    """
    parts = line.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]


def execute(command, args):
    """
    Execute a command with the given arguments.

    First checks if the command is a built-in. If not, tries to run it
    as an external program using subprocess.
    """
    # Part 4 Background Processes
    background = False
    
    # Checks if args exists and if the last arg is "&"
    if args and args[-1] == "&":
        background = True
        args = args[:-1] # Removes the & from args, because its not part of the command

    # I/O Redirection (>, >>)
    redirect = None
    filename = None

    # Check for append operator
    if ">>" in args:
        
        idx = args.index(">>")    # Finds position of ">>"
        redirect = "a"            # "a" = append mode
        filename = args[idx +1]   # Gets filename
        args = args[:idx]         # Removes ">>" and filename from args

    # Checks for overwrite operator
    elif ">" in args: 
        
        idx = args.index(">")     # Finds position of ">"
        redirect = "w"            # "w" write mode to overwrite file
        filename = args[idx + 1]  # gets filename after ">"
        args = args[:idx]         # Removes ">" and filename so its just the command

    # TODO: Add your own built-in commands here
    
    if command == "pwd":
        builtin_pwd(args)

    elif command == "touch":
        builtin_touch(args)
    
    elif command == "help":
        builtin_help(args)

    elif command == "echo":
        builtin_echo(args)

    elif command == "cd":
        builtin_cd(args)
    
    elif command == "procinfo":
        builtin_procinfo(args)

    elif command == "exit":
        builtin_exit(args)
        
    elif command == "cat":
        builtin_cat(args)

    elif command == "head":
        builtin_head(args)

    elif command == "wc":
        builtin_wc(args)

    elif command == "download":
        builtin_download(args)

    elif command == "sysinfo":
        builtin_sysinfo(args)

    else:
        try:
            # Checks if user used ">" or ">>", then redirect output to a file
            if redirect:

                # Opens file in either "w" or "a"
                # w = overwrite
                # a = append
                with open(filename, redirect) as f:
                    if background:
                        # Popen runs process without blocking the shell
                        # stdout=f means that the output goes to the file instead of the terminal
                        proc = subprocess.Popen([command] + args, stdout=f)

                        # Print process ID so user is aware its running 
                        print(f"[{proc.pid}] Running in Background")
                    else:

                        # run() puts a block up untill command finishes
                        # stdout=f redirects output into the file
                        subprocess.run([command] + args, stdout=f)
                        
            else:
                if background:
                    proc = subprocess.Popen([command] + args)
                    print(f"{proc.pid} Running in Background")
                else:
                    subprocess.run([command] + args)

        except FileNotFoundError:
            print(f"pysh: {command}: command not found")
    
    


def main():
    """Entry point for the shell."""

    print(
        r"""
 __
 \ \
  \ \
  / /
 /_/   ______
      /_____/"""
    )

    print()
    print("Welcome to pysh! Type 'help' to see available commands.\n")

    while True:
        try:
            line = input(prompt())

            command, args = parse(line)

            # If the user just pressed Enter, show the prompt again
            if command is None:
                continue

            execute(command, args)

        except EOFError:
            # Ctrl+D — exit the shell
            print("\nGoodbye!")
            break

        except KeyboardInterrupt:
            # Ctrl+C — don't exit, just move to a new line
            print()
            continue

        except SystemExit:
            # The exit command was called
            break
