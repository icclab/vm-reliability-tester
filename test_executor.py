# -*- coding: utf-8 -*-
"""
Created on Wed Feb 04 16:42:43 2015

@author: Konstantin
"""

import configparser, os
from fabric.api import env, execute, task
import cuisine
import vm_control

@task
def upload_file(remote_location, local_location, sudo=False):
    cuisine.file_upload(remote_location, local_location, sudo=sudo)
    cuisine.file_ensure(remote_location)

@task
def run_python_program(program=None, sudo=False):
    cuisine.file_ensure('/usr/bin/python')
    if sudo:
        cuisine.sudo(('/usr/bin/python %s' % program))
    else:
        cuisine.run(('/usr/bin/python %s' % program))

def run():
    execfile('openrc.py')
    print os.environ['OS_USERNAME']
    config = configparser.ConfigParser()
    config.read('config.ini')
    print(config.sections())

    vm_credentials = dict(config['SSH_CREDENTIALS'])
    ssh_username = str(vm_credentials['ssh.username'])
    ssh_password = str(vm_credentials['ssh.password'])
    ssh_key_filename = str(vm_credentials['ssh.key_filename'])
        
    VM_control = vm_control.VM_Control()
    ssh_url = VM_control.get_floating_ip('master')
    
    env.hosts = [ssh_url]
    env.user = ssh_username
    env.password = ssh_password
    env.key_filename = ssh_key_filename
    env.connection_attempts = 5
    
#    execute(upload_file,'/root/test_runner.py','test_runner.py',sudo=True) 
    execute(run_python_program, program='/root/test_runner.py')

if __name__ == "__main__":       
    execfile('openrc.py')
    print os.environ['OS_USERNAME']
    config = configparser.ConfigParser()
    config.read('config.ini')
    print(config.sections())

    vm_credentials = dict(config['SSH_CREDENTIALS'])
    ssh_username = str(vm_credentials['ssh.username'])
    ssh_password = str(vm_credentials['ssh.password'])
    ssh_key_filename = str(vm_credentials['ssh.key_filename'])
        
    vm_control = vm_control.VM_Control()
    ssh_url = vm_control.get_floating_ip('master')
    
    env.hosts = [ssh_url]
    env.user = ssh_username
    env.password = ssh_password
    env.key_filename = ssh_key_filename
    env.connection_attempts = 5
    
#    execute(upload_file,'/root/test_runner.py','test_runner.py',sudo=True) 
    execute(run_python_program, program='/root/test_runner.py')
