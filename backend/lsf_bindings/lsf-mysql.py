#!/usr/bin/python
# This file is an adaptation of the work at https://github.com/passrafi/lsf-stats/
# User passrafi's files are intended as a guide to use the Python LSF API, no rip off intended.
# With their permission, all code is now under MIT license:
# https://github.com/passrafi/lsf-stats/issues/2
#
# Copyright (c) 2015 Zachary Giles
# The MIT License (MIT)

from pythonlsf import lsf
from pythonlsf.lsf import submit as jobRequest
from pythonlsf.lsf import submitReply as jobReply
import json
import time
import copy
import MySQLdb
import re

# not quite at the params file level yet...
db_host = 'db1.example.local'
db_username = 'lsfstats'
db_password = 'lsfstats'
db_dbname = 'lsfstats'

now = int(time.time())

_copied_attributes_ = {
    'avgMem':'mem_avg',
    'cpuTime':'cputime',
    'endTime':'end_time',
    'exitInfo':'exit_info',
    'exitStatus':'exit_status',
    'jobId':'id',  
    'jobPriority':'job_priority',
    'maxMem':'mem_max',
    'runTime':'run_time',
    'startTime':'start_time',
    'status':'status',
    'submitTime':'submit_time',
    'user':'user',
    'numExHosts':'numExHosts',
}
    
DEFAULT_FEATURES = ['total_jobs','pending_jobs','running_jobs','hosts/processers','threads','mem','mem_avg','pending_time_avg','pending_time']
_all = 'all_users'

class JobInfo ():
    
    def _copy_submit_(self,lsf_job):
        self.__dict__['name']=lsf_job.submit.jobName
        self.__dict__['project_name']=lsf_job.submit.projectName
        self.__dict__['queue']=lsf_job.submit.queue
        self.__dict__['command']=lsf_job.submit.command
        self.__dict__['resreq']=lsf_job.submit.resReq
        self.__dict__['out_file']=lsf_job.submit.outFile
        self.__dict__['err_file']=lsf_job.submit.errFile
        self.__dict__['user_priority']=lsf_job.submit.userPriority
        self.__dict__['mail_user']=lsf_job.submit.mailUser
        self.__dict__['run_limits']= {
                'cpu_time'     : lsf_job.submit.rLimits[0], #in ms
                'file_size'    : lsf_job.submit.rLimits[1],
                'data_size'    : lsf_job.submit.rLimits[2],
                'open_files'   : lsf_job.submit.rLimits[6],
                'swap_mem'     : lsf_job.submit.rLimits[8],
                'wall_time'    : lsf_job.submit.rLimits[9], #in seconds
                'processes'    : lsf_job.submit.rLimits[10],
                'threads '     : lsf_job.submit.rLimits[11],
                                     }

    def _copy_rusage_(self,lsf_job):
	self.__dict__['runRusage']= {
		'mem':		copy.deepcopy(lsf_job.runRusage.mem),
		'nthreads':	copy.deepcopy(lsf_job.runRusage.nthreads),
		'utime': 	copy.deepcopy(lsf_job.runRusage.utime)
		}

    _specially_copied_attributes_ = {'submit':_copy_submit_, 'runRusage':_copy_rusage_}
    
    #Job related information
    def __init__(self, lsf_job):
        for lsf_job_attribute, self_attribute in _copied_attributes_.iteritems():
            self.__dict__[self_attribute] = lsf_job.__getattribute__(lsf_job_attribute)
        for lsf_job_attribute, self_callback in self._specially_copied_attributes_.iteritems():
            self_callback(self,lsf_job)

def init():
    lsf.lsb_init('lsfstats')

def get_job_info(job_id=0L, job_name=None, user_name=None, queue_name=None, host_name=None, options=0 ):
    '''a wrapper for c lsf api: 
       int lsb_openjobinfo(
       LS_LONG_INT jobId, 
       char *jobName, 
       char *userName, 
       char *queueName, 
       char *hostName, 
       int options) '''
    if user_name == None:
        user_name = lsf.ALL_USERS
    if options == 0:
        options = lsf.ALL_JOB

    count = lsf.lsb_openjobinfo(job_id, job_name, user_name, queue_name, host_name, options)
    jobs = read_all_jobs(count)
    lsf.lsb_closejobinfo()
    return jobs

