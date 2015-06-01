# -*- coding: utf-8 -*-
"""
Created on Tue Mar 03 18:38:56 2015

@author: Konstantin
"""

import configparser, os, csv
from fabric.api import env, execute, task, get
import cuisine
import vm_control
import numpy as np
import pandas

@task
def upload_file(remote_location, local_location, sudo=False):
    """
    Fabric task to upload a file to a VM.
    """
    cuisine.file_upload(remote_location, local_location, sudo=sudo)
    cuisine.file_ensure(remote_location)

@task
def collect_data_files(vm_list):
    i = 1
    for vm in vm_list:
        get('/root/response_time.csv.'+vm,
            'response_time_'+str(i)+'.csv')
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

#def read_data_from_files(vm_list):
##    execution_time_array = np.array([])   
#    execution_time_array = [] 
#    i = 1
#    for vm in vm_list:
#        with open('response_time_'+str(i)+'.csv','rb') as f:
#            reader = csv.reader(f, delimiter=';', quotechar='|')
#            execution_time_array.append(list([row[1] for row in reader]))
##            execution_time_array = np.concatenate((execution_time_array, np.array([row[1] for row in reader])),
##                                                  axis=1)
#        i += 1
#    return execution_time_array

def read_data_from_files(vm_list, data_type):
#    execution_time_array = np.array([])   
    execution_time_array = [] 
    for i in range(1, len(vm_list)+1):
        with open(str(data_type)+str(i)+'.csv','rb') as f:
            reader = csv.reader(f, delimiter=';', quotechar='|')
            execution_time_array.append(list([[row[0],row[1]] for row in reader]))
#            execution_time_array = np.concatenate((execution_time_array, np.array([row[1] for row in reader])),
#                                                  axis=1)
    return execution_time_array

def read_data_from_file(vm_list, data_type, index):
#    execution_time_array = np.array([])   
    execution_time_array = [] 
    with open(str(data_type)+str(index)+'.csv','rb') as f:
        reader = csv.reader(f, delimiter=';', quotechar='|')
        execution_time_array.append(list([[row[0],row[1]] for row in reader]))
#            execution_time_array = np.concatenate((execution_time_array, np.array([row[1] for row in reader])),
#                                                  axis=1)
    return execution_time_array

def log_data(path, data):
    with open(path, 'ab') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(data)
    return
    
#def calc_sum(data_list):
#    result = 0.0
#    for x in data_list:
#        result += x
#    return result

def spc_estimated_data_point(vm_list):    
    vm_list = read_hosts_file('host_ips.csv')
    
    print vm_list
    
    ex_times = read_data_from_files(vm_list, 'response_time_')
    data = np.array(ex_times, dtype='float64')
    data2 = np.transpose(data.copy())
    X = data2.mean(axis=1)
#    X.dtype='float64'
    X_bar = np.mean(X)
#    X = pandas.DataFrame(X,columns=['X'])
    R = data2.max(axis=1) - data2.min(axis=1)
    R_bar = np.mean(R)
    
#    D3 = 0
#    D4 = 2.114
    A2 = 0.577
    
#    LCL_r = R_bar * D3
#    UCL_r = R_bar * D4
#    
#    LCL = X_bar - A2 * R_bar
    UCL = X_bar + A2 * R_bar
    
    frame = pandas.DataFrame(data2, columns=['VM1','VM2','VM3','VM4','VM5'])
    failure_rates = []
    failure_rate1 = float(len(frame[frame.VM1 > UCL]))    
    failure_rates.append(failure_rate1)    
    failure_rate2 = float(len(frame[frame.VM2 > UCL]))
    failure_rates.append(failure_rate2)
    failure_rate3 = float(len(frame[frame.VM3 > UCL]))
    failure_rates.append(failure_rate3)
    failure_rate4 = float(len(frame[frame.VM4 > UCL]))
    failure_rates.append(failure_rate4)
    failure_rate5 = float(len(frame[frame.VM5 > UCL]))   
    failure_rates.append(failure_rate5)  
    
    f_rates = np.array(failure_rates)
#    f_sum = [calc_sum(failure_rates)]
    f_sum = f_rates.cumsum()[-1:].tolist()
#    np.savetxt('f_rates.csv',f_rates, delimiter=';', fmt='%10')
    log_data('f_rates.csv',f_sum)

def implicit_data_point(vm_list):
    f_sum = 0.0
    for i in range(1, len(vm_list)+1):
        occ_times = read_data_from_file(vm_list, 'failures_', i)       
        data = np.array(occ_times[0], dtype='float64')
        frame = pandas.DataFrame(data=data, columns=['Nr','Occtime'])
        nums = frame.groupby(['Nr']).agg('count')['Nr']
        print nums.cumsum().tolist()[-1]
        f_sum += nums.cumsum().tolist()[-1]
    log_data('f_rates.csv',(f_sum,))

def set_data_point():
    config = configparser.ConfigParser()
    conf = open('config.ini', 'rb')
#    conf.readline()
    config.readfp(conf)
    print(config.sections()) 
    tool_data = dict(config['TOOL_DATA'])
    markov_mode = bool(tool_data['markov.mode'])
    vm_list = read_hosts_file('host_ips.csv')    
    print vm_list
    if markov_mode:
        implicit_data_point(vm_list)
    else:
        spc_estimated_data_point(vm_list)

if __name__ == "__main__":   
    set_data_point()    

#    
#    vm_list = read_hosts_file('host_ips.csv')
#    
#    print vm_list
#    
#    markov_data_point(vm_list)
    
        
