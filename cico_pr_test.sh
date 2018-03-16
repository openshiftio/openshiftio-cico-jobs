#!/usr/bin/bash

set -x

NEW_JOBS=$(mktemp -d)
MASTER_JOBS=$(mktemp -d)

delete_tmp() {
    rm -rf $NEW_JOBS $MASTER_JOBS
}

jenkins-jobs test devtools-ci-index.yaml -o $NEW_JOBS
ret=$?

if [ "$ret" != "0" ]; then
    delete_tmp
    exit $ret
fi

git show origin/master:devtools-ci-index.yaml | jenkins-jobs test -o $MASTER_JOBS

diff -uNr $MASTER_JOBS $NEW_JOBS

delete_tmp

exit 0
