# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 18:20:40 2015

@author: Konstantin
"""

from scipy import optimize
import numpy as np

import configparser, os, csv
from fabric.api import env, execute, task, get
import cuisine
import pandas
import operator
import pickle

import scipy.stats as stats

#class Parameter:
#    def __init__(self, value):
#        self.value = value
#    def set_val(self, value):
#        self.value = value
#    def __call__(self):
#        return self.value
#
#def fit(function, parameters, y, x=None):
#    def f(params):
#        i = 0
#        for p in parameters:
#            p.set_val(params[i])
#            i += 1
#        return y - function(x)
#    if x is None: x = np.arange(y.shape[0])
#    p = [param() for param in parameters]
#    optimize.leastsq(f, p)
#
#mu = Parameter(7)
#sigma = Parameter(3)
#height = Parameter(5)
#landa = Parameter(2)
#
#def gaussian(x):
#    return height() * np.exp(-((x-mu())/sigma())**2)
#def exponential(x):
#    return landa * np.exp(-(landa * x))
#
#def weibull(x, c):
#    return c / 2 * abs(x)**(c-1) * np.exp(-abs(x)**c)
#
#def norm(x):
#    return np.exp(-x**2/2)/np.sqrt(2*np.pi)
#
#def lognorm(x):
#    return 1 / (s*x*np.sqrt(2*np.pi)) * np.exp(-1/2*(np.log(x)/s)**2)

# pylint: disable=E1101
@task
def upload_file(remote_location, local_location, sudo=False):
    """
    Fabric task to upload a file to a VM.
    """
    cuisine.file_upload(remote_location,
                        local_location, sudo=sudo)
    cuisine.file_ensure(remote_location)

@task
def collect_data_files(vm_list):
    i = 1
    for vm in vm_list:
        get('/home/ubuntu/response_time.csv.'+vm,
            'response_time_'+str(i)+'.csv')
        i += 1

def expectation(data, dist=stats.dweibull):
    """
    Computes the expected value of a sample.
    """
    return dist(*dist.fit(data)).mean()

def sum_sq(x, x_bar):
    """
    Returns the sum of squared difference between 
    x and x_bar.
    """
    return (x - x_bar)**2

def log_num(x, x_bar):
    return np.log(x / x_bar) + ((x - x_bar)/x_bar)

def log_den(x, x_bar):
    return np.log(x / x_bar)

def calculate_prediction_data():
    data = pickle.load(open('valid_predictions', 'r'))
    Y_bar = np.mean(data['measured'].copy())
    y_var = np.apply_along_axis(log_den,
                                0,
                                data['measured'],
                                Y_bar)
    y_var2 = np.apply_along_axis(sum_sq,
                                 0,
                                 data['measured'],
                                 Y_bar)
    y_var = y_var.cumsum()[-1]
    y_var2 = y_var2.cumsum()[-1]
    R_squared_list = []
    regres_list = []
    i = 0
    for el in data.columns:
        if i == 3:
#            break
            print y_var2
#        Y_bar_z = np.mean(data[el].copy())
            regres_var = np.apply_along_axis(sum_sq,
                                             0,
                                             data[el],
                                             Y_bar)
            regres_var = regres_var.cumsum()[-1]
            regres_list.append(regres_var)
            R_squared = y_var2/regres_var
            if R_squared > 1.0:
                R_squared = (1.0 / R_squared)
            print "======%s" % R_squared
            R_squared_list.append(R_squared)
        elif i == 4:
#            break
            print y_var2
#        Y_bar_z = np.mean(data[el].copy())
            regres_var = np.apply_along_axis(sum_sq,
                                             0,
                                             data[el],
                                             Y_bar)
            regres_var = regres_var.cumsum()[-1]
            regres_list.append(regres_var)
            R_squared = y_var2/regres_var
            if R_squared > 1.0:
                R_squared = (1.0 / R_squared)
            print "======%s" % R_squared
            R_squared_list.append(R_squared)
        else:
            print y_var
#        Y_bar_z = np.mean(data[el].copy())
            regres_var = np.apply_along_axis(log_num,
                                             0,
                                             data[el],
                                             Y_bar)
            regres_var = regres_var.cumsum()[-1]
            regres_list.append(regres_var)
            R_squared = 1 - abs(y_var/regres_var)
            print "======%s" % R_squared
            R_squared_list.append(R_squared)
        i += 1
    print R_squared_list
    print regres_list
    print y_var
    R_squared_list = np.array(R_squared_list, dtype='float64')
#    R_squared_list = pandas.DataFrame(R_squared_list)
    print data
    data.loc[len(data)] = R_squared_list
#    data = np.hstack((data,R_squared_list))
    pickle.dump(data, open('valid_predictions2', 'w'))
    np.savetxt('valid_predictions2.csv', data,
               fmt='%.4f', delimiter=';')
    with open('valid_predictions2.csv', 'ab') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(R_squared_list)
        writer.writerow(data.columns)

def write_prediction_data(data, ratings):
    n = len(data)
    print n
    rates = sorted(ratings.keys())
    for el in rates:
        preds = get_predictions(ratings, el, n)
        data = np.vstack((data, preds))
    data = data.transpose()
    data = pandas.DataFrame(data=data, dtype='float64')
    np.savetxt('valid_predictions.csv', data,
               fmt='%.4f', delimiter=';')
    names = ['measured']
    [names.append(el) for el in rates]
    print names
    data.columns = names
    pickle.dump(data, open('valid_predictions', 'w'))
#    np.savetxt('predictions.csv', arr, fmt='%.4f', delimiter=';')

def read_data_from_files():
    """
    Get number of failure rates from failure rates file.
    """
    f_rates = [] 
    with open('f_rates.csv', 'rb') as f:
        reader = csv.reader(f, delimiter=';', quotechar='|')
        f_rates = [row[0] for row in reader]
    return f_rates

def fit_model(data, model_name, ratings):
    n = len(data)
    if model_name == 'expon':
        params = convert_string_to_tuple(ratings['expon'][0][0])
        print params
        std_func = stats.expon.rvs(size=n,
                                   loc=params[0],
                                   scale=params[1])
    elif model_name == 'dweibull':
        params = convert_string_to_tuple(ratings['dweibull'][0][0])
        print params
        std_func = stats.dweibull.rvs(params[0],
                                      loc=params[1],
                                      scale=params[2],
                                      size=n)

    elif model_name == 'norm':
        params = convert_string_to_tuple(ratings['norm'][0][0])
        print params
        std_func = stats.norm.rvs(loc=params[0],
                                  scale=params[1], 
                                  size=n)
    elif model_name == 'lognorm':
        params = convert_string_to_tuple(ratings['lognorm'][0][0])
        print params
        std_func = stats.lognorm.rvs(params[0],
                                     loc=params[1],
                                     scale=params[2],
                                     size=n)
    std_func.sort()
    test_vals = stats.ks_2samp(data, std_func)
    result = [test for test in test_vals]
    result.append(params)
    result.append(std_func)
    return result

def convert_string_to_tuple(ratings_string):
    """
    Helper method to convert a Python string to a tuple.
    """
    result_tuple = ratings_string.split(', ')
    result_tuple[0] = result_tuple[0].lstrip('(')
    result_tuple[-1] = result_tuple[-1].rstrip(')')
    result_tuple = tuple([float(el) for el in result_tuple])
    return result_tuple
        

    
def rank_models(ratings):
    sorted_by_stat = sorted(ratings.items(),
                            key=operator.itemgetter(1))
    return [element[0] for element in sorted_by_stat]


def get_models():
    with open('fitted_models.csv', 'rb') as f:
        reader = csv.reader(f, delimiter=';')
        data = {}
        for row in reader:
            data.update({row[0]: [row[1:]]})
#        data = [row for row in reader]
    return data

def write_results(ranking, ratings):
    with open('validated_models.csv', 'wb') as f:
        writer = csv.writer(f, delimiter=';')
        for dist in ranking:
            writer.writerow([dist, ratings[dist][2],
                             ratings[dist][0], ratings[dist][1]
                            ])

def get_predictions(ratings, model_name, size):
    """
    Computes predicted random values depending on type
    and parameters of the distribution.
    """
    if(model_name == 'expon'):
        preds = stats.expon.rvs(ratings['expon'][2][0],
                                ratings['expon'][2][1],
                                size=size)
    elif(model_name == 'dweibull'):
        preds = stats.dweibull.rvs(ratings['dweibull'][2][0],
                                   ratings['dweibull'][2][1],
                                   ratings['dweibull'][2][2],
                                   size=size)
    elif(model_name == 'norm'):
        preds = stats.norm.rvs(ratings['norm'][2][0],
                               ratings['norm'][2][1],
                               size=size)
    elif(model_name == 'lognorm'):
        preds = stats.lognorm.rvs(ratings['lognorm'][2][0],
                                  ratings['lognorm'][2][1],
                                  ratings['lognorm'][2][2],
                                  size=size)
    preds = np.apply_along_axis(abs, 0, preds)
    preds = np.apply_along_axis(sorted, 0, preds)
    return preds


def fit_models():
    """
    Gets fitted models and checks them via KS-test. Computes
    R-squared as goodness of fit measurements.
    """
#if __name__ == "__main__":
    f_rates = read_data_from_files()
    f_rates = sorted(f_rates)
    print f_rates
    data = np.array(f_rates, dtype='float64')
    data = data/1500
    n = len(data)
    data.sort()

    ratings = get_models()
    [ratings.update({key : fit_model(data, key, ratings)})
     for key
     in ratings.keys()]

    ranking = rank_models(ratings)
    write_results(ranking, ratings)

    write_prediction_data(data, ratings)
    calculate_prediction_data()

if __name__ == "__main__":
    fit_models()
