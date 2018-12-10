import re
import time
import bisect
import pickle
import pandas as pd
import numpy as np
from base_ import PriorityQueue
from utils import *
from train import structure_dict, segment_dict, change_dict

type_dict = dict()


def get_new_base(base_a, base_b, way):
    if not base_a:
        return base_b
    struct_a = re.findall(struct, base_a)
    struct_b = re.findall(struct, base_b)
    index_a = re.findall(digit, base_a)
    index_b = re.findall(digit, base_b)

    if way == 'hd':
        # 只需要比最后一个位置的数是否相同
        pos = len(index_b)-1
        if index_a[pos] == index_b[pos]:
            tmp_base = ''
        else:
            if struct_a[pos] not in 'LDS':
                tmp_base = struct_b[pos] + index_b[pos]
            else:
                tmp_base = struct_a[pos] + \
                    str(int(index_a[pos])-int(index_b[pos]))
        for i in range(pos+1, len(index_a)):
            tmp_base = tmp_base + struct_a[i] + index_a[i]

    elif way == 'td':
        # 只需要比第一个位置的数是否相同
        pos = len(index_a)-len(index_b)
        tmp_base = ''
        for i in range(0, pos):
            tmp_base = tmp_base + struct_a[i] + index_a[i]
        if index_a[pos] != index_b[0]:
            if struct_a[pos] not in 'LDS':
                tmp_base = tmp_base + struct_b[pos] + index_b[pos]
            else:
                tmp_base = tmp_base + struct_a[pos] + \
                    str(int(index_a[pos])-int(index_b[0]))

    elif way == 'hi':
        # 只需要比较base_b的最后一个位置
        if struct_b[-1] == struct_a[0]:
            if struct_b[-1] in 'LDS':
                if len(index_b[-1]) == 1:
                    base_b = base_b[:-2]
                else:
                    base_b = base_b[:-3]
                index_a[0] = str(int(index_a[0])+int(index_b[-1]))
        tmp_base = base_b
        for i in range(len(index_a)):
            tmp_base = tmp_base + struct_a[i] + index_a[i]

    elif way == 'ti':
        # 只需要比较base_b的第一个位置
        if struct_b[0] == struct_a[-1]:
            if struct_a[-1] in 'LDS':
                if len(index_a[-1]) == 1:
                    base_a = base_a[:-2]
                else:
                    base_a = base_a[:-3]
                index_b[0] = str(int(index_b[0])+int(index_a[-1]))
        tmp_base = base_a
        for i in range(len(index_b)):
            tmp_base = tmp_base + struct_b[i] + index_b[i]
    return tmp_base


def generate_struct(guess_queue, pwa, prob, base):
    try:
        dic = structure_dict[base]
    except KeyError as e:
        return
    total_size = dic['total_size']
    struct_a = re.findall(struct, base)
    index_a = re.findall(digit, base)
    tmp_base = list()
    for j in range(len(index_a)):
        tmp_base.append(struct_a[j] + index_a[j])

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

        # 不需要判断，一定能删
        struct_list = re.findall(struct, hd_base)
        index_list = re.findall(digit, hd_base)
        for i in range(len(index_list)):
            if struct_list[i] not in 'LDS':
                try:
                    index_list[i] = len(
                        type_dict[struct_list[i]+index_list[i]])
                except:
                    continue
        len_del = sum([int(x) for x in index_list])
        pwaE = pwa[len_del:]
        tmp_base = get_new_base(base, hd_base, 'hd')
        guess_queue.insert((pwaE, tmp_prob, tmp_base))
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
        # 不需要判断，一定能删
        struct_list = re.findall(struct, td_base)
        index_list = re.findall(digit, td_base)
        for i in range(len(index_list)):
            if struct_list[i] not in 'LDS':
                try:
                    index_list[i] = len(
                        type_dict[struct_list[i]+index_list[i]])
                except:
                    continue
        len_del = sum([int(x) for x in index_list])
        pwaE = pwa[:-len_del]

        tmp_base = get_new_base(base, td_base, 'td')
        guess_queue.insert((pwaE, tmp_prob, tmp_base))
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
        # A2从'A2'变成事实上的信息
        if hi in type_dict.keys():
            hi = type_dict[hi]
        pwaE = hi + pwa
        struct_list = re.findall(struct, hi)
        index_list = re.findall(digit, hi)

        try:
            if (len(struct_list) == len(index_list)) and len(struct_list) > 0:
                hi = ''
                for i in range(len(struct_list)):
                    hi += type_dict[struct_list[i]+index_list[i]]
        except:
            continue

        hi_base = get_base(hi, type_dict)
        tmp_base = get_new_base(base, hi_base, 'hi')
        guess_queue.insert((pwaE, tmp_prob, tmp_base))
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

        if ti in type_dict.keys():
            ti = type_dict[ti]
        pwaE = pwa + ti
        struct_list = re.findall(struct, ti)
        index_list = re.findall(digit, ti)

        try:
            if (len(struct_list) == 1) and (len(index_list) == 1):
                ti = ''
                for i in range(len(struct_list)):
                    ti += type_dict[struct_list[i]+index_list[i]]
        except:
            continue

        ti_base = get_base(ti, type_dict)
        tmp_base = get_new_base(base, ti_base, 'ti')
        guess_queue.insert((pwaE, tmp_prob, tmp_base))


