import re
import time
import bisect
import pandas as pd
import numpy as np
from base_ import PriorityQueue
from utils import *
from train import structure_dict, segment_dict, change_dict


def generate_struct(guess_queue, pwa, prob):
    base = get_base(pwa)
    try:
        dic = structure_dict[base]
    except KeyError as e:
        #         pwa = ''
        #         base = ''
        #         dic = structure_dict[base]
        return
    total_size = dic['total_size']

    # no
#     pwaE = pwa
#     tmp_prob = prob*dic['No']/total_size
#     if tmp_prob>struct_prob_thres:
#         guess_queue.insert((pwaE,tmp_prob))
    # hd
    tmp_prob = prob*dic['hd'][0]/total_size
    flag = 0
    if tmp_prob < struct_prob_thres:
        flag = 1
    for hd_base in dic['hd'][1]:
        if flag:
            # 整个hd的概率都不可能高于struct_prob_thres
            break
        tmp_prob = prob*dic['hd'][1][hd_base]/total_size
        if tmp_prob < struct_prob_thres:
            continue
        index_list = re.findall(digit, hd_base)
        len_del = sum([int(x) for x in index_list])
        if len_del > len(pwa):
            # 删不了
            continue
        if get_base(pwa[:len_del]) == hd_base:
            pwaE = pwa[len_del:]
            guess_queue.insert((pwaE, tmp_prob))
    # td
    tmp_prob = prob*dic['td'][0]/total_size
    flag = 0
    if tmp_prob < struct_prob_thres:
        flag = 1
    for td_base in dic['td'][1]:
        if flag:
            break
        tmp_prob = prob*dic['td'][1][td_base]/total_size
        if tmp_prob < struct_prob_thres:
            continue
        index_list = re.findall(digit, td_base)
        len_del = sum([int(x) for x in index_list])
        if len_del > len(pwa):
            # 删不了
            continue
        if get_base(pwa[-len_del:]) == td_base:
            pwaE = pwa[:-len_del]
            guess_queue.insert((pwaE, tmp_prob))
    # hi
    tmp_prob = prob*dic['hi'][0]/total_size
    flag = 0
    if tmp_prob < struct_prob_thres:
        flag = 1
    for hi in dic['hi'][1]:
        if flag:
            break
        tmp_prob = prob*dic['hi'][1][hi]/total_size
        if tmp_prob < struct_prob_thres:
            continue
        pwaE = hi + pwa
        guess_queue.insert((pwaE, tmp_prob))
    # ti
    tmp_prob = prob*dic['ti'][0]/total_size
    flag = 0
    if tmp_prob < struct_prob_thres:
        flag = 1
    for ti in dic['ti'][1]:
        if flag:
            break
        tmp_prob = prob*dic['ti'][1][ti]/total_size
        if tmp_prob < struct_prob_thres:
            continue
        pwaE = pwa + ti
        guess_queue.insert((pwaE, tmp_prob))


def generate_segment(guess_queue, pwa, prob):
    base = get_base(pwa)
    struct_a = re.findall(struct, base)
    index_a = re.findall(digit, base)
    count = 0
    prev_pwa = ''
    for i in range(len(index_a)):
        prev_pwa = pwa[:count]
        this_pwa = pwa[count:count+int(index_a[i])]
        count += int(index_a[i])
        remain_pwa = pwa[count:]
        #pwaE = prev_pwa + this_guess + remain_pwa
        tmp_base = struct_a[i] + index_a[i]
        try:
            dic = segment_dict[tmp_base]
        except KeyError as e:
            return
        total_size = dic['total_size']
        # hd
        tmp_prob = prob*dic['hd'][0]/total_size
        flag = 0
        if tmp_prob < segment_prob_thres:
            flag = 1
        for hd_base in dic['hd'][1]:
            if flag:
                # 整个hd的概率都不可能高于segment_prob_thres
                break
            tmp_prob = prob*dic['hd'][1][hd_base]/total_size
            if tmp_prob < segment_prob_thres:
                continue
            index_list = re.findall(digit, hd_base)
            len_del = sum([int(x) for x in index_list])
            if len_del > len(this_pwa):
                # 删不了
                continue
            if get_base(this_pwa[:len_del]) == hd_base:
                pwaE = prev_pwa + this_pwa[len_del:] + remain_pwa
                guess_queue.insert((pwaE, tmp_prob))
        # td
        tmp_prob = prob*dic['td'][0]/total_size
        flag = 0
        if tmp_prob < segment_prob_thres:
            flag = 1
        for td_base in dic['td'][1]:
            if flag:
                # 整个td的概率都不可能高于segment_prob_thres
                break
            tmp_prob = prob*dic['td'][1][td_base]/total_size
            if tmp_prob < segment_prob_thres:
                continue
            index_list = re.findall(digit, td_base)
            len_del = sum([int(x) for x in index_list])
            if len_del > len(this_pwa):
                # 删不了
                continue
            if get_base(this_pwa[-len_del:]) == td_base:
                pwaE = prev_pwa + this_pwa[:-len_del] + remain_pwa
                guess_queue.insert((pwaE, tmp_prob))
        # hi
        tmp_prob = prob*dic['hi'][0]/total_size
        flag = 0
        if tmp_prob < segment_prob_thres:
            flag = 1
        for hi in dic['hi'][1]:
            if flag:
                break
            tmp_prob = prob*dic['hi'][1][hi]/total_size
            if tmp_prob < segment_prob_thres:
                continue
            pwaE = prev_pwa + hi + this_pwa + remain_pwa
            guess_queue.insert((pwaE, tmp_prob))
        # ti
        tmp_prob = prob*dic['ti'][0]/total_size
        flag = 0
        if tmp_prob < segment_prob_thres:
            flag = 1
        for ti in dic['ti'][1]:
            if flag:
                break
            tmp_prob = prob*dic['ti'][1][ti]/total_size
            if tmp_prob < segment_prob_thres:
                continue
            pwaE = prev_pwa + this_pwa + ti + remain_pwa
            guess_queue.insert((pwaE, tmp_prob))


