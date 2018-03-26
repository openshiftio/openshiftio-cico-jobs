#!/usr/bin/env python

"""
This script prints the difference between the jobs defined in devtools cico yaml
(DEVTOOLS_URL) and those defined in Jenkins (JENKINS_JOBS_URL).

Usage:

    ./jenkins-jobs-diff.py [devtools_index]

If devtools_index is not supplied, it will connect to DEVTOOLS_URL. Note that
devtools_file can be a URL (make sure it's RAW in case of GH) or a path.

Requirements:

    pip install jenkins-job-builder==1.6.1
"""

import ast
import urllib2
import yaml
import sys

from jenkins_jobs.builder import Builder

JENKINS_JOBS_URL = 'https://ci.centos.org/view/Devtools/api/python'
DEVTOOLS_URL = 'https://raw.githubusercontent.com/openshiftio/openshiftio-cico-jobs/master/devtools-ci-index.yaml'
UNTRACKED_JOBS = set(['devtools-jjb-service'])

def get_devtools_jobs(devtools_fp):
    builder = Builder("None", None, None, None, plugins_list={})

    builder.load_files(devtools_fp)
    builder.parser.expandYaml()
    builder.parser.generateXML()

    return [job.name for job in builder.parser.xml_jobs]


def get_jenkins_jobs(url):
    jenkins_jobs = ast.literal_eval(urllib2.urlopen(url).read())

    return [job['name'] for job in jenkins_jobs['jobs']]


def main():
    if len(sys.argv) > 1:
        devtools_index = sys.argv[1]
    else:
        devtools_index = DEVTOOLS_URL

    if devtools_index.startswith('http'):
        devtools_fp = urllib2.urlopen(devtools_index)
    else:
        devtools_fp = open(devtools_index, 'r')

    devtools_jobs = get_devtools_jobs(devtools_fp)
    jenkins_jobs = get_jenkins_jobs(JENKINS_JOBS_URL)

    devtools_not_jenkins = set(devtools_jobs) - set(jenkins_jobs) - UNTRACKED_JOBS
    jenkins_not_devtools = set(jenkins_jobs) - set(devtools_jobs) - UNTRACKED_JOBS

    diff = {}
    if devtools_not_jenkins:
        diff["in_devtools_not_in_jenkins"] = list(devtools_not_jenkins)
    if jenkins_not_devtools:
        diff["in_jenkins_not_in_devtools"] = list(jenkins_not_devtools)

    print yaml.dump(diff, default_flow_style=False)

if __name__ == '__main__':
    main()
