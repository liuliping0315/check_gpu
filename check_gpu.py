#!/usr/bin/env /opt/anaconda3/bin/python
import os,sys,subprocess
import time
import numpy as np
import pandas as pd

def convert_range_nodes_to_list(my_str:str):
    if r'[' in my_str:
        pre = my_str.split(r'[')[0]
        numbers = my_str.split(r'[')[1].split(r']')[0]
        all_ranges = numbers.split(',')
        my_list = []
        for one_range in all_ranges:
            if '-' in one_range:
                tmp_range = one_range.split('-')
                this_range = [int(t_tmp) for t_tmp in tmp_range]
                my_list += [ pre+str(tmp) for tmp in range(this_range[0], this_range[1]+1) ]
            else:
                my_list += [ pre+one_range ]
        return my_list
    else:
        return [my_str]

def cmd2nodelist(command = r"sinfo | grep -v down | grep -v drain | awk '{print $6}'"):
    result = subprocess.run(command, stdout=subprocess.PIPE, encoding='utf-8', shell=True)
    if result.returncode != 0:
        print("error run " + command)
        sys.exit()
    txt = result.stdout.split('\n')
    
    node_list = []
    for i in range(1,len(txt)):
        if txt[i] == '':
            continue
        node_list += convert_range_nodes_to_list(txt[i])
        #print(node_list)
    node_list.sort()
    return node_list


def get_all_state():
    node_state = ["" for i in range(50)]
    new_command = "sinfo -o '%N %T' --sort=N"
    result = subprocess.run(new_command, stdout=subprocess.PIPE, encoding='utf-8', shell=True)
    if result.returncode != 0:
        print("error run " + new_command)
        sys.exit()
    txt = result.stdout.split('\n')[1:-1]
   #print("stdout:")
   #print(result.stdout)
   #print("stdout end")
    for i in range(len(txt)):
        tmp_txt = txt[i].split()
        tmp_result = convert_range_nodes_to_list(tmp_txt[0])
        for j in range(len(tmp_result)):
            index_node = int(tmp_result[j].split('n')[1]) - 1 # "gn50" -> 49
            node_state[index_node] = tmp_txt[1]
            
    return node_state
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("running list_gpu.sh")
        os.system("bash list_gpu.sh")
        os.system("sleep 10")
    else:
        print("skip list gpu, use old info")
    #print("run `bash list_gpu.sh`, then run this script with python3 interpreter `./check_gpu.py`")
    node_states = get_all_state()
    num_cards = np.zeros((50),dtype=int)
    lost_cards = [ [] for i in range(50) ]
    nlost = [ 0 for i in range(50)]
    card_names = ["02", "03", "82", "83"]
    node_names = ["gn" + str(i+1) for i in range(50)]
    exist_card = np.zeros((50,4),dtype=int)
    error_card = np.zeros((50,4),dtype=int)
    avai_card = np.zeros((50,4),dtype=int)
    bus_names = [r"00000000:02:00.0", r"00000000:03:00.0", r"00000000:82:00.0", r"00000000:83:00.0"]
    short_bus = ["02", "03", "82", "83"]
    for i in range(50):
        try:
            fnv = open(r"/data/info/card_info/"+node_names[i],'r')
            txt = fnv.readlines()
            fnv.close()
            num_lines = len(txt)
        except IOError:
            print("read error: {}".format(node_names[i]))
            continue
        for j in range(num_lines-1):
            for k in range(4):
                if bus_names[k] in txt[j]:
                    exist_card[i,k] = 1
                    if r"ERR!" in txt[j+1]:
                        error_card[i,k] = 1
    node_states = get_all_state()
    avai_card = exist_card - error_card
    num_cards = np.sum(avai_card,axis=-1)
    num_bad_nodes = np.sum(num_cards < 4)
    #np.savetxt("num_cards.txt", num_cards, fmt="%d")
    print("num_bad_nodes: ", num_bad_nodes)
    print("node_name    node_states    avai_card       bad_card(if read error, all cards set bad)")
    bad_card = [[] for i in range(50)]
    for i in range(50):
        for j in range(4):
            if avai_card[i,j] == 0:
                bad_card[i].append(short_bus[j])
    for i in range(50):
        if num_cards[i] < 4:
            print(f"    {node_names[i]:>4s}    {node_states[i]:>10s}        {avai_card[i]}      {bad_card[i]}")
