#!/bin/bash

set -xe

setenforce 0
yum -y install docker
systemctl start docker

make test
