from django.shortcuts import render
from django.http import HttpResponse

import json
import subprocess
import time
import netifaces
import configparser 

# Create your views here.

python_path = './venv/bin/python2.7'

def work(request):

    """ 
    {
        'log': 'sniff.log', 
        'sniff_type': 'realtime', 
        'dev': '/dev/ttyUSB0', 
        'input_content': 'aaaaaaaaaaaaaaa\r\nccccccccd\r\n',
        'mode': 'mode1',
        'interface': 'mon1'
    }
    """

    if request.method == 'POST':
        info_json = request.POST.get('info_dict')
        info_dict = json.loads(info_json)
        print('[Info] Show Post Data')

        if info_dict['sniff_type'] == 'realtime':

            # execute sniff program
            print('[Info]\texecute sniff program with type RealTime')
            print('Execute sniff')
            sniff_command = "%s work_space/sniff.py --interface %s --log %s %s"%(python_path, info_dict['interface'], info_dict['log'], info_dict['sniff_type'])
            print(sniff_command)
            o = subprocess.Popen(sniff_command, shell=True, stdout=subprocess.PIPE)

            time.sleep(5)

            # execute attenuator program 
            print('[Info]\texecute attenuator program with mode %s'%(info_dict['mode']))
            print('Execute attenuator')
            attenuator_command = "%s work_space/attenuator.py %s %s"%(python_path, info_dict['dev'], info_dict['mode'])
            print(attenuator_command)
            subprocess.call(attenuator_command, shell=True)
            print('attenuator done')

            result = o.stdout.read()
            print('result = ')
            print(result)

        elif info_dict['sniff_type'] == 'file':

            print('[Info]\tMake input_file')
            f = open('work_space/input_file','w')
            f.write(info_dict['input_content'])
            f.close()

            print('[Info]\texecute sniff program with type Packet Trace')
            sniff_command = "%s work_space/sniff.py --input work_space/input_file file"%(python_path)
            print(sniff_command)
            o = subprocess.Popen(sniff_command, shell=True, stdout=subprocess.PIPE)
            result = o.stdout.read()
            f = open('static/result_file', 'w')
            f.write(result.decode("utf-8"))
            f.close()

    return HttpResponse(result)

def home(request):

    subtype_list = [
        "Association Request",
        "Association Response",
        "Reassociation Request",
        "Reassociation Response",
        "Probe Response",
        "Beacon",
        "Disassociation",
    ]

    iface_list = netifaces.interfaces()
    return render(request, 'index.html', {'iface_list':iface_list, 'subtype_list':subtype_list}) 

def read_config_file(request):
    f = open('work_space/sniff.config', 'r')
    result = f.read()
    return HttpResponse(result)


def save_update_config_file(request):
    if request.method == 'POST':
        file_content = request.POST.get('file_content') 
        print(file_content)
        f = open('work_space/sniff.config', 'w')
        f.write(file_content)
        f.close()
    return HttpResponse('haha')


def save_config_file(request):

    subtype_map = {
            'Association Request':   '        {"[Association Request]": [["%(ap2_mac)s", "%(client_mac)s"]]},\n',        
            'Association Response':  '        {"[Association Response]": [["%(client_mac)s", "%(ap2_mac)s"]]},\n',
            'Reassociation Request': '        {"[Reassociation Request]": [["%(ap2_mac)s", "%(client_mac)s"]]},\n',
            'Reassociation Response':'        {"[Reassociation Response]": [["%(client_mac)s", "%(ap2_mac)s"]]},\n',
            'Probe Response':        '        {"[Probe Response]": [["%(client_mac)s", "%(ap2_mac)s"]]},\n',
            'Beacon':                '        {"[Beacon]": [["%(client_mac)s", "%(ap2_mac)s"]]},\n',
            'Disassociation':        '        {"[Disassociation]": [["%(client_mac)s", "%(ap1_mac)s"], ["%(ap1_mac)s", "%(client_mac)s"]]},\n',
    }

    print('in save_config_file')
    if request.method == 'POST':
        config_dict = json.loads(request.POST.get('config_data'))
        file_content = """[packet_type]
0 = [Association Request]
1 = [Association Response]
2 = [Reassociation Request]
3 = [Reassociation Response]
5 = [Probe Response]
8 = [Beacon]
10 = [Disassociation]\n
"""
        start_condition = "[start_condition]\n"
        start_condition += "client_mac = %s\n"%(config_dict['sta_mac'])
        start_condition += "ap1_mac = %s\n"%(config_dict['old_ap_mac'])
        start_condition += "ap2_mac = %s\n"%(config_dict['new_ap_mac'])

        for (key, value) in [('start_cond_trigger_event', 'certain'), ('start_cond_possible_init','possible_interval_init'), ('start_cond_possible_end','possible_interval_end')]:
            cond = ""
            if len(config_dict[key]) != 0:
                for subtype in config_dict[key]:
                    cond += subtype_map[subtype]
                cond = "%s = [\n%s\n    ]\n"%(value, cond[:-2])
            start_condition += cond
        #print(start_condition)

        end_condition = "\n[end_condition]\n"
        end_condition += "client_mac = %s\n"%(config_dict['sta_mac'])
        end_condition += "ap1_mac = %s\n"%(config_dict['old_ap_mac'])
        end_condition += "ap2_mac = %s\n"%(config_dict['new_ap_mac'])

        for (key, value) in [('end_cond_trigger_event', 'certain'), ('end_cond_possible_init','possible_interval_init'), ('end_cond_possible_end','possible_interval_end')]:
            cond = ""
            if len(config_dict[key]) != 0:
                for subtype in config_dict[key]:
                    cond += subtype_map[subtype]
                cond = "%s = [\n%s\n    ]\n"%(value, cond[:-2])
            end_condition += cond
        #print(end_condition)

        file_content += start_condition
        file_content += end_condition
        print(file_content)

        f = open('work_space/sniff.config', 'w')
        f.write(file_content)
        f.close()

    return HttpResponse('haha')

def get_config_file(request):
    cf = configparser.ConfigParser()
    config_file = cf.read("work_space/sniff.config") 
    client_mac = cf.get('start_condition', 'client_mac')
    #print(client_mac)

    basic_data = {
        'sta_mac':cf.get('start_condition', 'client_mac'),
        'old_ap_mac':cf.get('start_condition', 'ap1_mac'),
        'new_ap_mac':cf.get('start_condition', 'ap2_mac'),
    }

    cond_data = {
        'start_cond_trigger_event':[], 
        'start_cond_possible_init':[], 
        'start_cond_possible_end':[], 
        'end_cond_trigger_event':[], 
        'end_cond_possible_init':[], 
        'end_cond_possible_end':[], 
    };

    map_dict = {
            "certain":"_cond_trigger_event",         
            "possible_interval_init":"_cond_possible_init",
            "possible_interval_end":"_cond_possible_end"
    }

    for option in map_dict.keys():
        if cf.has_option('start_condition', option):
            for cond in json.loads(cf.get('start_condition', option)):
                if len(cond.keys()) > 0:
                    cond_data['start'+map_dict[option]].append(next (iter (cond.keys()))[1:-1])
                
    for option in map_dict.keys():
        if cf.has_option('end_condition', option):
            for cond in json.loads(cf.get('end_condition', option)):
                if len(cond.keys()) > 0:
                    cond_data['end'+map_dict[option]].append(next (iter (cond.keys()))[1:-1])

    data = {'basic_data':basic_data, 'cond_data':cond_data}
    return HttpResponse(json.dumps(data))







