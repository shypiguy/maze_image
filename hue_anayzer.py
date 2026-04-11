# hue analyzer - provides functions for categorizing hues found in a set of color pixels

import multiprocessing

# intital single-threaded hue analysis functions

def huestogram(hue_list):
    hset = [0]*256
    for hue_item in hue_list:
        hset[hue_item] = hset[hue_item] + 1
    return hset
