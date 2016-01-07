# # -*- coding: utf-8 -*-
from params import ANNOTATION_STATUS
import random


def random_generator():
    content = 'Cu,01:01:01,01:02:01,some comments'
    status = random.choice(ANNOTATION_STATUS)
    return {'line': content, 'status': status}


def n_random_generator(n):
    for i in range(n):
        x = random_generator()
        x.update({'index': i+1})
        yield x


def n_random_lines(n):
    lines = [x for x in n_random_generator(n)]
    return lines


if __name__ == '__main__':
    print n_random_lines(10)