def generate_segment(guess_queue, pwa, prob, base):
    struct_a = re.findall(struct, base)
    index_a = re.findall(digit, base)
    pwa_list = list()
    count = 0
    for i in range(len(index_a)):
        if struct_a[i] in 'LDS':
            pwa_list.append(pwa[count:count+int(index_a[i])])
            count += int(index_a[i])
        else:
            info = type_dict[struct_a[i]+index_a[i]]
            pwa_list.append(info)
            count += int(len(info))
    tmp_base = list()
    for j in range(len(index_a)):
        tmp_base.append(struct_a[j] + index_a[j])

    for i in range(len(index_a)):
        prev_pwa = ''.join(pwa_list[:i])
        this_pwa = pwa_list[i]
        remain_pwa = ''.join(pwa_list[i+1:])
        #pwaE = prev_pwa + this_guess + remain_pwa
        try:
            dic = segment_dict[struct_a[i] + index_a[i]]
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
            # 个人信息直接替换就好
            if struct_a[i] not in 'LDS':
                try:
                    pwaE = prev_pwa + type_dict[hd_base] + remain_pwa
                except:
                    continue
                tmp = tmp_base[i]
                tmp_base[i] = hd_base
                guess_queue.insert((pwaE, tmp_prob, ''.join(tmp_base)))
                tmp_base[i] = tmp
                continue

            index_list = re.findall(digit, hd_base)
            len_del = sum([int(x) for x in index_list])
            pwaE = prev_pwa + this_pwa[len_del:] + remain_pwa

            tmp = tmp_base[i]
            tmp_base[i] = get_new_base(tmp_base[i], hd_base, 'hd')
            guess_queue.insert((pwaE, tmp_prob, ''.join(tmp_base)))
            tmp_base[i] = tmp
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
            pwaE = prev_pwa + this_pwa[:-len_del] + remain_pwa

            tmp = tmp_base[i]
            tmp_base[i] = get_new_base(tmp_base[i], td_base, 'td')
            guess_queue.insert((pwaE, tmp_prob, ''.join(tmp_base)))
            tmp_base[i] = tmp
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
            hi_base = get_base(hi, type_dict)
            tmp = tmp_base[i]
            tmp_base[i] = get_new_base(tmp_base[i], hi_base, 'hi')
            guess_queue.insert((pwaE, tmp_prob, ''.join(tmp_base)))
            tmp_base[i] = tmp
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
            ti_base = get_base(ti, type_dict)
            tmp = tmp_base[i]
            tmp_base[i] = get_new_base(tmp_base[i], ti_base, 'ti')
            guess_queue.insert((pwaE, tmp_prob, ''.join(tmp_base)))
            tmp_base[i] = tmp


