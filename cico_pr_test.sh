#!/usr/bin/bash

set -x

NEW_JOBS=$(mktemp -d)
MASTER_JOBS=$(mktemp -d)

DEVTOOLS_INDEX="devtools-ci-index.yaml"

delete_tmp() {
    rm -rf $NEW_JOBS $MASTER_JOBS
}

jenkins-jobs test $DEVTOOLS_INDEX -o $NEW_JOBS
ret=$?

if [ "$ret" != "0" ]; then
    delete_tmp
    exit $ret
fi

git show origin/master:$DEVTOOLS_INDEX | jenkins-jobs test -o $MASTER_JOBS
echo "-------------------------------------------------------------------------"
diff -uNr $MASTER_JOBS $NEW_JOBS
echo "-------------------------------------------------------------------------"
diff -qr $MASTER_JOBS $NEW_JOBS
echo "-------------------------------------------------------------------------"

delete_tmp

# Check if job list is empty
JOB_LIST=$(scripts/jenkins-jobs-diff.py $DEVTOOLS_INDEX)

if echo "$JOB_LIST" | grep -q 'in_jenkins_not_in_devtools'; then
    echo "ERROR: Jobs in jenkins not in the devtools index:"
    echo "$JOB_LIST"
    echo
    echo "====================================================================="
    echo "Stopping the execution because some Jobs have not been deleted"
    echo "from ci.centos.org. Please ask a Jenkins admin to remove them, and"
    echo "this test will succeed."
    echo "====================================================================="
    exit 1
fi

exit 0
