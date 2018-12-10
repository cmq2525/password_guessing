import time
import re
import pickle
import pandas as pd
from utils import *
from base_ import base_table

change_dict = {
    'C': dict(zip(['No', 'C1', 'C2', 'C3', 'C4'], [0]*5)),
    'SM': dict(zip(['No', 'Yes'], [0]*2)),
    'R': dict(zip(['No', 'R1', 'R2'], [0]*3)),
    'L': dict(zip(['No', 'L1', 'L2', 'L3', 'L4', 'L5'], [0]*6)),
    'total_size': 0}

structure_dict = dict()
# e.g.: {'L8':base_table()}
segment_dict = dict()
# e.g.: {'L8':base_table()}
type_dict = dict()


def structure_hi(pwaE, pwb, hi, hi_len):
    hi_len = hi_len.copy()
    hi_len_ = hi_len.copy()
    for i in range(len(hi)):
        if hi[i] not in 'LDS':
            typ = hi[i] + hi_len_[i]
            hi_len_[i] = str(len(type_dict[typ]))
    hi_str = pwb[:sum([int(x) for x in hi_len_])]
    hi_len_.reverse()
    hi_len.reverse()
    hi = hi[::-1]

    for i in range(len(hi)):
        base_a = get_base(pwaE, type_dict)
        if not base_a in structure_dict:
            structure_dict[base_a] = base_table()
        if hi[i] in 'LDS':
            tmp = hi_str[-int(hi_len_[i]):]
            structure_dict[base_a]._insert(tmp, 'hi')
            #hi_str = hi_str[:-int(hi_len_[i])]
            pwaE = tmp + pwaE
        else:
            #hi_str = hi_str[:-len(base)]
            typ = hi[i] + hi_len[i]
            structure_dict[base_a]._insert(typ, 'ti')
            pwaE = type_dict[typ] + pwaE
        #base_hi = get_base(hi)
    return pwaE, hi_len_


def structure_ti(pwaE, pwb, ti, ti_len):
    ti_len_ = ti_len.copy()
    for i in range(len(ti)):
        if ti[i] not in 'LDS':
            typ = ti[i] + ti_len_[i]
            ti_len_[i] = len(type_dict[typ])
    ti_str = pwb[:sum([int(x) for x in ti_len_])]

    count = 0
    for i in range(len(ti)):
        base_a = get_base(pwaE, type_dict)
        if not base_a in structure_dict:
            structure_dict[base_a] = base_table()
        if ti[i] in 'LDS':
            pwaE = pwaE + ti_str[count:count+int(ti_len_[i])]
            structure_dict[base_a]._insert(
                ti_str[count:count+int(ti_len_[i])], 'ti')
            count += int(ti_len_[i])
        else:
            typ = ti[i] + ti_len[i]
            structure_dict[base_a]._insert(typ, 'ti')
            pwaE = pwaE + type_dict[typ]
            count += len(type_dict[typ])
    return pwaE, ti_len_


def structure_hd(pwaE, hd, hd_len):
    for i in range(len(hd)):
        base_a = get_base(pwaE, type_dict)
        if not base_a in structure_dict:
            structure_dict[base_a] = base_table()
        if hd[i] in 'LDS':
            hd_str = pwaE[:int(hd_len[i])]
            hd_base = get_base(hd_str, type_dict)
            pwaE = pwaE[int(hd_len[i]):]
        else:
            hd_base = hd[i] + hd_len[i]
            pwaE = pwaE[len(type_dict[hd_base]):]
        structure_dict[base_a]._insert(hd_base, 'hd')
    return pwaE


def structure_td(pwaE, td, td_len):
    td_len = td_len.copy()
    td_len.reverse()
    td = td[::-1]
    for i in range(len(td)):
        base_a = get_base(pwaE, type_dict)
        if not base_a in structure_dict:
            structure_dict[base_a] = base_table()
        if td[i] in 'LDS':
            td_str = pwaE[-int(td_len[i]):]
            td_base = get_base(td_str, type_dict)
            pwaE = pwaE[:-int(td_len[i])]
        else:
            td_base = td[i] + td_len[i]
            pwaE = pwaE[:-len(type_dict[td_base])]
        structure_dict[base_a]._insert(td_base, 'td')
    return pwaE