def get_all_job_info():
    return get_job_info()

def read_all_jobs(count):
    jobs = []
    more = lsf.new_intp()
    while count > 0:
        jobp = lsf.lsb_readjobinfo(more)
        #create a copy of data
        job = JobInfo(jobp)
        jobs.append(job)
        count = lsf.intp_value(more)
    lsf.delete_intp(more)
    return jobs

def lsf_stats():
    jobs = get_all_job_info()
    user_stats = {}
    feature_stats = {}
    feature_stats['total_jobs']       = {'title':'Total Jobs','unit':'','users':{}}
    feature_stats['pending_jobs']     = {'title':'Pending Jobs','unit':'','users':{}}
    feature_stats['running_jobs']     = {'title':'Running Jobs','unit':'','users':{}}
    feature_stats['hosts/processers'] = {'title':'Processors','unit':'','users':{}}
    feature_stats['threads']          = {'title':'Threads','unit':'','users':{}}
    feature_stats['mem']              = {'title':'Instantaneous Memory Usage','unit':'GB','users':{}}
    feature_stats['mem_avg']          = {'title':'Average Memory Usage','unit':'GB','users':{}}
    feature_stats['pending_time_avg'] = {'title':'Average Waiting Time of Pending Jobs','unit':'min','users':{}}
    feature_stats['pending_time']     = {'title':'Total Waiting Time of Pending Jobs','unit':'s','users':{}}

    def create_user(user_stats, feature_stats, name):
        user_stats[name] = {}
        user_stats[name]['total_jobs'] = 0
        feature_stats['total_jobs']['users'][name] = 0
        user_stats[name]['pending_jobs'] = 0
        feature_stats['pending_jobs']['users'][name] = 0
        user_stats[name]['pending_time_avg'] = 0
        feature_stats['pending_time_avg']['users'][name] = 0
        user_stats[name]['running_jobs'] = 0
        feature_stats['running_jobs']['users'][name] = 0
        user_stats[name]['hosts/processers'] = 0
        feature_stats['hosts/processers']['users'][name] = 0
        user_stats[name]['threads'] = 0
        feature_stats['threads']['users'][name] = 0
        user_stats[name]['mem'] = 0
        feature_stats['mem']['users'][name] = 0
        user_stats[name]['mem_avg'] = 0
        feature_stats['mem_avg']['users'][name] = 0
        user_stats[name]['pending_time'] = 0
        feature_stats['pending_time']['users'][name] = 0
        
    create_user(user_stats, feature_stats, _all)
   
    def increment(feature_name, user, N=1):
        user_stats[_all][feature_name] = user_stats[_all][feature_name] + N
        feature_stats[feature_name]['users'][_all] = feature_stats[feature_name]['users'][_all] + N
        user_stats[user][feature_name] = user_stats[user][feature_name] + N
        feature_stats[feature_name]['users'][user] = feature_stats[feature_name]['users'][user] + N

    def pending_time_avg_min(name):
        new_avg = user_stats[_all]['pending_time'] / user_stats[_all]['pending_jobs'] / 60
        user_stats[_all]['pending_time_avg'] = int(new_avg)
        feature_stats['pending_time_avg']['users'][_all] = int(new_avg)
        
        new_avg = user_stats[name]['pending_time'] / user_stats[name]['pending_jobs'] / 60
        user_stats[name]['pending_time_avg'] = int(new_avg)
        feature_stats['pending_time_avg']['users'][name] = int(new_avg)

    for job in jobs:
        if job.user not in user_stats:
            create_user(user_stats,feature_stats,job.user)
        increment('total_jobs',job.user)
        if job.status == 1:
            #job is pending
            #if job is pending more that two weeks, ignore it
            if (time.time() - job.submit_time) < 1209600:
                increment('pending_jobs',job.user)
                increment('pending_time',job.user, int((time.time() - job.submit_time)))
                pending_time_avg_min(job.user)
        elif job.status ==4:
            #running jobs
            increment('running_jobs',job.user)
            increment('hosts/processers',job.user,job.numExHosts)
            increment('threads',job.user,job.runRusage['nthreads'])
            increment('mem',job.user,int(job.runRusage['mem']))
            increment('mem_avg', job.user, int(job.mem_avg))
    
    if not user_stats:
        return None
    return user_stats, feature_stats, jobs 

