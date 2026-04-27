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
import time
import queue
import threading
import requests

download_queue = queue.Queue()
completed_count = 0

lock = threading.Lock()
workers = []

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


#-------------------------------------------------------------------------------

# Part 2

def builtin_cat(args):
    
    if len(args) == 0:
        print("cat: missing file arguments")
        return

    for file in args:
        try: 
            with open(file, "r") as f:
                print(f.read(), end="")

        except FileNotFoundError:
            print(f"cat: {file}: No such file")
        
        except PermissionError:
            print(f"cat: {file}: Permission denied")

def builtin_head(args):
    
    # Checks for user arguments.
    if len(args) == 0:
        print("head: missing file arguments")
        return

    # Default Values.
    n = 10         # if num of lines isnt specified, default is 10.
    file = None    # Placeholder until file is specified.

    # Check's if user used -n.
    if args[0] == "-n":
        if len(args) < 3:
            print(f"head: use: head -n N {file}")
            return
        # convert num of lines inputted into integer.
        try:
            n = int(args[1])
        except ValueError:
            print("head: invalid number")
            return

        file = args[2] # Gets third arg, filename.
    else:
        file = args[0]

    try:
        with open(file, "r") as f:   # Opens file in read only.
            lines = f.readlines()
            for line in lines[:n]:
                print(line, end="")  # reads all lines.

    except FileNotFoundError:
        print(f"head: {file}: File not Found")
        
    except PermissionError:
        print(f"head: {file}: Permission denied")


def builtin_wc(args):

    if len(args) == 0:
        print("wc: missing file operand")
        return

    for file in args:
        try: 
            with open(file, "r") as f:

                text = f.read()
                lines = text.splitlines()
                line_count = len(lines)
                word_count = len(text.split())
                char_count = len(text)
                print(f"{line_count} {word_count} {char_count} {file}")

        except FileNotFoundError:
            print(f"wc: {file}: No such file")
        
        except PermissionError:
            print(f"wc: {file}: Permission denied")

#-------------------------------------------------------------------------------

# Part 3 
def bytes_to_gb(b):
    return b / (1024 ** 3) # converts bytes to gigabytes.

def builtin_sysinfo(args):

    while True:
        os.system("clear")
        
        # -- Gets memory information --
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        print(" -- MEMORY --")
        print(f"Total: {bytes_to_gb(mem.total):.2f} GB")
        print(f"Used: {bytes_to_gb(mem.used):.2f} GB")
        print(f"Available: {bytes_to_gb(mem.available):.2f} GB")
        print(f"Usage: {mem.percent}%")

        print("\n -- SWAP --")
        print(f"Total: {bytes_to_gb(swap.total):.2f} GB")
        print(f"Used: {bytes_to_gb(swap.used):.2f} GB")
        print(f"Free: {bytes_to_gb(swap.free):.2f} GB")

        print("\n -- CPU --")
        # CPU Usage Total.
        cpu_total = psutil.cpu_percent(interval=None)
        print(f"Total CPU Usage: {cpu_total}%")


        # CPU Usage per core.
        cpu_cores = psutil.cpu_percent(interval=0, percpu=True)
        for i, core in enumerate(cpu_cores):
            print(f"Core {i:<2}: {core:>5.1f}%")

        # -- Processes --

        for proc in psutil.process_iter():
            try:
                proc.cpu_percent(interval=None)
            except:
                pass

        time.sleep(1)

        processes = []

        for proc in psutil.process_iter(["pid","name","memory_percent"]):
            try :
                cpu = proc.cpu_percent(interval=None)
                info = proc.info
                info['cpu_percent'] = cpu
                processes.append(info)
            except:
                pass

        sort_by = "memory" # Default.

        if len(args) >= 2 and args[0] == "--sort":
            if args[1] in ["cpu", "memory"]:
                sort_by = args[1]

        if sort_by == "cpu":
            processes.sort(key=lambda p: p['cpu_percent'], reverse=True)
        else:
            processes.sort(key=lambda p: p['memory_percent'], reverse=True)

        top = processes[:10]

        print("\n-- TOP 10 PROCESSES --")
        print(f"{'PID':<6} {'NAME':<20} {'CPU%':<6} {'MEM%':<6}")

        for p in top:
            name = (p['name'] or "")[:20]
            print(f"{p['pid']:<6} {name:<20} {p['cpu_percent']:<6.1f} {p['memory_percent']:<6.2f}")
            

        # Wait before refreshing.
        time.sleep(2)

#-------------------------------------------------------------------------------
# Part 4 

# Queue Files

# Reads file line by line. Adds each URL to the sahred queue.

def load_urls(file):
    try:
        # Opens file in read only mode.
        with open(file, "r") as f:
            for line in f:
                # Removes the whitespace.
                url = line.strip()

                # Only add non-empty lines.
                if url:
                    # Put URL into shared queue.
                    download_queue.put(url)
    except FileNotFoundError:
        print(f"download: {file}: No such file")

# Download Command.
# Handles the downloading of URLs, status checking, and setting the amount of workers to the download.
def builtin_download(args):
    global workers

    if len(args) == 0:
        print("download: missing file")
        return

    # Status Command - Shows progress of current download.
    if args[0] == "--status":
        # Gets number of items in queue.
        queued = download_queue.qsize()

        print(f"Queued: {download_queue.qsize()}")
        print(f"Current workers: {len(workers)}")
        print(f"Completed: {completed_count}")

        # If the queue is empty then print download complete message.
        if queued == 0:
            print("All downloads complete.")
        return

    # Prevents starting multiple sets of workers at the same time.
    if workers:
        print("Workers already running")
        return

    # First arg is the file containing the URLs.
    file = args[0]

    num_workers = 3 # Default value.

    # Check if user specified custome worker amount.
    if "-w" in args:
        try:
            # Get the vlaue that comes after "-w"
            num_workers = int(args[args.index("-w") + 1])
        except:
            print("download: invalid worker count")
            return
    
    # Loads URLs into the queue
    load_urls(file)

    # Creates the worker thread. Each worker runs in the background and precesses the queue
    for _ in range(num_workers):
        t = threading.Thread(target = worker, daemon = True)
        t.start()
        workers.append(t)

    print (f"Loaded URLs: Starting {num_workers} workers..")



# Worker Command. Takes URL from Queue. Downloads URL. Saves it to file. Updates completed counter safely with lock.
def worker():
    global completed_count
    # Runs infinitly waiting for new tasks.
    while True:
        # Get next URL in queue
        url = download_queue.get()
        #print(f"Downloading: {url}")

        try: 
            # sends a Http request to download the file
            response = requests.get(url, timeout=5)

            # Makes downloads folder if it doesnt already exist
            os.makedirs("downloads", exist_ok=True)

            # Gets the file name from URL.
            # If URL ends with "/", deafult to index.html
            filename = url.split("/")[-1] or "index.html"

            # Creates the full file path
            filepath = os.path.join("downloads", filename)

            # Writes the file in binary mode. for files with non-text content
            with open(filepath, "wb") as f:
                f.write(response.content)

            # Thread safe counter increment
            # Prevents multiple threads updating at the same time. Lock used to prevent race conditions.
            with lock:
                completed_count += 1

        except Exception:
            print(f"download error: {url}")
        
        finally:
            download_queue.task_done()

    
