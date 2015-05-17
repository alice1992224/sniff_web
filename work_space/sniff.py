# -*- coding: utf-8 -*-
"""
    sniff 類別，讓別的程式 import 
"""

import scapy
from scapy.all import *
import time
import re
import json
import sys
import ConfigParser
import argparse
import signal
import os

class Sniff5:
    def __init__(self, pkt_source="file", input_file="input_file", log_file="sniff.log", count="1000", interface=""):
        self.pkt_source = pkt_source
        self.input_file = input_file
        self.log_file = log_file
        self.count = count
        self.interface = interface

        self.packet_type_list = []
        self.packet_type_dict = {}
        self.client_mac = ""
        self.cf = ConfigParser.ConfigParser()

        # result record
        self.possiable_start_init = 0
        self.possiable_start_end = 0
        self.end_time = 0

        # initial variable
        self.__initial()

    def count_roaming_time_by_realtime(self):
        if self.interface == "":
            print "Please use --interface argument to inform us the wifi interface name." 
        else:
            self.isEnd = False
            self.log_fp = open(self.log_file, 'w')
            #sniff(iface=self.interface, prn = self.__PacketHandler, count=self.count)
            sniff(iface=self.interface, prn = self.__PacketHandler)
            self.log_fp.close()
            return self.isEnd

    def count_roaming_time_by_file(self):
        #print 'in count_roaming_time_by_file'
        if self.input_file == "":
            print "Please use -f argument to inform us the input file name." 
        else:
            self.__read_input()

    def set_interface(self, interface):
        self.interface = interface

    def set_input_file(self, input_file):
        self.input_file = input_file 

    def __initial(self):
        """
            準備 cf 物件，方便之後讀取設定檔資料
            初始化 packet_type_list 和 packet_type_dict

            packet_type_list
                [
                    ('0', '[Association Request]'), 
                    ('1', '[Association Response]'), 
                    ...
                ]
            packet_type_dict
                {
                    '[Probe Response]': [], 
                    '[Beacon]': [], 
                    ...
                }
        """

        # establish cf object
        config_file = self.cf.read("work_space/sniff.config") 
        if config_file is []:
            print 'Error: Config file is empty'

        # initial packet_type_list and packet_type_dict
        self.packet_type_list = self.cf.items("packet_type")
        for type_num, pkt_type in self.packet_type_list:
            self.packet_type_dict[pkt_type] = []

        # get client_mac
        self.client_mac = self.cf.get('start_condition', 'client_mac')

    def __send_end_signal(self):
        f = open("work_space/pid", "r")
        pid = int(f.read())
        os.kill(pid, signal.SIGINT) 

    def __PacketHandler(self, pkt) :
        if pkt.addr1 == self.client_mac or pkt.addr2 == self.client_mac:

            if pkt.type == 0:
                # collect packet infomation
                for type_num, pkt_type in self.packet_type_list: 
                    if pkt.subtype == int(type_num):
                        tmp_dict = {}
                        tmp_dict['type'] = pkt_type
                        tmp_dict['dst_mac'] = pkt.addr1  
                        tmp_dict['src_mac'] = pkt.addr2 
                        tmp_dict['time'] = time.time() 
                        s = "%s %s %s %f"%( tmp_dict['type'], tmp_dict['dst_mac'], tmp_dict['src_mac'], tmp_dict['time'])
                        self.log_fp.write(str(s)+'\n')

                        # check if is end
                        conditions_list = json.loads(self.cf.get('end_condition', 'certain'))
                        for conditions in conditions_list:
                            pkt_type = conditions.keys()[0]
                            if tmp_dict['type']  == pkt_type:
                                print '[Info] %s \t %s send a %s packet to %s'%(tmp_dict['time'], tmp_dict['dst_mac'], pkt_type, tmp_dict['src_mac'])
                                self.isEnd = True
                                end_time = self.__pkt_checker([tmp_dict], conditions[pkt_type], pkt_type)
                                 
                                if end_time != None:
                                    print "================ Handover complete =================="
                                    self.__count_start_time()
                                    print "End time is at %f"%(tmp_dict['time'])
                                    self.end_time = tmp_dict['time']
                                    print "Totally cost %f seconds."%(self.end_time - self.possible_interval_end) 
                                    #print "Totally cost %f ~ %f seconds."%(self.end_time - self.possible_interval_end, self.end_time - self.possible_interval_init) 
                                    self.__send_end_signal()
                                    exit() 
                                else:
                                    print 'end none'
                        
                        # push packet to stack 
                        for type_num, pkt_type in self.packet_type_list:
                            if tmp_dict['type'] == pkt_type :
                                self.packet_type_dict[pkt_type].append(tmp_dict) 
                                print '[Info] %s \t %s send a %s packet to %s'%(tmp_dict['time'], tmp_dict['dst_mac'], pkt_type, tmp_dict['src_mac'])
                                break

    def __read_input(self):

        global packet_type_dict

        input_fp = open(self.input_file, 'r')
        for line in input_fp:

            tmp_dict = {}
            m = re.search('(\[[a-zA-Z ]+\]) ([:a-f0-9]+) ([:a-f0-9]+) ([\d.]+)', line)
            if m :

                # collect packet infomation
                tmp_dict['type'] = m.group(1)
                tmp_dict['dst_mac'] = m.group(2)
                tmp_dict['src_mac'] = m.group(3)
                tmp_dict['time'] = m.group(4)

                # check if end
                conditions_list = json.loads(self.cf.get('end_condition', 'certain'))
                for conditions in conditions_list:
                    pkt_type = conditions.keys()[0]
                    if tmp_dict['type']  == pkt_type:
                        end_time = self.__pkt_checker([tmp_dict], conditions[pkt_type], pkt_type)
                        print '[Info] %s \t %s send a %s packet to %s'%(tmp_dict['time'], tmp_dict['dst_mac'], pkt_type, tmp_dict['src_mac'])
                        if end_time != None:
                            print "================ Handover complete =================="
                            self.__count_start_time()
                            print "End time is at "+tmp_dict['time']
                            self.end_time = tmp_dict['time']
                            print "Totally cost %f seconds."%(float(self.end_time) - float(self.possible_interval_end)) 
                            #print "Totally cost %f ~ %f seconds."%(self.end_time - self.possible_interval_end, self.end_time - self.possible_interval_init) 
                            return 
                
                # push packet to stack 
                for type_num, pkt_type in self.packet_type_list:
                    if tmp_dict['type'] == pkt_type :
                        self.packet_type_dict[pkt_type].append(tmp_dict) 
                        print '[Info] %s \t %s send a %s packet to %s'%(tmp_dict['time'], tmp_dict['dst_mac'], pkt_type, tmp_dict['src_mac'])
                        break

    def __pkt_checker(self, pkt_list, cond_list, pkt_type):
        latest_pkt_time = ""
        for pkt in pkt_list:
            for dst_cond, src_cond in cond_list:
                if pkt['dst_mac'] == dst_cond and pkt['src_mac'] == src_cond:
                    latest_pkt_time = pkt['time']

        if latest_pkt_time == "":
            return None
        else:
            return latest_pkt_time 

    def __count_start_time(self):
        start_time = self.__config_match('start_condition', 'certain')
        if start_time != None:
            print "Start is at "+ start_time
            return
        else:
            possible_interval_init = self.__config_match('start_condition', 'possible_interval_init')
            possible_interval_end  = self.__config_match('start_condition', 'possible_interval_end')
            if possible_interval_init != None and possible_interval_end != None:
                if type(possible_interval_init) == str and type(possible_interval_end) == str:
                    print "Start time is possibly at %s"%(possible_interval_end)
                    #print "Start time is possibly at %s ~ %s"%(possible_interval_init, possible_interval_end)
                    self.possible_interval_init = possible_interval_init
                    self.possible_interval_end = possible_interval_end
                elif type(possible_interval_init) == float and type(possible_interval_end) == float:
                    print "Start time is possibly at %f"%(possible_interval_end)
                    #print "Start time is possibly at %f ~ %f"%(possible_interval_init, possible_interval_end)
                    self.possible_interval_init = possible_interval_init
                    self.possible_interval_end = possible_interval_end
                else:
                    print 'In else'
                return
        print 'Failed to find start time!'
        print '[Probe Response]', self.packet_type_dict['[Probe Response]']
        print '[Beacon]', self.packet_type_dict['[Beacon]']

    def __config_match(self, tag_name, tag_index):
        conditions_list = json.loads(self.cf.get(tag_name, tag_index))
        if tag_index != 'possible_interval_init':
            for conditions in conditions_list:
                pkt_type = conditions.keys()[0]
                start_time = self.__pkt_checker(self.packet_type_dict[pkt_type], conditions[pkt_type], pkt_type)
                if start_time != None:
                    return start_time
        else:
            for conditions in conditions_list:
                pkt_type = conditions.keys()[0]
                start_time = self.__pkt_checker(self.packet_type_dict[pkt_type], conditions[pkt_type], pkt_type)
                if start_time != None:
                    return start_time
        return None


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='handover_counter')
    parser.add_argument('type', help='source of packets, must be "realtime" or "file"')
    parser.add_argument('--input', help='source file name')
    parser.add_argument('--log', default="sniff.log", help='name of log file, default is sniff.log')
    parser.add_argument('--interface', help='an interface used to capture packet')
    opts = vars(parser.parse_args())
    #print opts

    if opts['type'] == 'realtime':
        if opts['interface'] != None:
            print "================ Parameter Info =================="
            print 'Input File', opts['input']
            print 'Log File', opts['log']
            print 'Interface', opts['interface']
            c = Sniff5("realtime", opts['input'], opts['log'], '1000', opts['interface'])
            print "================ Start to catch realtime packet =================="
            c.count_roaming_time_by_realtime()
        else:
            print "Please use --interface argument to inform us the wifi interface name." 

    elif opts['type'] == 'file':
        if opts['input'] != None:
            print "================ Parameter Info =================="
            print 'Input', opts['input']
            print 'Log File', opts['log']
            print 'Interface', opts['interface']
            c = Sniff5("realtime", opts['input'], opts['log'], opts['interface'])
            print "================ Start to read log file =================="
            c.count_roaming_time_by_file()
        else:
            print "Please use -f argument to inform us the input file name." 
    else: 
        parser.print_help()


