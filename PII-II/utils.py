import re
struct = re.compile('D|S|L')
digit = re.compile('\d+')
struct_prob_thres = 1e-3
segment_prob_thres = 1e-5
total_prob_thres = 1e-7


def Capitalization(str1, way='C1'):
    way = int(way[1])
    if str1:
        return {1: lambda x: x.upper(),
                2: lambda x: x[0].upper()+x[1:],
                3: lambda x: x.lower(),
                4: lambda x: x[0].lower()+x[1:]}[way](str1)


def Substring_moving(str1, structure):
    index_list = re.findall(digit, structure)
    if len(index_list) < 2:
        return str1
    else:
        # 交换前两个结构的位置，如L5D3->D3L5
        len1 = int(index_list[0])
        len2 = int(index_list[1])
        return str1[len1:len1+len2] + str1[:len1] + str1[len1+len2:]


def Reverse(str1, structure, way='R1'):
    way = int(way[1])
    if way == 1:
        return str1[::-1]
    else:
        len_list = re.findall(digit, structure)
        count = 0
        final_str = list()
        for i in len_list:
            tmp = str1[count:count+int(i)]
            count += int(i)
            final_str.append(tmp[::-1])

        return ''.join(final_str)


def Leet(str1, way='L1'):
    way = int(way[1])
    return {1: lambda x: x.replace('a', '@'),
            2: lambda x: x.replace('s', '$'),
            3: lambda x: x.replace('o', '0'),
            4: lambda x: x.replace('i', '1'),
            5: lambda x: x.replace('e', '3')}[way](str1)

# 得到str1和str2的最大公共子串


def get_substring(str1, str2):
    len1 = len(str1)
    len2 = len(str2)
    max_num = 0
    p = -1
    sim_m = [[0 for i in range(len2+1)]for j in range(len1+1)]
    for i in range(len1):
        for j in range(len2):
            if str1[i] == str2[j]:
                sim_m[i+1][j+1] = sim_m[i][j] + 1
            if sim_m[i+1][j+1] > max_num:
                max_num = sim_m[i+1][j+1]
                p = i + 1
    return str1[p-max_num:p]


def get_edit_dist(str1, str2):
    sub = get_substring(str1, str2)
    return len(sub)*2/(len(str1)+len(str2))


def get_base(password):
    if not password:
        return ''
    password = re.sub(r'[a-zA-Z]', 'L', password, count=0, flags=0)
    password = re.sub(r'[0-9]', 'D', password, count=0, flags=0)
    password = re.sub(r'[^a-zA-Z0-9]', 'S', password, count=0, flags=0)
    combo = password[0]
    parsed_base = ''
    for i in range(1, len(password)):
        if password[i] == combo[-1]:
            combo += password[i]
        else:
            parsed_base += combo[0] + str(len(combo))
            combo = password[i]
    parsed_base += combo[0] + str(len(combo))
    return parsed_base
