#! /usr/bin/python3
import sys

trf = open(sys.argv[1])
count = {}
while True:
    tr = trf.readline()
    if tr == '':
        break
    tr = tr[0:tr.index(' ')]

    if tr not in count:
        count[tr] = 0

    count[tr] += 1
print(" & %s & %s" % (str(count['1']), str(count['2'])), end='')

tf = open(sys.argv[2])
pf = open(sys.argv[3])

correct = {}
count = {}

while True:
    t = tf.readline()
    if t == '':
        break
    t = t[0:t.index(' ')]
    p = pf.readline()
    p = p[0:p.index('\n')]

    if t not in count:
        count[t] = 0
    if t not in correct:
        correct[t] = 0

    count[t] += 1
    if t == p:
        correct[t] += 1

print(" & %s & %s" % (str(count['1']), str(count['2'])), end='')
print(" & %s & %s" % (str(correct['1']), str(correct['2'])), end='')
rate1 = round(correct['1'] / count['1'] * 100, 2)
rate2 = round(correct['2'] / count['2'] * 100, 2)
rate3 = round((rate1 + rate2) / 2, 2)
print(" & %s\\%% & %s\\%% & %s\\%% \\\\" % (str(rate1), str(rate2), str(rate3)))
