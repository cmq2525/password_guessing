import re
import queue
struct = re.compile('[A-Z]')
digit = re.compile('\d+')
struct_prob_thres = 1e-3
segment_prob_thres = 1e-5
total_prob_thres = 1e-7

def get_base(password,type_dict):
    if not password:
        return ''
    
#     if '1' in mask:
#         base = ''
#         combo = ''
#         for i in range(len(mask)):
#             if mask[i] == '0':
#                 combo += password[i]
#             else:
#                 base += get_base(combo)
#                 base += password[i]
#                 combo = ''
#         return base
    parse_dict = dict()
    reverse_type_dict = dict(zip(type_dict.values(),type_dict.keys()))
    info_list = sorted(type_dict.values(),key=lambda x:len(x),reverse=True)
    q = queue.Queue()
    q.put(password)
    type_list = list()
    while not q.empty():
        tmp_pass = q.get()
        for i in range(len(info_list)):
            info = info_list[i]
            index = tmp_pass.find(info)
            if index!= -1:
                q.put(tmp_pass[:index])
                q.put(tmp_pass[index+len(info):])
                parse_dict[info] = reverse_type_dict[info]
                type_list.append(reverse_type_dict[info])
                info_list = info_list[i:]
                break

    mask = password
    mask = re.sub(r'[a-zA-Z]','L',mask,count=0,flags=0)
    mask = re.sub(r'[0-9]','D',mask,count=0,flags=0)
    mask = re.sub(r'[^a-zA-Z0-9()]','S',mask, count=0, flags=0)   
    mask = list(mask)
    for typ in type_list:
        info = type_dict[typ]
        ind = password.index(type_dict[typ])
        password = list(password)
        password[ind:ind+len(type_dict[typ])] = ['!']*len(type_dict[typ])
        password = ''.join(password)
        mask[ind:ind+len(info)] = [typ] * len(info)
        mask[ind+len(info)-1] = 'END'

    combo = mask[0]
    count = 1
    parsed_base = list()
    for i in range(1,len(mask)):
        if mask[i]!=combo:
            if combo in 'LDS':
                parsed_base.append(combo+str(count))
            else:
                if combo != 'END':
                    parsed_base.append(combo)
            count = 1
            combo = mask[i]
        else:
            count += 1
    if combo in 'LDS':
        parsed_base.append(combo+str(count))
    else:
        if combo != 'END':
            parsed_base.append(combo)

    return ''.join(parsed_base)
def get_type(data,type_dict):
    if len(data) == 8:
        email,pwa,name,identity,account,phone,xx,pwb = data
    elif len(data) == 7:
        email,pwa,name,identity,account,phone,pwb = data
    birth = identity[6:14]
    name = 'Unknown'
#     name = info_dict['name']
#     birth = info_dict['birth']
#     phone = info_dict['phone']
#     email = info_dict['email']
#     account = info_dict['account']
#     identity = info_dict['identity']

#     type_dict['N1'] = ''.join(name.split())
#     type_dict['N2'] = ''.join([x[0] for x in name.split()])
#     type_dict['N3'] = name.split()[-1]
#     type_dict['N4'] = name.split()[0]
#     type_dict['N5'] = name.split()[0][0] + name.split()[-1]
#     type_dict['N6'] = name.split()[-1] + name.split()[0][0]
#     type_dict['N7'] = name.split()[-1][0].upper()+name.split()[-1][1:]
    
    type_dict['B1'] = birth
    type_dict['B2'] = birth[4:] + birth[:4]
    type_dict['B3'] = birth[6:] + birth[4:6] + birth[:4]
    type_dict['B4'] = birth[4:]
    type_dict['B5'] = birth[:4]
    type_dict['B6'] = birth[:6]
    type_dict['B7'] = birth[4:6] + birth[:4]
    type_dict['B8'] = birth[2:]
    type_dict['B9'] = birth[4:] + birth[2:4]
    type_dict['B10'] = birth[6:] + birth[4:6] + birth[2:4]
    type_dict['A1'] = account
    a2 = re.findall(re.compile('[a-z]+'),account)
    if a2:
        type_dict['A2'] = a2[0]
    a3 = re.findall(re.compile('\d+'),account)
    if a3:
        type_dict['A3'] = a3[0]

    type_dict['E1'] = re.findall(re.compile('[a-z0-9]+'),email)[0]
    e2 = re.findall(re.compile('[a-z]+'),email)
    if e2:
        type_dict['E2'] = e2[0]
    e3 = re.findall(re.compile('\d+'),email)
    if e3:
        type_dict['E3'] = e3[0]
    type_dict['P1'] = phone
    type_dict['P2'] = phone[:3]
    type_dict['P3'] = phone[-4:]
    if identity:
        type_dict['I1'] = identity[-4:]
        type_dict['I2'] = identity[:6]
        type_dict['I3'] = identity[:3]
    
    #排除掉长度过小的噪声，如用户名cmq1，则1会被识别成A2
    key_list = list(type_dict.keys())
    for k in key_list:
        if len(type_dict[k])<3 and not 'N' in k:
            del type_dict[k]
    return pwa,pwb
def Capitalization(str1,way='C1'):
    way = int(way[1])
    if str1:
        return {1:lambda x:x.upper(),
                2:lambda x:x[0].upper()+x[1:],
                3:lambda x:x.lower(),
                4:lambda x:x[0].lower()+x[1:]}[way](str1)
def Substring_moving(str1,structure):
    index_list = re.findall(digit,structure)
    if len(index_list)<2:
        return str1
    else:
        #交换前两个结构的位置，如L5D3->D3L5
        len1 = int(index_list[0])
        len2 = int(index_list[1])
        return str1[len1:len1+len2] + str1[:len1] + str1[len1+len2:]
def Reverse(str1,structure,way='R1'):
    way = int(way[1])
    if way==1:
        return str1[::-1]
    else:
        len_list = re.findall(digit,structure)
        count = 0
        final_str = list()
        for i in len_list:
            tmp = str1[count:count+int(i)]
            count += int(i)
            final_str.append(tmp[::-1])
            
        return ''.join(final_str)
def Leet(str1,way='L1'):
    way = int(way[1])
    return {1:lambda x:x.replace('a','@'),
            2:lambda x:x.replace('s','$'),
            3:lambda x:x.replace('o','0'),
            4:lambda x:x.replace('i','1'),
            5:lambda x:x.replace('e','3')}[way](str1)

#得到str1和str2的最大公共子串
def get_substring(str1,str2):
    len1 = len(str1)
    len2 = len(str2)
    max_num = 0
    p = -1
    sim_m = [[0 for i in range(len2+1)]for j in range(len1+1)]
    for i in range(len1):
        for j in range(len2):
            if str1[i]==str2[j]:
                sim_m[i+1][j+1] = sim_m[i][j] + 1
            if sim_m[i+1][j+1]>max_num:
                max_num = sim_m[i+1][j+1]
                p = i + 1
    return str1[p-max_num:p]
def get_edit_dist(str1,str2):
    sub = get_substring(str1,str2)
    return len(sub)*2/(len(str1)+len(str2))
