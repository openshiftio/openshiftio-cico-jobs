#!/usr/bin/env python

"""
This script prints the difference between the jobs defined in devtools cico yaml
(JJB_URL) and those defined in Jenkins (JENKINS_JOBS_URL).

Usage:

    ./jenkins-jobs-diff.py [new_index_yaml]

If new_index_yaml is not supplied, it will connect to JJB_URL. Note that
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
        new_index_yaml = sys.argv[1]
    else:
        new_index_yaml = JJB_URL

    if new_index_yaml.startswith('http'):
        new_index = urllib2.urlopen(new_index_yaml)
    else:
        new_index = open(new_index_yaml, 'r')

    new_jobs_list = get_jjb_jobs(new_index)
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
