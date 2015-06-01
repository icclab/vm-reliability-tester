# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 09:42:19 2015

@author: Konstantin
"""

import keystoneclient.v2_0.client as ksclient
from novaclient import client as noclient
import configparser, time, os, copy


class VM_Control(object):
    """
    A class to control VMs in OpenStack
    """   
    __instance = None
    cred = None          
    KEYSTONE_CONN = None
    NOVA_CONN = None
    config_data = None
    ssh_public_key_filename = None
    pk = None
    sec_group = None
    
    def __init__(self):
        execfile('openrc.py')
        self.cred = self.get_nova_creds()
        print self.cred
        self.KEYSTONE_CONN = self.get_keystone_client(self.cred)
        self.NOVA_CONN = self.get_nova_client(self.cred)
        config = configparser.ConfigParser()
        config.read('config.ini')
        print(config.sections()) 
        vm_credentials = dict(config['SSH_CREDENTIALS'])
        ssh_public_key_filename = str(vm_credentials['ssh.public_key_filename'])
        self.pk = self.ensure_public_key(self.NOVA_CONN,
                                         ssh_public_key_filename);                                           print self.pk    
        self.sec_group = self.ensure_security_group(self.NOVA_CONN)
     
    
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        execfile('openrc.py')
        cls.__instance.cred = cls.__instance.get_nova_creds()
        cls.__instance.KEYSTONE_CONN = cls.__instance.get_keystone_client(cls.__instance.cred)
        cls.__instance.NOVA_CONN = cls.__instance.get_nova_client(cls.__instance.cred)
        config = configparser.ConfigParser()
        config.read('config.ini')
        vm_credentials = dict(config['SSH_CREDENTIALS'])
        ssh_public_key_filename = str(vm_credentials['ssh.public_key_filename'])
        cls.__instance.pk = cls.__instance.ensure_public_key(cls.__instance.NOVA_CONN,
                                         ssh_public_key_filename)
        cls.__instance.sec_group = cls.__instance.ensure_security_group(cls.__instance.NOVA_CONN)
        return cls.__instance

   
    def get_nova_creds(self):
        #returns credentials dictionary from os variables in nova format   
        cred = {}        
        cred['username'] = os.environ['OS_USERNAME']
        cred['api_key'] = os.environ['OS_PASSWORD']
        cred['auth_url'] = os.environ['OS_AUTH_URL']
        cred['project_id'] = os.environ['OS_TENANT_NAME']
        return cred
    
    def get_keystone_client(self, cred):
        #returns keystone client
        temp = copy.copy(cred)
        temp['password'] = cred['api_key']
        temp.pop('api_key', None)
        temp['tenant'] = cred['project_id']
        temp.pop('project_id', None)
        print temp
        return ksclient.Client(**temp)
    
    def get_nova_client(self, cred):
        #returns nova client
        KEYSTONE_CONN = self.get_keystone_client(cred)
        cred['auth_token'] = KEYSTONE_CONN.get_token(KEYSTONE_CONN.session)
        RAW_TOKEN = KEYSTONE_CONN.get_raw_token_from_identity_service(
            auth_url=cred['auth_url'],
            username=cred['username'],
            password=cred['api_key'],
            tenant_name=cred['project_id'])
        cred['tenant_id'] = RAW_TOKEN['token']['tenant']['id']
        return noclient.Client('1.1',**cred)
    
    def ensure_public_key(self, nova_client,
                      public_key_filename):
        KP_MANAGER = nova_client.keypairs
        public_key = [line for line in open(public_key_filename)][0]
        if not(KP_MANAGER.findall(name='test_key')):
            pk = KP_MANAGER.create('test_key',public_key=public_key)
        else:
            pk = KP_MANAGER.findall(name='test_key')[0]
        return pk

    def ensure_security_group(self, nova_client):
        SG_MANAGER = nova_client.security_groups
        RULE_MANAGER = nova_client.security_group_rules
        sg_new = False
        if not(SG_MANAGER.findall(name='webserver')):
            sec_group = SG_MANAGER.create('webserver','Allows SSH and web server access.')
            sg_new = True
        else:
            sec_group = SG_MANAGER.findall(name='webserver')[0]
        if (sg_new):
            RULE_MANAGER.create(sec_group.id,ip_protocol='tcp',from_port=22,to_port=22)
            RULE_MANAGER.create(sec_group.id,ip_protocol='tcp',from_port=80,to_port=80)
            RULE_MANAGER.create(sec_group.id,ip_protocol='icmp',from_port=-1,to_port=-1)
        return sec_group
        
    def create_vm(self,
              vm_name='TestVM',
              image_name='Ubuntu 12.04 LTS',
              flavor_name='m1.small',
              network_label=u'zhaw-net',
              sec_group='default',
              injected_pk=None,
              availability_zone='nova'):
        VM_MANAGER = self.NOVA_CONN.servers
        IMAGE_MANAGER = self.NOVA_CONN.images
        FLAVOR_MANAGER = self.NOVA_CONN.flavors
        NETWORK_MANAGER = self.NOVA_CONN.networks
        
        image = IMAGE_MANAGER.findall(name=image_name)[0]
        flavor = FLAVOR_MANAGER.findall(name=flavor_name)[0]
        network = NETWORK_MANAGER.findall(label=network_label)[0]
        nics = [{'net-id': network.id}]
        
        print nics
        
        injected_pk = self.pk
        sec_group = self.sec_group        
        
        if not (VM_MANAGER.findall(name=vm_name)):
            VM_MANAGER.create(name=vm_name,
                           image=image.id, 
                           flavor=flavor.id,
                           security_groups=[sec_group.human_id],
                           key_name=injected_pk.name,
                           nics=nics)
        vm_id, name, status = self.ensure_vm_active(vm_name)
        return vm_id, name, status
    
    def ensure_vm_active(self, vm_name):
        VM_MANAGER = self.NOVA_CONN.servers
        vm = VM_MANAGER.findall(name=vm_name)[0]
        timeout = 60
        elapsed_time = 0
        while (vm.status != 'ACTIVE'):
            vm = VM_MANAGER.findall(name=vm.name)[0]
            if (vm.status == 'ERROR'):
                print("VM ID: %s name: %s CREATION FAILED!!" % (vm.id, vm.name))
                break
            print("VM ID: %s name: %s in status: %s" % (vm.id, vm.name, vm.status))
            time.sleep(1)
            elapsed_time += 1
            if (elapsed_time > timeout):
                vm.delete()
                print("VM ID: %s name: %s CREATION FAILED!!" % (vm.id, vm.name))
                break
            
        print("VM ID: %s name: %s %s." % (vm.id, vm.name, vm.status))
        return vm.id, vm.name, vm.status
    
    def create_vms(self, vms):
        return [self.create_vm(
                    vm_name=vm,
                      image_name='Ubuntu 12.04 LTS',
                      flavor_name='m1.small',
                      network_label='zhaw-net',
                      sec_group=self.sec_group,
                      injected_pk=self.pk
                      ) for vm in vms]
                          
    def start_vm(self,
                     vm_name):
        VM_MANAGER = self.NOVA_CONN.servers
        vm = VM_MANAGER.findall(name=vm_name)[0]
        vm.start()
    
        while (vm.status != 'ACTIVE'):
            vm = VM_MANAGER.findall(name=vm.name)[0]
            if (vm.status == 'ERROR'):
                print("VM ID: %s name: %s START FAILED!!" % (vm.id, vm.name))
                break
            print("VM ID: %s name: %s in status: %s" % (vm.id, vm.name, vm.status))
            time.sleep(1)
            
        print("VM ID: %s name: %s %s." % (vm.id, vm.name, vm.status))
        return vm.id, vm.name, vm.status

    def start_vms(self, vms):
        return [self.start_vm(
                    vm_name=vm
                      ) for vm in vms]
                          
    def stop_vm(self,
                     vm_name):
        VM_MANAGER = self.NOVA_CONN.servers
        vm = VM_MANAGER.findall(name=vm_name)[0]
        vm.stop()
    
        while (vm.status != 'SHUTOFF'):
            vm = VM_MANAGER.findall(name=vm.name)[0]
            if (vm.status == 'ERROR'):
                print("VM ID: %s name: %s STOP FAILED!!" % (vm.id, vm.name))
                break
            print("VM ID: %s name: %s in status: %s" % (vm.id, vm.name, vm.status))
            time.sleep(1)
            
        print("VM ID: %s name: %s %s." % (vm.id, vm.name, vm.status))
        return vm.id, vm.name, vm.status

    def stop_vms(self, vms):
        return [self.stop_vm(
                    vm_name=vm
                      ) for vm in vms]
    
    def get_vm(self,
                     vm_name):
        VM_MANAGER = self.NOVA_CONN.servers
        vm = VM_MANAGER.findall(name=vm_name)[0]
        return vm
    
    def get_vms_data(self, vms):
        return [self.get_vm(
                    vm_name=vm
                      ) for vm in vms]
    
    def get_free_floating_ips(self):
        IP_MANAGER = self.NOVA_CONN.floating_ips
        return [ip for ip in IP_MANAGER.list() 
                if ip.instance_id==None]
                    
    def assign_floating_ip_to_vm(self,
                                 vm_name,
                                 ip_list):
        VM_MANAGER = self.NOVA_CONN.servers
        vm = VM_MANAGER.findall(name=vm_name)[0]
        assigned_ips = [address for address in vm.addresses.values()[0] 
                        if address[u'OS-EXT-IPS:type']==u'floating']
        if len(assigned_ips) < 1:
            free_ip = ip_list[0].ip
            fixed_ip = [ip[0] for ip in vm.networks.values()][0]
            vm.add_floating_ip(free_ip, fixed_address=fixed_ip)
            return vm
        else:
            return vm
            
    def get_floating_ip(self,
                        vm_name):
        VM_MANAGER = self.NOVA_CONN.servers
        vm = VM_MANAGER.findall(name=vm_name)[0]
        floating_ip = [address for address in vm.addresses.values()[0] 
                        if address[u'OS-EXT-IPS:type']==u'floating'][0]
        return floating_ip[u'addr'] 


if __name__ == "__main__":       
    execfile('openrc.py') 
    vm_list = ['vm1','vm2']
   
    vm_control = VM_Control()
    ip_list = vm_control.get_free_floating_ips()
    vm_control.assign_floating_ip_to_vm('vm1',ip_list)
    ip = vm_control.get_floating_ip('vm1')
    print ip
