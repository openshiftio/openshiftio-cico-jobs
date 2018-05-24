#!/usr/bin/env python

"""
This script prints the difference between the jobs defined in devtools cico yaml
(JJB_URL) and those defined in Jenkins (JENKINS_JOBS_URL).

Usage:

    ./jenkins-jobs-diff.py [new_index] [old_index]

If new_index is not supplied, it will connect use the current version of the index:
https://github.com/openshiftio/openshiftio-cico-jobs/blob/master/devtools-ci-index.yaml

Note that the index be a URL (make sure it's RAW in case of GH) or a path.

If old_index is not supplied, it will query jenkins for the list of defined
jobs. If it is supplied, it can be a URL or a path.

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

def get_jjb_jobs(index_raw):
    if index_raw.startswith('http'):
        index_fp = urllib2.urlopen(index_raw)
    else:
        index_fp = open(index_raw, 'r')

    builder = Builder("None", None, None, None, plugins_list={})

    builder.load_files(index_fp)
    builder.parser.expandYaml()
    builder.parser.generateXML()

    index_fp.close()

    return [job.name for job in builder.parser.xml_jobs]

def get_jenkins_jobs(url):
    jenkins_jobs = ast.literal_eval(urllib2.urlopen(url).read())

    return [job['name'] for job in jenkins_jobs['jobs']]

def main():
    old_index_yaml = None

    if len(sys.argv) == 2:
        new_index_yaml = sys.argv[1]
    elif len(sys.argv) == 3:
        new_index_yaml = sys.argv[1]
        old_index_yaml = sys.argv[2]
    else:
        new_index_yaml = JJB_URL

    new_jobs_list = get_jjb_jobs(new_index_yaml)

    if old_index_yaml:
        old_jobs_list = get_jjb_jobs(old_index_yaml)
    else:
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
