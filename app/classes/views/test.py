import scipy.misc
import math

ints = [i for i in range(1, 11)] + [15, 20]
ints.extend([i for i in range(25, 100, 25)])
ints.extend([i for i in range(100, 600, 100)])
path_lens = [2 * i - 1 for i in ints]
sqs = [i * i for i in ints]
path_ratio = [path_lens[i]/sqs[i] for i in range(len(ints))]
lns = [math.log(i) for i in path_lens]
sqs_ratio = [lns[i]/sqs[i] for i in range(len(ints))]
ps = [math.pow(1-sqs_ratio[i], path_lens[i]) for i in range(len(ints))]

lists = [ints, path_lens, sqs, path_ratio, lns, sqs_ratio, ps]

print('\tints\tpath\tsqs\t\tpath_r\tlns\t\tsqs_r\tps')
for r in range(0, len(ints)):
    i = ints[r]

    cols = ['{:.2f}'.format(l[r]) for l in lists]
    row = '{}'.format('\t'.join(cols))
    print('\t{}'.format(row))


