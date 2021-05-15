# Multithreaded Cron/Task Engine

This codebase from [Github](https://github.com/DevOps-Nirvana/threaded-cron-task-engine) fixes the following problem(s) I've encountered in the field of DevOps and automation...

* Need a Cron/Task engine similar to supervisord/cron to run a process regularly on a schedule/interval that...
* Remembers the previous interval it ran the script and continues to execute it properly on that schedule
* Allows you to specify certain days/times of the day to "skip" running
* Detects and kills a child process if it runs too long (silly cron/supervisord)
* Allows you to change into a specific directory before running (silly cron)
* Guarantees it doesn't run a command more than once (I'm looking at you cron)
* Runs scripts with a full shell environment/tty (silly cron)
* Something super easy to setup, run, and maintain
* Can execute any language, script, executable easily
* Runs reliably and the same way on every operating system

Honestly, with that list above, there isn't a tool out there that can do all, or most of those _well_, which simply disappoints me.

After wrestling with similar tools in this space with gaps left, I felt I needed to write something.  If I had the time I would probably write this as a plugin for supervisord because they have a solid enough framework, but the complexity of that codebase puts this out of reach.  In this codebase, I accomplish most or all of what Supervisord and Cron does, plus a bunch of great features, and do it within' only a few pages of easy to understand Python code.

The simplicity of this code also helps promote its support, usage, and adaptation.  I encourage you to take this code and tweak it to do whatever you want!  If it makes sense send me a Pull Request, and I'll consider accepting it, although the goal of this project directly is to stay _dead simple_ over adding tons and tons of features.  I do not want this to become SupervisorD and be impossible to maintain.

# Usage

To get started simply install the requirements with `pip install pyyaml` or `pip install -r requirements.txt` and then `python3 run.py` or `./run.py`.  It should immediately start up and run on Linux/Mac.  On Windows you will need a different config file (todo, add an example for windows).

To begin configuring the tasks you wish to run, please edit the tasks.yml file and add the commands you wish to run.  The file is well documented and self explanatory.  Put in the tasks you wish to add, and re-run `run.py` and watch it work.

I would recommend installing this somewhere in your system.  Perhaps by running `cp run.py /usr/local/bin/threaded-cron-engine && chmod a+x /usr/local/bin/threaded-cron-engine`.  A simply way to run this might be to run this in a `session` in Linux so you can detach from it and it runs forever.  Alternatively, you may want to ensure it is running and runs on boot with an init script specific to your system, or (amusingly) run it via Supervisord.  For the purposes of this codebase, at this time, I am not adding any init/boot-like scripts, although if some contributor took the time to write some really good ones, I wouldn't turn down a Pull Request.

# TODO

* Add metrics?  (Prometheus?)
* Dockerize and publish this into Docker Hub, making it easy(ier) for others to integrate and build off of (related to adding Prometheus metrics)
* Allow signaling via HUP to reload the config
* Instead-of the hard-kill that occurs now when you CTRL-C, allow catching of signals to parent thread and (optionally?) pass down into threads
* Add detection of duplication of execution of this script.  Shouldn't be able to run twice (in the same folder/config?)
* Add ability to query/tweak/restart a specific child process (similar to supervisor_ctl commands) and leave the others untouched
* Make "before/after" also support a date and datetime format instead of just an "hour before/after", detect the format and use accordingly
* Others / Profit ???

# DONE

* (FINALLY) Published the code as Open Source Software on Github after many years of it laying around
* Documented and cleaned up the codebase, added this awesome readme
* Integrated the max_runtime feature directly into the codebase instead of being an (annoying) helper script
* Making a few variables configurable via env vars making it easier to Dockerize

# History

This codebase in some form has been used in about a dozen companies over the last 10 years.  I've iterated on it and tweaked it over time, it currently proudly powers a few larger website's background task engines with ~40+ tasks running/scheduled concurrently with a ridiculous uptime.  I've been meaning to open-source it forever, it's basically "been" open source already just not published.  But finally!

# Support

Please file [issues on Github](https://github.com/DevOps-Nirvana/threaded-cron-task-engine/issues) or email me at _farley_ --AT-- **neonsurge** _dot_ COM.  I can be found on Github called [AndrewFarley](http://github.com/andrewfarley) but my legal name is Farley now.   