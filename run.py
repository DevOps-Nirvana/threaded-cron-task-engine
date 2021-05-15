#!/usr/bin/env python3
from __future__ import print_function
from subprocess import Popen, TimeoutExpired
import threading
import datetime
import time
import yaml
import os


##########################
# Configuration Variables
##########################

# Tmpdir (Must END in /)
tmpdir = "/tmp/"
try:
    tmpdir = os.environ['TMPDIR']
except:
    pass

# Config file path, defining our tasks to run
configpath = "./tasks.yml"
try:
    configpath = os.environ['CONFIGPATH']
except:
    pass    
with open(configpath, 'r') as stream:
    jobs = yaml.load(stream, Loader=yaml.FullLoader)


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
        last_run = 999999999999
        f = open(tmpfile_path, 'w')
        print(str(last_run), file=f)
        f.close()


    print("{}: Worker main loop launched...".format(label))
    while True:

        # Wait until the interval has passed...
        print("{}: Waiting for interval started...".format(label))
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
            print("{}: Running command...".format(label))
            myproc = Popen(command, shell=True)
            # If we have max runtime specified, then make this command timeout...
            if max_runtime != None:
                try:
                    myproc.wait(max_runtime)
                except TimeoutExpired as e:
                    print("{}: Command reached max_runtime, force killing...".format(label))
                    myproc.kill()
            else:
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
