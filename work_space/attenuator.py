import time
import sys
import serial
import os
import signal
import subprocess
import re


def signal_handler(signal, frame):
    print('[Success] Catch signal.')
    sys.exit(0)

def connect_to_serial(ser):

    try:
        if ser.isOpen():
            ser.close()
            ser.open()
        else:
            ser.open()
    except serial.serialutil.SerialException as ex:
        print "Some error was found."
        return False
    return True

def get_ap_signal(interface, ap_essid):
    a = subprocess.Popen("iwlist %s scanning"%interface, shell=True, stdout=subprocess.PIPE)
    s = a.stdout.read()
    m = re.search('Signal\slevel=(-*\d+)\sdBm[a-z\WA-Z0-9]*ESSID:"%s"'%ap_essid, s)
    n = m.group(1)

    return n

def make_dm_list(ap_signal):
    pass

if __name__ == '__main__':

    dev = sys.argv[1]
    #interface = sys.argv[2]
    #ap_essid = sys.argv[3]
    mode = sys.argv[2]

    ser = serial.Serial(
        port=dev,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
    )

    if connect_to_serial(ser): 

        print "[Success] Connect to attenuator."
        my_pid = str(os.getpid()) 
        f = open('work_space/pid', 'w')
        f.write(my_pid)
        f.close()
        print "[Success] Save process id to file."
        signal.signal(signal.SIGINT, signal_handler)
        print "[Success] Set signal handler."

        #ap_signal = get_ap_signal(interface, ap_essid)
        #dm_list = make_dm_list(ap_signal)

        mode1 = ['100']
        mode2 = []
        for _ in range(1,20):
            mode2.append(str(_*3))

        if mode == 'mode1': 
            dbm_list = mode1
        elif mode == 'mode2': 
            dbm_list = mode2
       
        print "[Success] Get dbm_list."

        for dbm in dbm_list:
            print'[Info] Reduce %s dbm'%dbm
            inStr = "V%s;"%dbm
            ser.write(inStr)
            ser.flush()
            time.sleep(5)
        ser.close()

        while True:
            time.sleep(20)
            print "[Info] After 20 sec."
