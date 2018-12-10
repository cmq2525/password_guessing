import numpy as np
from utils import *

class base_table(dict):
    def __init__(self):
        self['No'] = 0
        self['hi'] = [0, dict()]
        self['ti'] = [0, dict()]
        self['hd'] = [0, dict()]
        self['td'] = [0, dict()]
        self['total_size'] = 0

    def _insert(self, password, way):
        if way == 'No':
            self['No'] += 1
        else:
            base = password if 'i' in way else get_base(password)
            if not base in self[way][1]:
                self[way][1][base] = 0
            self[way][1][base] += 1
            self[way][0] += 1
        self['total_size'] += 1

class PriorityQueue(object):
    def __init__(self):
        self.queue = ['start']
        self.size = 0

    def isEmpty(self):
        return True if self.size == 0 else False

    def insert(self, key):
        self.size += 1
        self.queue.append(key)
        pos = self.size
        dad = int(pos/2)
        while dad > 0:
            if self.queue[pos][1] > self.queue[dad][1]:
                tmp = self.queue[dad]
                self.queue[dad] = self.queue[pos]
                self.queue[pos] = tmp
                tmp = dad
                dad = int(tmp/2)
            else:
                break

    def insert_list(self, key_list):
        for key in key_list:
            self.insert(key)

    def return_max(self):
        if not self.isEmpty:
            return self.queue[1]

    def check(self):
        if self.size != len(self.queue):
            return self.queue
        else:
            return None

    def del_max(self):
        if self.isEmpty():
            return None
        tmp = self.queue[1]
        self.queue[1] = self.queue[self.size]
        self.queue[self.size] = tmp
        max_num = self.queue.pop(self.size)
        self.size -= 1
        pos = 1
        while pos < self.size:
            try:
                # 不一定有两个子节点
                tmp_max = max(self.queue[pos*2][1], self.queue[pos*2+1][1])
                tmp_index = pos*2 + [self.queue[pos*2][1],
                                     self.queue[pos*2+1][1]].index(tmp_max)
            except:
                tmp_max = 0
            if tmp_max > self.queue[pos][1]:
                #                 print('------')
                #                 print(tmp_max)
                #                 print(self.queue[pos])
                #                 print('tmp_index:',tmp_index)
                #                 print(self.queue[tmp_index])
                tmp = self.queue[pos]
                self.queue[pos] = self.queue[tmp_index]
                self.queue[tmp_index] = tmp
                pos = tmp_index
            else:
                break
        return max_num
