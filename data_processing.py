# -*- coding: utf-8 -*-
"""
Created on Tue Mar 03 08:00:26 2015

@author: Konstantin
"""

import numpy as np
import configparser, os, csv
from fabric.api import env, execute, task, get
import cuisine
import vm_control
import numpy as np
import pandas

def read_data_from_file(data_file):  
    num_array = [] 
    with open(str(data_file),'rb') as f:
        reader = csv.reader(f, delimiter=';', quotechar='|')
        num_array.append([row[0] for row in reader])
#            execution_time_array = np.concatenate((execution_time_array, np.array([row[1] for row in reader])),
#                                                  axis=1)
    return num_array

def add_diffs():
    num_failures = read_data_from_file('f_rates.csv')
    data = np.array(num_failures, dtype='float64')
    data = np.transpose(data)
    frame = pandas.DataFrame(data=data, columns=['num_failures'])
    diffs = frame.diff()
    diffs[0:1]=frame[0:1]
    frame['num_diff'] = diffs
    frame.to_csv('f_rates.csv',sep=';',header=False,index=False)

if __name__ == "__main__":     
    add_diffs()
