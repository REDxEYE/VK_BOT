from random import *


def FullMerge(F1Name, F2Name):
    F1 = open(F1Name, 'rb').read()
    F2 = open(F2Name, 'rb').read()

    f = 0
    while F2 != b'':
        f += 1
        # for I in range(50):
        startpoint = randint(0, int(len(F2)))
        endpoint = randint(startpoint, startpoint + int(len(F2)))
        insertpoint = randint(0, len(F1))
        if len(F2) < 2:
            endpoint = len(F2)
            startpoint = 0
        # print(startpoint,endpoint,F2)
        F1 = F1[:insertpoint] + F2[startpoint:endpoint] + F1[insertpoint + 1:]
        F2 = F2[:startpoint] + F2[endpoint:]
        # print(startpoint,endpoint,F2)
        # if f==450:
        #    break
    F = open(F1Name, 'wb')
    F.write(F1)
    F.close()


def Merge(F1Name, F2Name):
    F1 = open(F1Name, 'rb').read()
    F1Orig = F1
    F2 = open(F2Name, 'rb').read()

    for _ in range(10):
        # for I in range(50):
        # startpoint = randint(0,int(len(F2)))
        # endpoint = randint(startpoint,startpoint+int(len(F2)))
        insertpoint = randint(0, len(F1))
        # random.shuffle(F1)
        # print(startpoint,endpoint,F2)
        F1 = F1[:insertpoint] + F1Orig + F1[insertpoint + 1:]

        # print(startpoint,endpoint,F2)

    return F1
