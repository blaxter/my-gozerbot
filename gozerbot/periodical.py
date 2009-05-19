# JobInterval scheduler
# (c) Wijnand 'tehmaze' Modderman - http://tehmaze.com
# BSD License

# gozerbot imports
from generic import calledfrom, lockdec, rlog, strtotime, handle_exception
import threads.thr as thr

# basic imorts
import datetime, sys, time, thread, types

# locks and vars
plock    = thread.allocate_lock()
locked   = lockdec(plock)
pidcount = 0

class JobError(Exception):

    """ job error exception. """

    pass

class Job(object):

    """ job to be scheduled. """

    group = ''
    pid   = -1

    def __init__(self):
        global pidcount
        pidcount += 1
        self.pid = pidcount

    def id(self):

        """ return job id. """

        return self.pid

    def member(self, group):

        """ check for group membership. """

        return self.group == group

class JobAt(Job):

    """ job to run at a specific time/interval/repeat. """

    def __init__(self, start, interval, repeat, func, *args, **kw):
        Job.__init__(self)
        self.func = func
        self.args = args
        self.kw = kw
        self.repeat = repeat
        self.description = ""
        self.counts = 0

        # check start time format
        if type(start) in [types.IntType, types.FloatType]:
            self.next = float(start)
        elif type(start) in [types.StringType, types.UnicodeType]:
            d = strtotime(start)
            if d and d > time.time():
                self.next = d
            else:
                raise JobError("invalid date/time")

        if type(interval) in [types.IntType]:
            d = datetime.timedelta(days=interval)
            self.delta = d.seconds
        else:
            self.delta = interval

    def __repr__(self):

        """ return a string representation of the JobAt object. """

        return '<JobAt instance next=%s, interval=%s, repeat=%d, function=%s>' % (str(self.next),
            str(self.delta), self.repeat, str(self.func))

    def check(self):

        """ run check to see if job needs to be scheduled. """

        if self.next <= time.time():
            rlog(-15, 'periodical', 'running %s' % str(self.func))
            self.func(*self.args, **self.kw)
            self.next += self.delta
            self.counts += 1
            if self.repeat > 0 and self.counts >= self.repeat:
                return False # remove this job
        return True

class JobInterval(Job):

    """ job to be scheduled at certain interval. """

    def __init__(self, interval, repeat, func, *args, **kw):
        Job.__init__(self)
        self.func = func
        self.args = args
        self.kw = kw
        self.repeat = int(repeat)
        self.counts = 0
        self.interval = float(interval)
        self.description = ""
        self.next = time.time() + self.interval
        self.group = None
        rlog(-10, 'periodical', 'scheduled next run of %s in %d seconds' % \
(str(self.func), self.interval))

    def __repr__(self):
        return '<JobInterval instance next=%s, interval=%s, repeat=%d, group=%s, \
function=%s>' % (str(self.next), str(self.interval), self.repeat, self.group,
str(self.func))

    def check(self):

        """ run check to see if job needs to be scheduled. """

        if self.next <= time.time():
            rlog(-15, 'periodical', 'running %s' % (str(self.func)))
            self.next = time.time() + self.interval

            # try the callback
            try:
                self.func(*self.args, **self.kw)
            except Exception, ex:
                handle_exception()

            self.counts += 1
            if self.repeat > 0 and self.counts >= self.repeat:
                return False # remove this job
        return True

class Periodical(object):

    """ periodical scheduler. """

    SLEEPTIME = 1 # smallest interval possible

    def __init__(self):
        self.jobs = []
        self.run = True

    def start(self):

        """ start the periodical scheduler. """

        thr.start_new_thread(self.checkloop, ())

    def addjob(self, sleeptime, repeat, function, description="" , *args, **kw): 

        """ add a periodical job. """

        job = JobInterval(sleeptime, repeat, function, *args, **kw)
        job.group = calledfrom(sys._getframe())
        job.description = str(description)
        self.jobs.append(job)
        return job.pid

    def changeinterval(self, pid, interval):
 
        """ change interval of of peridical job. """

        for i in periodical.jobs:
            if i.pid == pid:
                i.interval = interval
                i.next = time.time() + interval

    def checkloop(self):

        """ main loop of the periodical scheduler. """

        while self.run:
            for job in self.jobs:
                if job.next <= time.time():
                    thr.start_new_thread(self.runjob, (job, ))
            time.sleep(self.SLEEPTIME)

    def runjob(self, job):

        """ kill job is not to be runned. """

        if not job.check():
            self.killjob(job.id())

    def kill(self):

        ''' kill all jobs invoked by another module. '''

        group = calledfrom(sys._getframe())
        self.killgroup(group)

    def killgroup(self, group):

        ''' kill all jobs with the same group. '''

        @locked
        def shoot():

            """ knock down all jobs belonging to group. """

            deljobs = [job for job in self.jobs if job.member(group)]
            for job in deljobs:
                self.jobs.remove(job)
            rlog(5, 'periodical', 'killed %d jobs for %s' % (len(deljobs), \
group))
            del deljobs
        shoot() # *pow* you're dead ;)

    def killjob(self, jobId):

        ''' kill one job by its id. '''

        @locked
        def shoot():
            deljobs = [x for x in self.jobs if x.id() == jobId]
            numjobs = len(deljobs)
            for job in deljobs:
                self.jobs.remove(job)
            del deljobs
            return numjobs

        return shoot() # *pow* you're dead ;)

# the periodical scheduler
periodical = Periodical()


def interval(sleeptime, repeat=0):

    """ interval decorator. """

    group = calledfrom(sys._getframe())

    def decorator(function):
        decorator.func_dict = function.func_dict

        def wrapper(*args, **kw):
            job = JobInterval(sleeptime, repeat, function, *args, **kw)
            job.group = group
            periodical.jobs.append(job)
            rlog(-15, 'periodical', 'new interval job %d with sleeptime %d' % \
(job.id(), sleeptime))

        return wrapper

    return decorator

def at(start, interval=1, repeat=1):

    """ at decorator. """

    group = calledfrom(sys._getframe())

    def decorator(function):
        decorator.func_dict = function.func_dict

        def wrapper(*args, **kw):
            job = JobAt(start, interval, repeat, function, *args, **kw)
            job.group = group
            periodical.jobs.append(job)

        wrapper.func_dict = function.func_dict
        return wrapper

    return decorator

def minutely(function):

    """ minute decorator. """

    minutely.func_dict = function.func_dict
    group = calledfrom(sys._getframe())

    def wrapper(*args, **kw):
        job = JobInterval(60, 0, function, *args, **kw)
        job.group = group
        periodical.jobs.append(job)
        rlog(-15, 'periodical', 'new interval job %d running minutely' % \
job.id())

    return wrapper

def hourly(function):

    """ hour decorator. """

    rlog(-15, 'periodical', '@hourly(%s)' % str(function))
    hourly.func_dict = function.func_dict
    group = calledfrom(sys._getframe())

    def wrapper(*args, **kw):
        job = JobInterval(3600, 0, function, *args, **kw)
        job.group = group
        rlog(-15, 'periodical', 'new interval job %d running hourly' % job.id())
        periodical.jobs.append(job)

    return wrapper

def daily(function):

    """ day decorator. """

    rlog(-15, 'periodical', '@daily(%s)' % str(function))
    daily.func_dict = function.func_dict
    group = calledfrom(sys._getframe())

    def wrapper(*args, **kw):
        job = JobInterval(86400, 0, function, *args, **kw)
        job.group =  group
        periodical.jobs.append(job)
        rlog(-15, 'periodical', 'new interval job %d running daily' % job.id())

    return wrapper
