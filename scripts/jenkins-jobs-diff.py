#!/usr/bin/env python

"""
This script prints the difference between the jobs received by STDIN Jenkins
(JENKINS_JOBS_URL).

Usage:

    echo job1 job2 ... | ./jenkins-jobs-diff.py
"""

import ast
import urllib2
import yaml
import json
import sys
import os


JENKINS_JOBS_URL = 'https://ci.centos.org/view/Devtools/api/python'
UNTRACKED_JOBS = set(['devtools-jjb-service'])


def get_jenkins_jobs(url):
    """
    Returns an array with job names. It connects to jenkins to get the list of jobs.
    """
    jenkins_jobs = ast.literal_eval(urllib2.urlopen(url).read())

    return [job['name'] for job in jenkins_jobs['jobs']]


def main():
    new_jobs_list = sys.stdin.read().split()
    old_jobs_list = get_jenkins_jobs(JENKINS_JOBS_URL)

    new_jobs = set(new_jobs_list) - set(old_jobs_list) - UNTRACKED_JOBS
    removed_jobs = set(old_jobs_list) - set(new_jobs_list) - UNTRACKED_JOBS

    diff = {}
    if new_jobs:
        diff["new_jobs"] = list(new_jobs)
    if removed_jobs:
        diff["removed_jobs"] = list(removed_jobs)

    if os.environ.get('OUTPUT') == "json":
        print json.dumps(diff)
    else:
        print yaml.dump(diff, default_flow_style=False)


if __name__ == '__main__':
    main()
