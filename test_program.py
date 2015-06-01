# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 08:53:29 2015

@author: Konstantin
"""

import time, random, csv
import sys, getopt
from multiprocessing import Process, Queue, cpu_count, current_process
import logging
from functools import wraps


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

fibo_dict = {}
number_of_cpus = cpu_count()

data_queue = Queue()

class Failure(Exception):
    def __init__(self, value1, value2):
        self.value1 = value1
        self.value2 = value2

    def __str__(self):
        return repr(self.value1, self.value2)

def failure_registration(function):
    @wraps(function)
    def wrapper(q, fibo_dict, start, test_num):
            try:
                return function(q, fibo_dict, start, test_num)
            except Failure as e:
                test_num = e.value1
                occ_time = e.value2
                log_file = open('failures.csv', 'ab')
                log_writer = csv.writer(log_file,delimiter=';',quotechar='|')
                log_writer.writerow((test_num, occ_time))
                log_file.close()
                print("Exception caught")
    return wrapper

def producer_task(q, fibo_dict):
    for i in range(30):
        value = random.randint(9000,100000)
        fibo_dict[value] = None
        logger.info("Producer [%s] putting value [%d] into queue... " % (current_process().name, value))
        q.put(value)

@failure_registration
def consumer_task(q, fibo_dict, start, test_num):
    while not q.empty():
        value = q.get(True, 0.05)
        a,b = 0, 1
        calc_start = float(time.time())
        for item in range(value):
            a, b = b, a + b
            fibo_dict[value] = a
        calc_time = float(time.time() - calc_start)
        if(calc_time > 1.0):
            logger.info("Exception: calc time is [%.5f]" % calc_time)
            occ_time = time.time() - start
            raise Failure(test_num, occ_time)
        logger.info("Consumer [%s] getting value [%d] from queue... " % (current_process().name, value))


def main(argv):
   test_num = ''
   try:
      opts, args = getopt.getopt(argv,"hn::",longopts=[])
   except getopt.GetoptError:
      print('test_program.py -n <test_run>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test_program.py -n <test_run>'
         sys.exit()
      elif opt == '-n':
         test_num = arg
         return test_num

if __name__ == "__main__":
    test_num = main(sys.argv[1:])
    start = time.time()
    producer = Process(target=producer_task, args=(data_queue,fibo_dict))
    producer.start()
    producer.join()
    consumer_list = []
    for i in range(8*number_of_cpus-1):
        consumer = Process(target=consumer_task, args=(data_queue,fibo_dict,start,test_num))
        consumer.start()
        consumer_list.append(consumer)
    [consumer.join() for consumer in consumer_list]
    runtime = time.time() - start
    print("Runtime: %s" % runtime)
    data_file = open('response_time.csv', 'ab')
    data_writer = csv.writer(data_file,delimiter=';',quotechar='|')
    data_writer.writerow((test_num, runtime))
    data_file.close()