def generate_change(guess_queue, pwa, prob, base):
    if not pwa:
        return
    struct_a = re.findall(struct, base)
    index_a = re.findall(digit, base)
    tmp_base = list()
    for j in range(len(index_a)):
        tmp_base.append(struct_a[j] + index_a[j])

    total_size = change_dict['total_size']
    # Capitalization
    for way in change_dict['C']:
        if way == 'No':
            continue
        pwaE = Capitalization(pwa, way)
        tmp_prob = prob*change_dict['C'][way]/total_size
        if tmp_prob < total_prob_thres:
            continue
        guess_queue.insert((pwaE, tmp_prob, base))
    # Leet
    for way in change_dict['L']:
        if way == 'No':
            continue
        pwaE = Leet(pwa, way)
        tmp_prob = prob*change_dict['L'][way]/total_size
        if tmp_prob < total_prob_thres:
            continue
        guess_queue.insert((pwaE, tmp_prob, base))
    # SubstringMoving
    for way in change_dict['SM']:
        if way == 'No':
            continue
        pwaE = Substring_moving(pwa, base)
        tmp_prob = prob*change_dict['SM'][way]/total_size
        if tmp_prob < total_prob_thres:
            continue
        if len(tmp_base) > 1:
            tmp = tmp_base[0]
            tmp_base[0] = tmp_base[1]
            tmp_base[1] = tmp
        guess_queue.insert((pwaE, tmp_prob, ''.join(tmp_base)))
    # Reverse
    for way in change_dict['R']:
        if way == 'No':
            continue
        pwaE = Reverse(pwa, base, way)
        tmp_prob = prob*change_dict['R'][way]/total_size
        if tmp_prob < total_prob_thres:
            continue
        guess_queue.insert((pwaE, tmp_prob, ''.join(tmp_base[::-1])))
# 以每个元素的第一个值为主键，只存第一次出现的元素


def del_dup(a):
    result_list = list()
    key_dict = dict()
    for elem in a:
        try:
            if key_dict[elem[0]]:
                continue
        except:
            key_dict[elem[0]] = 1
            result_list.append(elem)
    return result_list


def generate(pwa, guess_time):
    struct_guess_list = list()
    guess_queue = PriorityQueue()
    guess_queue.insert((pwa, 1, get_base(pwa, type_dict)))
    count = 0
    while not guess_queue.isEmpty():
        pwa, prob, base = guess_queue.del_max()
        if prob < struct_prob_thres or count > guess_time:
            break
        struct_guess_list.append((pwa, prob, base))
        generate_struct(guess_queue, pwa, prob, base)
        count += 1

    # 同一个口令，只存最高的概率
    struct_guess_list = del_dup(sorted(struct_guess_list, key=lambda x: x[1]))
# ======================================================================
    # segement
    segment_guess_list = list()
    guess_queue = PriorityQueue()
    guess_queue.insert_list(struct_guess_list)
    count = 0
    while not guess_queue.isEmpty():
        pwa, prob, base = guess_queue.del_max()
        if prob < segment_prob_thres or count > guess_time:
            break
        segment_guess_list.append((pwa, prob, base))
        generate_segment(guess_queue, pwa, prob, base)
        count += 1
#     print('time:',time.time()-start)
#     start = time.time()
#     print(len(segment_guess_list))
    segment_guess_list = del_dup(
        sorted(segment_guess_list, key=lambda x: x[1]))

# ========================================================================
    # change
    change_guess_list = list()
    guess_queue = PriorityQueue()
    guess_queue.insert_list(segment_guess_list)
    count = 0
    while not guess_queue.isEmpty():
        pwa, prob, base = guess_queue.del_max()
        if prob < total_prob_thres or count > guess_time:
            break
        if len(pwa) >= 6 and len(pwa) <= 12:
            change_guess_list.append((pwa, prob, base))
        generate_change(guess_queue, pwa, prob, base)
        count += 1
    change_guess_list = del_dup(sorted(change_guess_list, key=lambda x: x[1]))
    return change_guess_list


def test_result_pkl(file_name, num, guess_num):
    with open(file_name, 'rb') as pkl_file:
        test_set = pickle.load(pkl_file)
    name_list = [1, 5, 10, 50, 100, 500, 1000]
    num_list = [0]*7
    index_list = np.random.permutation(len(test_set))
    for i in range(num):
        type_dict.clear()
        pwa, pwb = get_type(test_set[index_list[i]], type_dict)
        result = generate(pwa, guess_num+1)
        result = sorted(result, key=lambda x: x[1], reverse=True)[1:]
        result_list = [x[0] for x in result]

        try:
            pos = result_list.index(pwb)
        except:
            pos = -1
        if pos == -1:
            continue
        else:
            for i in range(bisect.bisect(name_list, pos), 7):
                num_list[i] += 1

    for i in range(len(num_list)):
        num_list[i] = num_list[i]/num
    print(name_list)
    print(num_list)