def getmemfromrusage(rusageline):
  mem = re.search('(?<=mem=)([0-9]+)',rusageline)
  if mem:
    if mem.group(0):
       return mem.group(0)
    else:
       return 0
  else:
    return 0
  return 0

def mysql_stats(user_stats, feature_stats, job_stats, features, all=True):
    unselected_features = copy.deepcopy(DEFAULT_FEATURES)
    for feature in features:
        if feature in unselected_features: unselected_features.remove(feature)
    for unselected_feature in unselected_features:
        feature_stats.pop(unselected_feature,None)
    try:
	db = MySQLdb.connect(host=db_host, user=db_username, passwd=db_password, db=db_dbname)
	cur = db.cursor()
	for job in job_stats:
		query = "INSERT INTO jobs (id, jobid, timestamp, user, submit_time, start_time, end_time, run_time, exit_status, cputime, status, resreq, project_name, queue, mem, mem_reservation, mem_avg, mem_max, cores) VALUES (NULL, " + str(job.__dict__['id']) + ", '" + str(now) + "', '" + str(job.__dict__['user']) + "', '" + str(job.__dict__['submit_time']) + "', '" + str(job.__dict__['start_time']) + "', '" + str(job.__dict__['end_time']) + "', '" + str(job.__dict__['run_time']) + "', '" + str(job.__dict__['exit_status']) + "', '" + str(job.__dict__['cputime']) + "', '" + str(job.__dict__['status']) + "', '" + db.escape_string(str(job.__dict__['resreq'])) + "', '" + str(job.__dict__['project_name']) + "', '" + str(job.__dict__['queue']) + "', '" + str(job.runRusage['mem']) + "', '" + str( int(getmemfromrusage(job.__dict__['resreq'])) * int(job.__dict__['numExHosts']) ) + "', '" + str(job.__dict__['mem_avg']) + "', '" + str(job.__dict__['mem_max']) + "', '" + str(job.__dict__['numExHosts']) + "')" 
		try:
			cur.execute(query)
		except:
			print "ERROR: ", query
			print query
		db.commit()
    except MySQLdb.Error, e:
	print "Error: %s" %e
	print query

    # Stage three. Summary table
    try:
	db = MySQLdb.connect(host=db_host, user=db_username, passwd=db_password, db=db_dbname)
	cur = db.cursor()
	query = "INSERT INTO summary (timestamp, mem, mem_reservation, mem_max, mem_avg, cores, pending_jobs, running_jobs, total_jobs, pending_time_avg) SELECT a.timestamp, a.mem, a.mem_reservation, a.mem_max, a.mem_avg, a.cores, b.pending_jobs, a.running_jobs, c.total_jobs, a.pending_time_avg FROM (SELECT timestamp as timestamp, sum(mem) as mem, sum(mem_reservation) as mem_reservation, sum(mem_max) as mem_max, sum(mem_avg)/count(mem_avg) as mem_avg, sum(cores) as cores, abs(sum(start_time-submit_time))/count(submit_time) as pending_time_avg, count(*) as running_jobs FROM jobs where status=4 and timestamp = " + str(now) + " group by timestamp order by timestamp desc) as a, (SELECT timestamp, count(*) as pending_jobs, abs(sum(submit_time)-(" + str(now) + "*count(submit_time)))/count(submit_time) as pending_time_avg  FROM jobs where status=1 and timestamp = " + str(now) + " group by timestamp order by timestamp desc) as b, (SELECT timestamp, count(*) as total_jobs FROM jobs where timestamp = " + str(now) + " group by timestamp order by timestamp desc) as c;"
	try:
		cur.execute(query)
	except:
		print "ERROR: ", query
		print query
	db.commit()
	
    except MySQLdb.Error, e:
	print "Error: %s" %e
	print query

def main():
    import argparse
    init()
    available_features = copy.deepcopy(DEFAULT_FEATURES)
    available_features.remove('pending_time')
    user_stats, feature_stats, job_stats = lsf_stats()
    mysql_stats(user_stats,feature_stats,job_stats,args.feature,all=True)
    return 0

if __name__ == "__main__":
    main()
