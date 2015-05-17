from django.shortcuts import render
from django.http import HttpResponse

import json
import subprocess
import time
import netifaces

# Create your views here.

python_path = '../venv/bin/python2.7'

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

    iface_list = netifaces.interfaces()
    return render(request, 'index.html', {'iface_list':iface_list}) 

def read_config_file(request):
    f = open('work_space/sniff.config', 'r')
    result = f.read()
    return HttpResponse(result)


def save_config_file(request):
    if request.method == 'POST':
        file_content = request.POST.get('file_content') 
        print(file_content)
        f = open('work_space/sniff.config', 'w')
        f.write(file_content)
        f.close()
    return HttpResponse('haha')












