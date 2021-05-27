# Multithreaded Cron/Task Engine

With 20+ years of experience as an DevOps Architect I found the need for an Cron/Task engine (similar to [supervisord](http://supervisord.org/)) that can run a process regularly on a schedule/interval that can...

* Remember the previous interval it ran last and continues to execute it properly on that schedule
* Allows you to specify certain days/times of the day to skip running (pointing fingers at cron/supervisord)
* Detects and kills a child process if it runs too long (laughing at cron/supervisord)
* Allows you to change into a specific directory before running (silly cron, tho can manually DiY this)
* Guarantees it doesn't run a command more than once (I'm looking at you cron, have to hack around this)
* Runs scripts with a full shell environment/tty (ahh cron you are painful in this regard)
* Something super easy to setup, run, and maintain (_stares at supervisord intently_)
* Have little or no dependencies on any system packages or libraries, giving maximum portability
* Can execute any language, script, executable easily as long as it can be executed by a shell command
* Runs reliably and consistently on every operating system

Honestly, with that list above, there isn't a tool out there that can do all, or most of those _well_, which simply disappoints me.

After wrestling with similar tools in this space with gaps left, I felt I needed to write something.  If I had the time I would probably write this as a plugin for supervisord because they have a solid enough framework, but the complexity of that codebase puts this out of reach.  In this codebase, I accomplish most or all of what Supervisord and Cron does, plus a bunch of great features, and do it within' only a few pages of easy to understand Python code.

The simplicity of this code also helps promote its support, usage, and adaptation.  I encourage you to take this code and tweak it to do whatever you want!  If it makes sense send me a Pull Request, and I'll consider accepting it, although the goal of this project directly is to stay _dead simple_ over adding tons and tons of features.  I do not want this to become SupervisorD and be impossible to maintain.

# Usage (Installation)

To get started simply install the requirements with `pip install pyyaml` or `pip install -r requirements.txt` and then `python3 run.py` or `./run.py`.  It should immediately start up and run on Linux/Mac.  On Windows you will need an slightly different config file, basically just use Windows-specific paths for chdir.  See `tasks-windows.yml`.  Also on Windows CTRL-C doesn't always kill the entire engine and all children.  You may need to force-kill the process from the task manager, or simply close the window if you ran it in an Windows Command Prompt/shell.

To begin configuring the tasks you wish to run, please edit the `tasks.yml` file and add the commands you wish to run.  The file is well documented and self explanatory.  Put in the tasks you wish to add, and re-run `run.py` and watch it work.

I would recommend installing this somewhere in your system.  Perhaps by running `cp run.py /usr/local/bin/threaded-cron-engine && chmod a+x /usr/local/bin/threaded-cron-engine`.  A simply way to run this might be to run this in a `session` in Linux so you can detach from it and it runs forever.  Alternatively, you may want to ensure it is running and runs on boot with an init script specific to your system, or (amusingly) run it via Supervisord.  For the purposes of this codebase, at this time, I am not adding any init/boot-like scripts, although if some contributor took the time to write some really good ones, I wouldn't turn down a Pull Request.

# Usage (Runtime)

To make it easy for dockerization, there's some environment variables present to configure this.
`TMPDIR` == The directory to store the "lastrun" files, to know when each task last run successfully
`CONFIGPATH` == The path to the tasks.yml file, can be absolute or relative (to cwd)

Example:
```
export TMPDIR=/tasks
export CONFIGPATH=/app/tasks.yml
/usr/local/bin/threaded-cron-engine.py
```

# Example Docker Integration

To add this to an existing docker container to run some background tasks, assuming an `ubnutu:latest` container would be to add the following to your Dockerfile.

```
FROM ubuntu:latest

### Install our threaded cron task engine
RUN apt-get update && \
# Get Python3 Pre-Installed (for some scripting and automation)
    apt-get install python3 python3-pip wget -y && \
    pip3 install pyyaml && \
# Install our task manager
    wget https://github.com/DevOps-Nirvana/threaded-cron-task-engine/releases/download/v1.0.1/run.py -O /usr/local/bin/threaded-cron-task-engine.py && \
    chmod a+x /usr/local/bin/threaded-cron-task-engine.py && \
# Final cleanup
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -Rf /tmp/*

WORKDIR /app
COPY tasks.yml /app/tasks.yml
COPY * /app/

ENTRYPOINT ["/usr/local/bin/threaded-cron-task-engine.py"]
```

To this above Docker image you will install the threaded engine, then add your codebase-specific tasks.yml file to define the tasks to run, and then specify our entrypoint to start up our engine

# TODO

* Add ability to set environment variables (per task)
* Add metrics?  (Prometheus?)
* Add more/some Try/Catch-es to ensure/maximize uptime?  Just incase?  Right now if there's an issue in the script it fatal errors the whole process, but the script is simple enough this _should_ never occur.  I kind-of like it failing at the moment for fatal issues, makes it obvious during development if something is broken.  This won't happen ever in any child-ran subtask.  Those can crash all they want.
* Dockerize and publish this into Docker Hub, making it easy(ier) for others to integrate and build off of (related to adding Prometheus metrics)
* Allow signaling via HUP to reload the config and only change/restart changed threads.
* Instead-of the hard-kill that occurs now when you CTRL-C, allow catching of signals to parent thread and (optionally?) pass down into threads
* Add detection of duplication of execution of this script.  Shouldn't be able to run twice (in the same folder/config?) (localhost port listener?)
* Add ability to query/tweak/restart a specific child process (similar to supervisor_ctl commands) and leave the others untouched
* Make "before/after" also support a date and datetime format instead of just an "hour before/after", detect the format and use accordingly
* Add ability to specify in a crontab-like format alternatively...?  (Maybe?  idk, I don't like this idea though)
* Make init script(s) for some popular Linux distributions
* Package this and submit it to package repositories (Ubuntu/Debian/CentOS)
* Alternatively, package and distribute this via pip
* Write some tests for each of the various features to be sure it works and continues to work as intended
* Make all logs pre-thread have a forced prefix?  Would need to buffer output to accomplish this, and it might break some output data formats especially multi-line ones (eg: JSON, or a stacktrace)
* Others / Profit ???

Note: With any of these above, consider the goal of this codebase is to stay simple to maintain.  If some of these would require pages and pages of code, unless it is deemed critical I would almost skip adding the feature.  I've just highlighted some desires that I will _possibly_ eventually implement in this codebase, or you're welcome to try.

# DONE

* (FINALLY) Published the code as Open Source Software on Github after many years of it laying around
* Documented and cleaned up the codebase, added this awesome readme
* Integrated the max_runtime feature directly into the codebase instead of being an (annoying) helper script
* Making a few variables configurable via env vars making it easier to Dockerize in the future
* Do some/more Windows testing, add documentation and examples for Windows.

# History

This codebase in some form has been used in about a dozen companies over the last 10 years.  I've iterated on it and tweaked it over time, it currently proudly powers a few larger website's background task engines with ~40+ tasks running/scheduled concurrently with a ridiculous uptime.  I've been meaning to open-source it forever.

# Contributions

Please feel free to send Pull Requests, preferably filling one of the gaps of TODO or fixing a bug you've found.  Please follow a similar style, comment your code, add new info to the README, etc as necessary.  Feel free to ask questions via my email below, or submit an [issue](https://github.com/DevOps-Nirvana/threaded-cron-task-engine/issues).

# Support / Author

Written and supported exclusively by Farley Farley (and yes, that's my name).  I'm on Github @ [AndrewFarley](http://github.com/andrewfarley), LinkedIn @ [Mr-Farley](https://www.linkedin.com/in/mr-farley/), AngelList @ [Farley-Farley](https://angel.co/u/farley-farley) and via email _farley_ AT **neonsurge** _dot_ com

Please file [issues on Github](https://github.com/DevOps-Nirvana/threaded-cron-task-engine/issues) or contact me on any platform above.  I'd be happy to hear of any success stories of yours with this, or your pain points with other systems that you think this tool might solve.
