VM Reliability Tester
=====================

**“Measure and benchmark reliability of your OpenStack virtual machines.”**

“VM Reliability Tester” is a software that tests performance and reliability of
virtual machines that are hosted in an OpenStack cloud platform. It evaluates
the failure rate of VMs by performing a stress test on them. VM Reliability
Tester installs OpenStack virtual machines, uploads a test program to them, runs
this test program remotely and then captures program execution times to
determine reliability of the virtual machines. If the test program takes a
significant amount of time to complete, this is considered to result in a VM
failure. Such deviations in execution time are an important benchmark for
testing performance and reliability of your OpenStack environment.

 

Installation
------------

Clone the git repository into the directory of your choice:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
git clone https://github.com/icclab/vm-reliability-tester
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

Edit the following files:

1.  config.ini: The configuration of VM Reliability Tester on your desktop.

2.  remote\_config.ini: The configuration of VM Reliability Tester on the master
    VM

3.  openrc.py: Your OpenStack Authentication credentials

4.  vm\_list.csv: Names of your master and client VMs

 

Run:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
python vm_reliability_tester.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

VM Reliability Tester does the folling:

-   First it creates the master and client VMs.

-   Then it uploads all configuration files and programs to the master VM

-   It uploads all test scripts from the master VM to client VMs

-   It starts the test runner on the master VM

-   The test runner orchestrates the test runs on the client VMs

-   The tests are executed on the client VMs

-   Measurements are downloaded from the client VMs to the master VM

-   The master VM consolidates measurements in the file f\_rates.csv

-   f\_rates.csv is downloaded to your labtop

-   Models are created and fitted to the data and stored in fitted\_models.csv

-   A second remote stress test is initiated

-   The master VM orchestrates the 2nd stress test

-   The 2nd stress test is executed on the client VMs

-   Measurements are downloaded from the client VMs to the master VM

-   The master VM consolidates measurements in the file f\_rates.csv

-   The fitted models are tested versus the 2nd sample and stored in
    validated\_models.csv

-   The result is an estimation of failure rates in f\_rates.csv and a model of
    failure rates in validated\_models.csv

 

After the test (it takes 20-30 minutes!) check the files f\_rates.csv,
fitted\_models.csv and validated\_models.csv on your labtop.