def structure_ins_del(pwaE, pwb):
    # 对齐structure
    base_a = get_base(pwaE, type_dict)
    base_b = get_base(pwb, type_dict)
    if base_a == base_b:
        if not base_a in structure_dict:
            structure_dict[base_a] = base_table()
        structure_dict[base_a]._insert(0, 'No')
        return
    struct_a = ''.join(re.findall(struct, base_a))
    index_a = re.findall(digit, base_a)
    struct_b = ''.join(re.findall(struct, base_b))
    index_b = re.findall(digit, base_b)

    # 'L3D4S1','L2S3'
    sub = get_substring(struct_a, struct_b)
    pos1 = struct_a.find(sub)
    pos2 = struct_b.find(sub)
    hd = struct_a[:pos1]
    hd_len = index_a[:pos1]

    td = struct_a[pos1+len(sub):]
    td_len = index_a[pos1+len(sub):]

    hi = struct_b[:pos2]
    hi_len = index_b[:pos2]

    ti = struct_b[pos2+len(sub):]
    ti_len = index_b[pos2+len(sub):]

    if hd:
        pwaE = structure_hd(pwaE, hd, hd_len)
    if td:
        pwaE = structure_td(pwaE, td, td_len)
    # 删除完之后就可以进行结构内的hi'、ti'等操作
    tmp_pwa = pwaE
    if hi:
        pwaE, hi_len = structure_hi(pwaE, pwb, hi, hi_len)
    if ti:
        pwaE, ti_len = structure_ti(pwaE, pwb, ti, ti_len)

    return tmp_pwa, pwaE, hi_len, ti_len


def structure_CLSMR(pwaE, pwb):
    # Capitalization
    edit_dist = get_edit_dist(pwaE, pwb)
    after_capitall = [get_edit_dist(Capitalization(
        pwaE, 'C'+str(x)), pwb) for x in range(1, 5)]
    max_dist = max(after_capitall)
    if max_dist > edit_dist:
        change_dict['C']['C'+str(after_capitall.index(max_dist)+1)] += 1
        pwaE = Capitalization(pwaE, 'C'+str(after_capitall.index(max_dist)+1))
    else:
        change_dict['C']['No'] += 1
    # Leet
    edit_dist = get_edit_dist(pwaE, pwb)
    after_leet = [get_edit_dist(Leet(pwaE, 'L'+str(x)), pwb)
                  for x in range(1, 6)]
    max_dist = max(after_leet)
    if max_dist > edit_dist:
        change_dict['L']['L'+str(after_leet.index(max_dist)+1)] += 1
        pwaE = Leet(pwaE, 'L'+str(after_leet.index(max_dist)+1))
    else:
        change_dict['L']['No'] += 1
    # Reverse
    edit_dist = get_edit_dist(pwaE, pwb)
    after_reverse = [get_edit_dist(
        Reverse(pwaE, get_base(pwaE, type_dict), 'R'+str(x)), pwb) for x in range(1, 3)]
    max_dist = max(after_reverse)
    if max_dist > edit_dist:
        change_dict['R']['R'+str(after_reverse.index(max_dist)+1)] += 1
        pwaE = Reverse(pwaE, 'R'+str(after_reverse.index(max_dist)+1))
    else:
        change_dict['R']['No'] += 1
    # Substring_moving
    edit_dist = get_edit_dist(pwaE, pwb)
    sm = Substring_moving(pwaE, get_base(pwaE, type_dict))
    if get_edit_dist(sm, pwb) > edit_dist:
        pwaE = sm
        change_dict['SM']['Yes'] += 1
    else:
        change_dict['SM']['No'] += 1
    change_dict['total_size'] += 1
    return pwaE


