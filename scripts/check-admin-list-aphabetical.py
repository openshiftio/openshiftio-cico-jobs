#!/usr/bin/env python

"""
Usage: python check-admin-list-aphabetical.py index_file

This script will exit 0 if the admin list is defined in alphabetical order.
"""

import yaml
import sys

with open(sys.argv[1], 'r') as f:
    index = yaml.load(f.read())

for elem in index:
    if 'admin_list_defaults' in elem:
        admin_list = [e.lower()
                      for e in elem['admin_list_defaults']['admin-list']]

        if sorted(admin_list) == admin_list:
            sys.exit(0)
        else:
            print >>sys.stderr, "Admin list not in alphabetical order."
            sys.exit(1)

raise Exception("Admin list could not be read")
