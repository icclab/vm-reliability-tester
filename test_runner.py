# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 08:59:22 2015

@author: Konstantin
"""

import configparser, csv, sys, getopt

from fabric.api import env, execute, task, parallel, serial, sudo, run
import cuisine

@task
@parallel
def run_python_program(program=None, param='0', sudo=False):
#    cuisine.file_ensure('/usr/bin/python')
    if sudo:
        sudo(('/usr/bin/python %s -n %s' % (program, param)))
    else:
        run(('/usr/bin/python %s -n %s' % (program, param)))

def read_hosts_file(path):
    with open(path, 'rb') as f:
        reader = csv.reader(f, delimiter=';', quotechar='|')
        host_ip_list = [row[0] for row in reader]
    return host_ip_list

if __name__ == "__main__":
    config = configparser.ConfigParser()
    conf = open('config.ini', 'rb')
#    conf.readline()
    config.readfp(conf)
    print(config.sections())

    vm_credentials = dict(config['SSH_CREDENTIALS'])
    ssh_username = str(vm_credentials['ssh.username'])
    ssh_password = str(vm_credentials['ssh.password'])
    ssh_key_filename = str(vm_credentials['ssh.key_filename'])
    
    test_runs = dict(config['TEST_RUNS'])
    test_start = str(test_runs['test_start'])
    test_end = str(test_runs['test_end'])
    
    vm_list = read_hosts_file('/etc/host_ips.csv')
    
    print vm_list

    env.hosts = vm_list
    env.user = ssh_username
    env.password = ssh_password
    env.key_filename = ssh_key_filename
    env.connection_attempts = 5
    
    [execute(run_python_program,program='/root/test_program.py',param=str(i)) 
        for i in range(int(test_start), int(test_end)+1)] 