
'Compute the recall/precision/fscore of the units boundaries.'


import argparse
import copy
import sys

import numpy as np
import beer

def load_transcript(path):
    with open(path, 'r') as f:
        trans = {}
        for line in f:
            tokens = line.strip().split()
            trans[tokens[0]] = tokens[1:]
    return trans

def boundaries(utt):
    boundaries = []
    frame = 1
    current_unit = utt[0]
    for frame, unit in enumerate(utt[1:], start=2):
        if unit != current_unit:
            current_unit = unit
            boundaries.append(frame)
    return np.array(boundaries)


def get_hits(ref_bounds_, hyp_bounds, delta=1):
    hits = 0
    ref_bounds = copy.deepcopy(ref_bounds_)
    for b in hyp_bounds:
        diff = np.abs(b - ref_bounds)
        min_dist = diff.min()
        min_i = diff.argmin()
        if min_dist <= delta:
            hits += 1
            ref_bounds[min_i] = 1000000
    return hits


def load_mapping(path):
    mapping = {}
    with open(path, 'r') as f:
        for line in f:
            try:
                p1, p2 = line.strip().split()
                mapping[p1] = p2
            except ValueError:
                pass
    return mapping


def map_trans(trans, mapfile):
    new_trans = {}
    oov_i = 1
    for utt, utt_trans in trans.items():
        tmp = []
        for token in utt_trans:
            if token not in mapfile:
                mapfile[token] = '<oov_' + str(oov_i) +'>'
                oov_i += 1
            new_token = mapfile[token]
            tmp.append(new_token)
        new_trans[utt] = tmp
    return new_trans



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delta', default=2, type=int,
                        help='acceptance threshold (in frame) to consider a ' \
                             'boundary a "hit"')
    parser.add_argument('--mapping', help='mapping')
    parser.add_argument('ref', help='reference frame transcription')
    parser.add_argument('hyp', help='hypothesis frame transcription')
    args = parser.parse_args()

    ref = load_transcript(args.ref)
    hyp = load_transcript(args.hyp)

    if args.mapping:
        mapping = load_mapping(args.mapping)
        hyp = map_trans(hyp, mapping)
        ref = map_trans(ref, mapping)

    hits = 0
    ref_bounds_count = 0
    hyp_bounds_count = 0
    for utt in ref:
        ref_bounds = boundaries(ref[utt])
        hyp_bounds = boundaries(hyp[utt])
        hits += get_hits(ref_bounds, hyp_bounds, delta=args.delta)
        ref_bounds_count += len(ref_bounds)
        hyp_bounds_count += len(hyp_bounds)

        if len(ref_bounds) != len(hyp_bounds):
            print(utt)

    if ref_bounds_count > 0:
        recall = hits / ref_bounds_count
    else:
        recall = 0.
    if hyp_bounds_count > 0:
        prec = hits / hyp_bounds_count
    else:
        prec = 0.
    if recall + prec > 0:
        fscore = 2 * (prec * recall) / (prec + recall)
    else:
        fscore = 0.

    print('recall (%), precision (%), f-score (%)')
    print(f'{100 * recall:.2f}, {100 * prec:.2f}, {100 * fscore: .2f}')


if __name__ == "__main__":
    main()