def generate_change(guess_queue, pwa, prob):
    if not pwa:
        return
    base = get_base(pwa)
    total_size = change_dict['total_size']
    # Capitalization
    for way in change_dict['C']:
        if way == 'No':
            continue
        pwaE = Capitalization(pwa, way)
        tmp_prob = prob*change_dict['C'][way]/total_size
        if tmp_prob < total_prob_thres:
            continue
        guess_queue.insert((pwaE, tmp_prob))
    # Leet
    for way in change_dict['L']:
        if way == 'No':
            continue
        pwaE = Leet(pwa, way)
        tmp_prob = prob*change_dict['L'][way]/total_size
        if tmp_prob < total_prob_thres:
            continue
        guess_queue.insert((pwaE, tmp_prob))
    # SubstringMoving
    for way in change_dict['SM']:
        if way == 'No':
            continue
        pwaE = Substring_moving(pwa, base)
        tmp_prob = prob*change_dict['SM'][way]/total_size
        if tmp_prob < total_prob_thres:
            continue
        guess_queue.insert((pwaE, tmp_prob))
    # Reverse
    for way in change_dict['R']:
        if way == 'No':
            continue
        pwaE = Reverse(pwa, base, way)
        tmp_prob = prob*change_dict['R'][way]/total_size
        if tmp_prob < total_prob_thres:
            continue
        guess_queue.insert((pwaE, tmp_prob))


def generate(pwa, guess_time):
    start = time.time()
    struct_guess_list = list()
    guess_queue = PriorityQueue()
    guess_queue.insert((pwa, 1))
    count = 0
    while not guess_queue.isEmpty():
        pwa, prob = guess_queue.del_max()
        if prob < struct_prob_thres or count > guess_time:
            break
        struct_guess_list.append((pwa, prob))
        generate_struct(guess_queue, pwa, prob)
        count += 1

    # 同一个口令，只存最高的概率
    struct_guess_list = dict(sorted(struct_guess_list, key=lambda x: x[1]))
# ======================================================================
    # segement
    segment_guess_list = list()
    guess_queue = PriorityQueue()
    guess_queue.insert_list(struct_guess_list.items())
    count = 0
    while not guess_queue.isEmpty():
        pwa, prob = guess_queue.del_max()
        if prob < segment_prob_thres or count > guess_time:
            break
        segment_guess_list.append((pwa, prob))
        generate_segment(guess_queue, pwa, prob)
        count += 1
#     print('time:',time.time()-start)
#     start = time.time()
#     print(len(segment_guess_list))
    segment_guess_list = dict(sorted(segment_guess_list, key=lambda x: x[1]))

# ========================================================================
    # change
    change_guess_list = list()
    guess_queue = PriorityQueue()
    guess_queue.insert_list(segment_guess_list.items())
    count = 0
    while not guess_queue.isEmpty():
        pwa, prob = guess_queue.del_max()
        if prob < total_prob_thres or count > guess_time:
            break
        if len(pwa) >= 6 and len(pwa) <= 12:
            change_guess_list.append((pwa, prob))
        generate_change(guess_queue, pwa, prob)
        count += 1
#     print('time2:',time.time()-start)
#     print(len(change_guess_list))
    change_guess_list = dict(sorted(change_guess_list, key=lambda x: x[1]))
    return change_guess_list


def test_result_bi(file_name,num,guess_num):
    name_list = [1,5,10,50,100,500,1000]
    num_list = [0]*7
    if num==-1:
        num = len(test_set)
    test_set = pd.read_csv(file_name,encoding='gb18030')
    test_set = test_set.values
    
    index_list = np.random.permutation(len(test_set))
    for i in range(num):
        type_dict = dict()
        #pwa,pwb = get_type(test_set[index_list[i]],type_dict)
        pwa,pwb = test_set[index_list[i]]
        result =  generate(pwa,guess_num+1)
        result = sorted(result,key=lambda x:x[1],reverse=True)[1:]
        result_list = [x[0] for x in result]

        try:
            pos = result_list.index(pwb)
        except:
            pos = -1
        if pos == -1:
            continue
        else:
            for i in range(bisect.bisect(name_list,pos),7):
                num_list[i] += 1

    for i in range(len(num_list)):
        num_list[i] = num_list[i]/num
    print(name_list)
    print(num_list)
