# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 08:59:22 2015

@author: Konstantin
"""

import configparser, csv

from fabric.api import env, execute, task, parallel
import cuisine

@task
@parallel
def update(package=None):
    """
    Fabric task to update all packages on a VM.
    """
    cuisine.package_update(package)
    
@task
@parallel
def upgrade(package=None):
    """
    Fabric task to upgrade all packages on a VM.
    """
    cuisine.package_upgrade(package)

@task
@parallel
def install(package):
    """
    Fabric task to install a package on a VM.
    """
    cuisine.package_install(package)
    cuisine.package_ensure(package)
    
@task
@parallel
def pip_install(package):
    """
    Fabric task to install a package via pip on a VM.
    """
    cuisine.package_ensure('python-pip')
    command = str('pip install %s' % package)
    cuisine.sudo(command)

@task
@parallel
def upload_file(remote_location, local_location, sudo=False):
    """
    Fabric task to upload a file to a VM.
    """
    cuisine.file_upload(remote_location, local_location, sudo=sudo)
    cuisine.file_ensure(remote_location)

@task
@parallel
def run_python_program(program=None, sudo=False):
    """
    Fabric task to run a Python program on a VM.
    """
    cuisine.file_ensure('/usr/bin/python')
    if sudo:
        cuisine.sudo(('/usr/bin/python %s' % program))
    else:
        cuisine.run(('/usr/bin/python %s' % program))

def read_hosts_file(path):
    """
    Reads the hosts list to get IPs of the other VMs.
    """
    with open(path, 'rb') as f:
        reader = csv.reader(f, delimiter=';', quotechar='|')
        host_ip_list = [row[0] for row in reader]
    return host_ip_list

if __name__ == "__main__":       
    config = configparser.ConfigParser()
    conf = open('config.ini', 'rb')
#    conf.readline()
    config.readfp(conf)
#    print(config.sections())

    vm_credentials = dict(config['SSH_CREDENTIALS'])
    ssh_username = str(vm_credentials['ssh.username'])
    ssh_password = str(vm_credentials['ssh.password'])
    ssh_key_filename = str(vm_credentials['ssh.key_filename'])
    
    vm_list = read_hosts_file('/etc/host_ips.csv')
    
    print vm_list
    
#    vm_control = vm_control.VM_Control()
#    vm_control.create_vms(vm_list)
##    vm_control.stop_vms(vm_list)
##    vm_control.start_vms(vm_list)
#    ip_list = vm_control.get_free_floating_ips()
#    vm_control.assign_floating_ip_to_vm('vm1',ip_list)
#    vm_data = vm_control.get_vms_data(vm_list)
#    ssh_url = vm_control.get_floating_ip('vm1')
    
    env.hosts = vm_list
    env.user = ssh_username
    env.password = ssh_password
    env.key_filename = ssh_key_filename
    env.connection_attempts = 5
    
#    execute(update)
#    execute(upgrade)    
#    execute(install, 'python-pip')
#    execute(install, 'python-dev')
#    execute(pip_install, 'dispy')
#    execute(pip_install, 'ecdsa')
#    execute(pip_install, 'pycrypto')
#    execute(pip_install, 'fabric')
#    execute(pip_install, 'cuisine')
    execute(update)
    execute(upgrade)
    execute(install, 'python-pip')
    execute(install, 'python-dev')
    execute(pip_install, 'multiprocessing')
    execute(pip_install, 'logging')
    execute(pip_install, 'multiprocessing')
#    execute(install, 'gcc')
    execute(upload_file, '/etc/host_ips.csv',
            '/etc/host_ips.csv', sudo=True)
    execute(upload_file, '/home/ubuntu/test_program.py',
            '/home/ubuntu/test_program.py', sudo=True)
    execute(upload_file, '/home/ubuntu/failures.csv',
            '/home/ubuntu/failures.csv', sudo=True)    
    execute(upload_file, '/home/ubuntu/response_time.csv',
            '/home/ubuntu/response_time.csv', sudo=True)
