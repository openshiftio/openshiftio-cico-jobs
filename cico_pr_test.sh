#!/usr/bin/bash

set -ex

NEW_JOBS=$(mktemp -d)
MASTER_JOBS=$(mktemp -d)

jenkins-jobs test devtools-ci-index.yaml -o $NEW_JOBS

git show origin/master:devtools-ci-index.yaml | jenkins-jobs test -o $MASTER_JOBS

diff -uNr $MASTER_JOBS $NEW_JOBS
rm -rf $MASTER_JOBS $NEW_JOBS