def segment_ins_del(tmp_pwa, tmp_pwb):
    base_a = get_base(tmp_pwa, type_dict)
    base_b = get_base(tmp_pwb, type_dict)
    struct_a = re.findall(struct, base_a)
    struct_b = re.findall(struct, base_b)
    index_a = re.findall(digit, base_a)
    index_b = re.findall(digit, base_b)
    count_a = 0
    count_b = 0
    # print(base_a,base_b)
    for i in range(len(index_a)):
        if struct_a[i] not in 'LDS':
            base_a = struct_a[i] + index_a[i]
            base_b = struct_b[i] + index_b[i]
            if not base_a in segment_dict:
                segment_dict[base_a] = base_table()
            if index_a[i] != index_b[i]:
                segment_dict[base_a]._insert(base_b, 'hd')
            else:
                segment_dict[base_a]._insert(0, 'No')
            count_a += len(type_dict[base_a])
            count_b += len(type_dict[base_b])
            continue

        tmp_a = tmp_pwa[count_a:count_a+int(index_a[i])]
        tmp_b = tmp_pwb[count_b:count_b+int(index_b[i])]
        count_a += int(index_a[i])
        count_b += int(index_b[i])

        sub = get_substring(tmp_a, tmp_b)
        len_sub = len(sub)
        start1 = tmp_a.find(sub)
        start2 = tmp_b.find(sub)
        hd_ = tmp_a[:start1]
        td_ = tmp_a[start1+len_sub:]
        hi_ = tmp_b[:start2]
        ti_ = tmp_b[start2+len_sub:]
        if not (hd_ + td_ + hi_ + ti_):
            # do not change!
            base_a = get_base(tmp_a, type_dict)
            if not base_a in segment_dict:
                segment_dict[base_a] = base_table()
            segment_dict[base_a]._insert(0, 'No')
            continue
        if hd_:
            base_a = get_base(tmp_a, type_dict)
            if not base_a in segment_dict:
                segment_dict[base_a] = base_table()
            segment_dict[base_a]._insert(get_base(hd_, type_dict), 'hd')
            tmp_a = tmp_a[len(hd_):]
        if td_:
            base_a = get_base(tmp_a, type_dict)
            if not base_a in segment_dict:
                segment_dict[base_a] = base_table()
            segment_dict[base_a]._insert(get_base(td_, type_dict), 'td')
            tmp_a = tmp_a[:-len(td_)]
        if hi_:
            base_a = get_base(tmp_a, type_dict)
            if not base_a in segment_dict:
                segment_dict[base_a] = base_table()
            segment_dict[base_a]._insert(hi_, 'hi')
            tmp_a = hi_ + tmp_a
        if ti_:
            base_a = get_base(tmp_a, type_dict)
            if not base_a in segment_dict:
                segment_dict[base_a] = base_table()
            segment_dict[base_a]._insert(ti_, 'ti')
            tmp_a = tmp_a + ti_


def reconstruct(pwa, pwb):
    base_a = get_base(pwa, type_dict)
    base_b = get_base(pwb, type_dict)
    struct_a = re.findall(struct, base_a)
    struct_b = re.findall(struct, base_b)
    index_a = re.findall(digit, base_a)
    index_b = re.findall(digit, base_b)

    pwaE = structure_hd(pwa, struct_a, index_a)
    pwaE = structure_ti(pwaE, pwb, struct_b, index_b)
    return pwaE


def train_pair(pwa, pwb):
    edit_dist = get_edit_dist(pwa, pwb)
    if edit_dist < 0.5:
        reconstruct(pwa, pwb)
        return -1
    # check C L SM R
    pwaE = structure_CLSMR(pwa, pwb)
    if pwaE == pwb:
        return 1
    # structure_level ins and del
    result = structure_ins_del(pwaE, pwb)
    if result != None:
        tmp_pwa, pwaE, hi_len, ti_len = result
        if not ti_len:
            # 因为a[:-0] = ''，所以如果没有ti的话tmp_pwb就会变成空了
            tmp_pwb = pwb[sum([int(x) for x in hi_len]):]
        else:
            tmp_pwb = pwb[sum([int(x) for x in hi_len]):-
                          sum([int(x) for x in ti_len]):]
########################################
    else:
        tmp_pwa = pwaE
        tmp_pwb = pwb
    segment_ins_del(tmp_pwa, tmp_pwb)


def train(file_name):
    start = time.time()
    with open(file_name, 'rb') as pkl_file:
        train_set = pickle.load(pkl_file)
    for i in range(len(train_set)):
        type_dict.clear()
        pwa, pwb = get_type(train_set[i], type_dict)
        train_pair(pwa, pwb)
    end = time.time()
    print('time:', end-start)
