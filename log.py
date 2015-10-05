#! /usr/bin/python

import json
import sys
import syslog
from datetime import datetime

def search(list, key, value):
  for item in list:
    if item[key] == value:
      return item
  return {}

lookupkey = "vm_template_image"

# get event from command line args
if len(sys.argv)>1:
  event = sys.argv[1]
else:
  event = 'unknown'

# read json object from STDIN and digest information
data = json.loads(sys.stdin.read())
hostname = data['host']['name']
uuid = data['host']['uuid']
mac = data['host']['mac']
parameter = {}
value = 'undefined'
if 'parameters' in data['host']:
  parameter = search(data['host']['parameters'],'name',lookupkey)
if 'value' in parameter:
  value = parameter['value']

# 
if not hostname.startswith('rhel'):
  exit(0)

logline = "received %s on managed %s uuid: %s %s: %s" % (event, hostname, uuid, lookupkey, value)

dt = datetime.now()
timestamp = dt.strftime("%y%m%d%H%M%S%f")

dumpname = "/var/log/foreman-hooks/foreman_hook.%s" % (timestamp)
dumpfile = open(dumpname,'w')
dumpfile.write(logline)
dumpfile.write('\n\n')
json.dump(data,dumpfile,sort_keys=True, indent=4)
dumpfile.close()

syslog.openlog('FOREMAN_HOOKS',0,syslog.LOG_LOCAL0)
syslog.syslog(logline)
exit(0)
