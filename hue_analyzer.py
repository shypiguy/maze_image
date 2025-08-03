# hue analyzer - provides functions for categorizing hues found in a set of color pixels

import multiprocessing

# takes a list of hue values as input (integers in range(256))
# produces a list of the count of input items by hue value

def huestogram_atomic(hue_list):
    hset = [0]*256
    for hue_item in hue_list:
        if hue_item > 0 and hue_item < 256:
            hset[hue_item] = hset[hue_item] + 1
    return hset

# divides large lists into 64 or 65 sub lsits and pool maps them to
# huestogram_atomic for faster analysis

def huestogram(hue_list):
    llen = len(hue_list)
    chunk_size = llen
    chunk_count = 1
    last_chunk_size = 0
    if llen > 64:
        chunk_size = int(llen/64)
        chunk_count = 64
        last_chunk_size = llen-(64*chunk_size)
        hue_set_list = []
        for chunk_num in range(64):
            hue_set_list += [hue_list[chunk_num*chunk_size:(chunk_num+1)*chunk_size]]
        hue_set_list += [hue_list[64*chunk_size:]]
        hist_list= []
        #if __name__ == "__main__":
        pool = multiprocessing.Pool()
        hist_list = pool.map(huestogram_atomic, hue_set_list)
        final_hist = [0]*256
        for hist in hist_list:
            final_hist = [sum(x) for x in zip(final_hist, hist)]
        return final_hist
    else:
        return huestogram_atomic(hue_list)

def peak_hue_and_v (hue_list, tgt_pct):
    hgram = huestogram(hue_list)
    targetsum = tgt_pct/100*len(hue_list)
    peaksum = 0
    peakhue = 0
    peakvariance = 0
    variance = 0
    while peaksum < targetsum:
        for basehue in range(255):
            setsum = 0
            for hue in range(basehue-variance,basehue+variance+1):
                if hue < 0:
                    hue = hue+255
                if hue > 254:
                    hue = hue-255
                setsum = setsum + hgram[hue]
            if setsum > peaksum:
                peaksum = setsum
                peakhue = basehue
                peakvariance = variance
        variance = variance + 1
    return [peakhue, peakvariance]

def hue_chunks(hue_list):
    llen = len(hue_list)
    chunk_size = llen
    chunk_count = 1
    last_chunk_size = 0
    if llen > 64:
        chunk_size = int(llen/64)
        chunk_count = 64
        last_chunk_size = llen-(64*chunk_size)
        hue_set_list = []
        for chunk_num in range(64):
            hue_set_list += [hue_list[chunk_num*chunk_size:(chunk_num+1)*chunk_size]]
        hue_set_list += [hue_list[64*chunk_size:]]
        return hue_set_list
    else:
        return [hue_list]
        
    
