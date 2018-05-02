#!/usr/bin/env python

"""
This script prints the difference between the jobs defined in devtools cico yaml
(JJB_URL) and those defined in Jenkins (JENKINS_JOBS_URL).

Usage:

    ./jenkins-jobs-diff.py [jjb_index]

If jjb_index is not supplied, it will connect to JJB_URL. Note that
jjb_file can be a URL (make sure it's RAW in case of GH) or a path.

Requirements:

    pip install jenkins-job-builder==1.6.1
"""

import ast
import urllib2
import yaml
import json
import sys
import os

from jenkins_jobs.builder import Builder

JENKINS_JOBS_URL = 'https://ci.centos.org/view/Devtools/api/python'
JJB_URL = 'https://raw.githubusercontent.com/openshiftio/openshiftio-cico-jobs/master/devtools-ci-index.yaml'
UNTRACKED_JOBS = set(['devtools-jjb-service'])

def get_jjb_jobs(jjb_fp):
    builder = Builder("None", None, None, None, plugins_list={})

    builder.load_files(jjb_fp)
    builder.parser.expandYaml()
    builder.parser.generateXML()

    return [job.name for job in builder.parser.xml_jobs]


def get_jenkins_jobs(url):
    jenkins_jobs = ast.literal_eval(urllib2.urlopen(url).read())

    return [job['name'] for job in jenkins_jobs['jobs']]


def main():
    if len(sys.argv) > 1:
        jjb_index = sys.argv[1]
    else:
        jjb_index = JJB_URL

    if jjb_index.startswith('http'):
        jjb_fp = urllib2.urlopen(jjb_index)
    else:
        jjb_fp = open(jjb_index, 'r')

    jjb_jobs = get_jjb_jobs(jjb_fp)
    jenkins_jobs = get_jenkins_jobs(JENKINS_JOBS_URL)

    jjb_not_jenkins = set(jjb_jobs) - set(jenkins_jobs) - UNTRACKED_JOBS
    jenkins_not_jjb = set(jenkins_jobs) - set(jjb_jobs) - UNTRACKED_JOBS

    diff = {}
    if jjb_not_jenkins:
        diff["in_jjb_not_in_jenkins"] = list(jjb_not_jenkins)
    if jenkins_not_jjb:
        diff["in_jenkins_not_in_jjb"] = list(jenkins_not_jjb)

    if os.environ.get('OUTPUT') == "json":
        print json.dumps(diff)
    else:
        print yaml.dump(diff, default_flow_style=False)

if __name__ == '__main__':
    main()
