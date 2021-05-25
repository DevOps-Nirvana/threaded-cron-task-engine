#!/usr/bin/env python3
from __future__ import print_function
from subprocess import Popen, TimeoutExpired
import threading
import datetime
import signal
import time
import yaml
import os


##########################
# Configuration Variables
##########################

def readEnvOrDefault(envname, default=False):
    try:
        return os.environ[envname]
    except:
        return default

# Tmpdir, this MUST end in /
tmpdir = readEnvOrDefault('TMPDIR', '/tmp/')
# To prevent flooding, sleep this amount between launching threads
thread_launch_interval = int(readEnvOrDefault('THREADLAUNCHINTERVAL', '1'))
# Config file path, defining our tasks to run, default to cwd tasks.yml file
configpath = readEnvOrDefault('CONFIGPATH', './tasks.yml')
# Open our configuration file to load our job configuration
try:
    with open(configpath, 'r') as stream:
        try:
            jobs = yaml.load(stream, Loader=yaml.FullLoader)
        except:
            jobs = yaml.load(stream) # This is a fallback to using an older pyyaml without the security patch
except:
    print("Fatal error: Unable to read or parse {}".format(configpath))
    raise 


###################
# Helper Functions
###################

# Helper to check if between hours...
def checkIfBetweenHours(start=None, end=None):
    timestamp = datetime.datetime.now().time() # Throw away the date information

    # convert start or end to time object
    if start:
        start = datetime.time(start, 00)
    if end:
        end = datetime.time(end, 00)

    # Checking...
    if end and start:
        if end < start:
            return (timestamp <= end)
        else:
            return (start <= timestamp <= end)
    elif end:
        return (timestamp <= end)
    elif start:
        return (start <= timestamp)
    else:
        return (True)


# Our main worker thread that does all the magic
def worker(label, command, interval, start=None, end=None, chdir=None, max_runtime=None):
    """thread worker function"""
    print('{}: Worker started for in interval {}'.format(label, interval))
    tmpfile_path = "{}{}.lastrun".format(tmpdir,label)
    
    if chdir is not None:
        print('{}: Worker chdir {}'.format(label, chdir))
        os.chdir(chdir)

    try:
        with open (tmpfile_path) as myfile:
            print("{}: opened previous file".format(label))
            last_run = int(myfile.read())
            print("{}: got last run {}".format(label, last_run))
    except:
        print("{}: setting new last run".format(label))
        last_run = 0
        f = open(tmpfile_path, 'w')
        print(str(last_run), file=f)
        f.close()

    print("{}: Worker main loop launched...".format(label))
    while True:

        # Wait until the interval has passed...
        print("{}: Waiting for interval {}, must wait another {} seconds...".format(label, interval, last_run - (int(time.time()) - int(interval))))
        while last_run > int(time.time()) - int(interval):
            # print("{}: Waiting for interval...".format(label))
            time.sleep(1)

        # Record when we ran (before we run)
        last_run = int(time.time())
        f = open(tmpfile_path, 'w')
        print(str(last_run), file=f)
        f.close()

        # Check if in operating hours (or none specified) then run the requested command...
        if checkIfBetweenHours(start, end):
            myproc = Popen(command, start_new_session=True, shell=True)
            # If we have max runtime specified, then make this command timeout...
            if max_runtime != None:
                try:
                    print("{}: Running command with timeout at {} seconds...".format(label, max_runtime))
                    myproc.wait(int(max_runtime))
                except TimeoutExpired as e:
                    print("{}: Command reached max_runtime, force killing...".format(label))
                    try:
                        os.killpg(os.getpgid(myproc.pid), signal.SIGTERM)  # Send a signal to kill the entire process group (sub-shell)
                        time.sleep(1)                                      # Wait just incase for clean exit
                        # myproc.kill()                                      # Send force kill to the parent if the TERM didn't kill it (this can cause zombies, skipping)
                        outs, errs = myproc.communicate()                  # "Hack" to clean zombies communicating (uselessly) to the subprocess
                    except:
                        pass
            else:
                print("{}: Running command with no timeout...".format(label))
                myproc.wait()  # Wait forever if not max runtime specified
            print("{}: Command completed with exit code {}".format(label, myproc.returncode))
        else:
            print("{}: Skipping, outside operating hours".format(label))


# Spawning our worker threads
threads = []
for key,value in jobs.items():

    # Required inputs
    if 'command' not in value:
        raise Exception("Error in {}: Command not specified".format(key))
    if 'interval' not in value:
        raise Exception("Error in {}: Interval not specified".format(key))

    # Input validation (optional inputs)
    if 'run_after' not in value:
        value['run_after'] = None
    if 'run_before' not in value:
        value['run_before'] = None
    if 'chdir' not in value:
        value['chdir'] = None
    if 'max_runtime' not in value:
        value['max_runtime'] = None

    # Start our worker thread
    t = threading.Thread(
        target=worker,
        args=(
            key,                  # Label
            value['command'],     # Command
            value['interval'],    # interval
            value['run_after'],   # start
            value['run_before'],  # end
            value['chdir'],       # chdir
            value['max_runtime'], # max_runtime
        )
    )
    threads.append(t)
    t.start()
    
    # To prevent flooding of our system, sleep 1 second between new thread creations, just incase
    time.sleep(thread_launch_interval)
