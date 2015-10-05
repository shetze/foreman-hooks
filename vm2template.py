#! /usr/bin/python

# vm2template is a foreman_hook to automate creation of RHEV templates out of a freshly provisioned VM
# although counter intuitive, this task should not be triggered as a create hook, because create is fired right at the beginning of the creation.
# it should better be used as an after_provision hook

# To get best results with this hook, the VM sould be sealed before it is converted

import json
import sys
import syslog
import time
from datetime import datetime
from ovirtsdk.xml import params
from ovirtsdk.api import API

rhevm = 'https://rhevm.example.com:443'
user = 'admin@internal'
passwd = 'Confidential'

lookupkey = "vm_template_image"

def search(list, key, value):
  for item in list:
    if item[key] == value:
      return item
  return {}

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

#! /usr/bin/python

# vm2template is a foreman_hook to automate creation of RHEV templates out of a freshly provisioned VM
# although counter intuitive, this task should not be triggered as a create hook, because create is fired right at the beginning of the creation.
# it should better be used as an after_provision hook

# To get best results with this hook, the VM sould be sealed before it is converted

import json
import sys
import syslog
import time
from datetime import datetime
from ovirtsdk.xml import params
from ovirtsdk.api import API

rhevm = 'https://rhevm.lunetix.org:443'
user = 'admin@internal'
passwd = 'Phei7EiN'

lookupkey = "vm_template_image"

def search(list, key, value):
  for item in list:
    if item[key] == value:
      return item
  return {}

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

# Here we check if his VM has the host parameter (lookupkey) set to 'true'.
# If this is not the case, we do not want this VM to become a template and exit here.
if not value == 'true':
  exit(0)

# now we need to talk to RHEV-M in order to to our job
api = API(url=rhevm,username=user,password=passwd,insecure=True)
syslog.openlog('FOREMAN_HOOKS',0,syslog.LOG_LOCAL0)


# The hook is triggered while the VM is still running, so we wait until it changes state...
state = 'up'
grace = 3
while state == 'up':
  time.sleep(5)
  vm = api.vms.get(id=uuid)
  if vm:
    state = vm.status.state
    logline = "vm2template waiting for %s uuid: %s to shut down state: %s" % (hostname, uuid, state)
  else:
    logline = "vm2template waiting for %s uuid: %s to shut down state: unknown" % (hostname, uuid)
  syslog.syslog(logline)
  if grace == 0:
    break
  grace = grace-1

time.sleep(5)
# ...then we wait until it is shut down.
while state != 'down':
  time.sleep(5)
  vm = api.vms.get(id=uuid)
  if vm:
    vm.stop()
    state = vm.status.state
    logline = "vm2template waiting for %s uuid: %s to power off state: %s" % (hostname, uuid, state)
  else:
    logline = "vm2template waiting for %s uuid: %s to power off state: unknown" % (hostname, uuid)
  syslog.syslog(logline)

# finally, we create the new template from this VM
time.sleep(5)
vm = api.vms.get(id=uuid)
state = vm.status.state
logline = "vm2template creating template from %s uuid: %s state: %s" % (hostname, uuid, state)
syslog.syslog(logline)
dt = datetime.now()
timestamp = dt.strftime("%y%m%d%H")
name = "rhel7baseline%s" % (timestamp)
vm = api.vms.get(id=uuid)
template = params.Template(name=name,vm=vm)
api.templates.add(template)

exit(0)
