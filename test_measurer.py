# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 15:47:37 2015

@author: Konstantin
"""

import configparser, os, csv
from fabric.api import env, execute, task, get
import cuisine
import vm_control

@task
def upload_file(remote_location, local_location, sudo=False):
    cuisine.file_upload(remote_location, local_location, sudo=sudo)
    cuisine.file_ensure(remote_location)

@task
def collect_data_files(vm_list):
    i = 1
    for vm in vm_list:
        get('/home/ubuntu/failures.csv.'+vm,'failures_'+str(i)+'.csv')
        get('/home/ubuntu/response_time.csv.'+vm,'response_time_'+str(i)+'.csv')
        i += 1

@task
def run_python_program(program=None, sudo=False):
    cuisine.file_ensure('/usr/bin/python')
    if sudo:
        cuisine.sudo(('/usr/bin/python %s' % program))
    else:
        cuisine.run(('/usr/bin/python %s' % program))

def read_hosts_file(path):
    with open(path, 'rb') as f:
        reader = csv.reader(f, delimiter=';', quotechar='|')
        host_ip_list = [row[0] for row in reader]
    return host_ip_list

def data_collection():
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
    
#    execute(upload_file,'/home/ubuntu/measurements_downloader.py','measurements_downloader.py',sudo=True) 
    execute(run_python_program, program='/home/ubuntu/measurements_downloader.py')
    
    vm_list = read_hosts_file('host_ips.csv')
    
    print vm_list
    
    execute(collect_data_files,vm_list)

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
    
#    execute(upload_file,'/home/ubuntu/measurements_downloader.py','measurements_downloader.py',sudo=True) 
    execute(run_python_program, program='/home/ubuntu/measurements_downloader.py')
    
    vm_list = read_hosts_file('host_ips.csv')
    
    print vm_list
    
    execute(collect_data_files,vm_list)