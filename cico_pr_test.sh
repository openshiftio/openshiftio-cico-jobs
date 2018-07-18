#!/usr/bin/bash

set -x

NEW_JOBS=$(mktemp -d)
MASTER_JOBS=$(mktemp -d)

JJB_INDEX="devtools-ci-index.yaml"
JENKINS_JOBS="~/venv/env/bin/jenkins-jobs"

delete_tmp() {
    rm -rf $NEW_JOBS $MASTER_JOBS
}

$JENKINS_JOBS test --config-xml $JJB_INDEX -o $NEW_JOBS
ret=$?

if [ "$ret" != "0" ]; then
    delete_tmp
    exit $ret
fi

git show origin/master:$JJB_INDEX | $JENKINS_JOBS test --config-xml -o $MASTER_JOBS

set +x

echo
echo "-------------------------------------------------------------------------"
echo diff -uNr '$MASTER_JOBS' '$NEW_JOBS'
echo diff -uNr $MASTER_JOBS $NEW_JOBS
echo
diff -uNr $MASTER_JOBS $NEW_JOBS
echo "-------------------------------------------------------------------------"
echo diff -qr '$MASTER_JOBS' '$NEW_JOBS'
echo diff -qr $MASTER_JOBS $NEW_JOBS
echo
diff -qr $MASTER_JOBS $NEW_JOBS
echo "-------------------------------------------------------------------------"
echo "Credential changes:"
echo
SED_EXPR='s/^.*>\(.*\)<.*$/\1/'
grep -rh credentialsId $MASTER_JOBS|sed "$SED_EXPR"|sort -u > $MASTER_JOBS/old_creds.txt
grep -rh credentialsId $NEW_JOBS|sed "$SED_EXPR"|sort -u > $NEW_JOBS/new_creds.txt
diff -U0 $MASTER_JOBS/old_creds.txt $NEW_JOBS/new_creds.txt
echo "-------------------------------------------------------------------------"

delete_tmp

# Check if job list is empty
JOB_DIFF=$(scripts/jenkins-jobs-diff.py $JJB_INDEX 2>/dev/null)

echo
echo "JOB_DIFF:"
echo "$JOB_DIFF"

if echo "$JOB_DIFF" | grep -q 'removed_jobs'; then
    echo
    echo "====================================================================="
    echo "ERROR: Found jobs defined in jenkins but not in the devtools jjb index."
    echo "Stopping the execution because some Jobs have not been deleted"
    echo "from ci.centos.org. Please ask a Jenkins admin to remove them, and"
    echo "this test will succeed."
    echo "====================================================================="
    exit 1
fi

exit 0
