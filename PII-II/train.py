import time
import re
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


def structure_hi(pwaE, hi_len=None, hi_str=None):
    hi_len = hi_len.copy()
    hi_len.reverse()
    for i in hi_len:
        base_a = get_base(pwaE)
        tmp = hi_str[-int(i):]
        hi_str = hi_str[:-int(i)]
        pwaE = tmp + pwaE

        #base_hi = get_base(hi)
        if not base_a in structure_dict:
            structure_dict[base_a] = base_table()
        structure_dict[base_a]._insert(tmp, 'hi')
    return pwaE


def structure_ti(pwaE, ti_len=None, ti_str=None):
    count = 0
    for i in ti_len:
        base_a = get_base(pwaE)
        pwaE = pwaE + ti_str[count:count+int(i)]
        #base_ti = get_base(ti)
        if not base_a in structure_dict:
            structure_dict[base_a] = base_table()
        structure_dict[base_a]._insert(ti_str[count:count+int(i)], 'ti')
        count += int(i)
    return pwaE


def structure_hd(pwaE, hd_len=None):
    for i in hd_len:
        hd_str = pwaE[:int(i)]
        base_a = get_base(pwaE)
        pwaE = pwaE[int(i):]
        #base_hd = get_base(hd)
        if not base_a in structure_dict:
            structure_dict[base_a] = base_table()
        structure_dict[base_a]._insert(hd_str, 'hd')
    return pwaE


def structure_td(pwaE, td_len=None):
    td_len = td_len.copy()
    td_len.reverse()
    for i in td_len:
        td_str = pwaE[-int(i):]
        base_a = get_base(pwaE)
        pwaE = pwaE[:-int(i)]
        #base_td = get_base(td)
        if not base_a in structure_dict:
            structure_dict[base_a] = base_table()
        structure_dict[base_a]._insert(td_str, 'td')
    return pwaE


def structure_ins_del(pwaE, pwb):
    # 对齐structure
    base_a = get_base(pwaE)
    base_b = get_base(pwb)
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
    #hd_str = pwaE[:sum([int(x) for x in hd_len])]
    td = struct_a[pos1+len(sub):]
    td_len = index_a[pos1+len(sub):]
    #td_str = pwaE[-sum([int(x) for x in td_len]):]
    hi = struct_b[:pos2]
    hi_len = index_b[:pos2]
    hi_str = pwb[:sum([int(x) for x in hi_len])]
    ti = struct_b[pos2+len(sub):]
    ti_len = index_b[pos2+len(sub):]
    ti_str = pwb[-sum([int(x) for x in ti_len]):]

    if hd:
        pwaE = structure_hd(pwaE, hd_len)
    if td:
        pwaE = structure_td(pwaE, td_len)
    tmp_pwa = pwaE
    # 删除完之后就可以进行结构内的hi'、ti'等操作
    if hi:
        pwaE = structure_hi(pwaE, hi_len, hi_str)
    if ti:
        pwaE = structure_ti(pwaE, ti_len, ti_str)

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
        Reverse(pwaE, get_base(pwaE), 'R'+str(x)), pwb) for x in range(1, 3)]
    max_dist = max(after_reverse)
    if max_dist > edit_dist:
        change_dict['R']['R'+str(after_reverse.index(max_dist)+1)] += 1
        pwaE = Reverse(pwaE, 'R'+str(after_reverse.index(max_dist)+1))
    else:
        change_dict['R']['No'] += 1
    # Substring_moving
    edit_dist = get_edit_dist(pwaE, pwb)
    sm = Substring_moving(pwaE, get_base(pwaE))
    if get_edit_dist(sm, pwb) > edit_dist:
        pwaE = sm
        change_dict['SM']['Yes'] += 1
    else:
        change_dict['SM']['No'] += 1
    change_dict['total_size'] += 1
    return pwaE


def segment_ins_del(tmp_pwa, tmp_pwb):
    base_a = get_base(tmp_pwa)
    base_b = get_base(tmp_pwb)
    index_a = re.findall(digit, base_a)
    index_b = re.findall(digit, base_b)
    count_a = 0
    count_b = 0
    for i in range(len(index_a)):
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
            base_a = get_base(tmp_a)
            if not base_a in segment_dict:
                segment_dict[base_a] = base_table()
            segment_dict[base_a]._insert(0, 'No')
            continue
        if hd_:
            base_a = get_base(tmp_a)
            if not base_a in segment_dict:
                segment_dict[base_a] = base_table()
            segment_dict[base_a]._insert(hd_, 'hd')
            tmp_a = tmp_a[len(hd_):]
        if td_:
            base_a = get_base(tmp_a)
            if not base_a in segment_dict:
                segment_dict[base_a] = base_table()
            segment_dict[base_a]._insert(td_, 'td')
            tmp_a = tmp_a[:-len(td_)]
        if hi_:
            base_a = get_base(tmp_a)
            if not base_a in segment_dict:
                segment_dict[base_a] = base_table()
            segment_dict[base_a]._insert(hi_, 'hi')
            tmp_a = hi_ + tmp_a
        if ti_:
            base_a = get_base(tmp_a)
            if not base_a in segment_dict:
                segment_dict[base_a] = base_table()
            segment_dict[base_a]._insert(ti_, 'ti')
            tmp_a = tmp_a + ti_


def reconstruct(pwa, pwb):
    base_a = get_base(pwa)
    base_b = get_base(pwb)
    index_a = re.findall(digit, base_a)
    index_b = re.findall(digit, base_b)

    pwaE = structure_hd(pwa, index_a)
    pwaE = structure_ti(pwaE, index_b, pwb)
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


def train():
    train_df = pd.read_csv(
        'D:\cmq\PII-II model\csdn-renren_train.csv', encoding='gb18030')
    start = time.time()
    for i in range(len(train_df)):
        train_pair(train_df.loc[i, 'pwa'], train_df.loc[i, 'pwb'])
    end = time.time()
    print('time:', end-start)
