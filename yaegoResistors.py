import json
from os import listdir
from os.path import isfile, join
from glob import glob

from engineering_notation import EngNumber

import smallPartDb



E12 = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82]

E24 = [10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91]

E48 = [100, 105, 110, 115, 121, 127, 133, 140, 147, 154, 162, 169, 178, 187, 196, 205, 215, 226, 237, 249, 261, 274,
        287, 301, 316, 332, 348, 365, 383, 402, 422, 442, 464, 487, 511, 536, 562, 590, 619, 649, 681, 715, 750, 787,
        825, 866, 909, 953]

E96 = [100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130, 133, 137, 140, 143, 147, 150, 154, 158, 162, 165,
        169, 174, 178, 182, 187, 191, 196, 200, 205, 210, 215, 221, 226, 232, 237, 243, 249, 255, 261, 267, 274, 280,
        287, 294, 301, 309, 316, 324, 332, 340, 348, 357, 365, 374, 383, 392, 402, 412, 422, 432, 442, 453, 464, 475,
        487, 499, 511, 523, 536, 549, 562, 576, 590, 604, 619, 634, 649, 665, 681, 698, 715, 732, 750, 768, 787, 806,
        825, 845, 866, 887, 909, 931, 953, 976]

E192 = [100, 101, 102, 104, 105, 106, 107, 109, 110, 111, 113, 114, 115, 117, 118, 120, 121, 123, 124, 126, 127, 129,
          130, 132, 133, 135, 137, 138, 140, 142, 143, 145, 147, 149, 150, 152, 154, 156, 158, 160, 162, 164, 165, 167,
          169, 172, 174, 176, 178, 180, 182, 184, 187, 189, 191, 193, 196, 198, 200, 203, 205, 208, 210, 213, 215, 218,
          221, 223, 226, 229, 232, 234, 237, 240, 243, 246, 249, 252, 255, 258, 261, 264, 267, 271, 274, 277, 280, 284,
          287, 291, 294, 298, 301, 305, 309, 312, 316, 320, 324, 328, 332, 336, 340, 344, 348, 352, 357, 361, 365, 370,
          374, 379, 383, 388, 392, 397, 402, 407, 412, 417, 422, 427, 432, 437, 442, 448, 453, 459, 464, 470, 475, 481,
          487, 493, 499, 505, 511, 517, 523, 530, 536, 542, 549, 556, 562, 569, 576, 583, 590, 597, 604, 612, 619, 626,
          634, 642, 649, 657, 665, 673, 681, 690, 698, 706, 715, 723, 732, 741, 750, 759, 768, 777, 787, 796, 806, 816,
          825, 835, 845, 856, 866, 876, 887, 898, 909, 920, 931, 942, 953, 965, 976, 988]

MinMaxE96 = [1, 10000000]

MultiFact = [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000, 100000]


class yaegoResistors():
    techType = None # APS Type
    size = "0603"
    tolerance = "F"
    packaging = "R"
    tempCoefficient = None
    tapingReel = None

    def __init__(self, techType, size, tolerance, packaging, tempCoefficient, tapingReel):
        self.techType = techType
        self.size = size
        self.tolerance = tolerance
        self.packaging = packaging
        self.tempCoefficient = tempCoefficient
        self.tapingReel = tapingReel
    
    def normalizeEngPartNumbering(self, value, multi):
        if multi == 0.01 or multi == 0.1 or multi == 1:
            vStr = str(value)
            if vStr.find(".") >= 0:
                vStr = vStr.replace(".", "R")
            else:
                vStr = vStr + "R"
            vStr = vStr.rstrip('0')
        elif multi == 10 or multi == 100 or multi == 1000 :
            vStr = str(value/1000.0)
            if vStr.find(".") >= 0:
                vStr = vStr.replace(".", "K")
            vStr = vStr.rstrip('0')
        elif 10000:
            vStr = str(value/1000000.0)
            if vStr.find(".") >= 0:
                vStr = vStr.replace(".", "M")
            vStr = vStr.rstrip('0')
        return vStr[0:4]

    def generateYaegoNumbers(self, series, minMax):
        code = 0
        yNumber = ""
        seriesNumbers = []
        for m in MultiFact:
            for value in series:
                v = value * m
                if v < minMax[0] or v > minMax[1]:
                    continue
                vStr = self.normalizeEngPartNumbering(v, m)
                yNumber = "RC" + self.size + self.tolerance + self.packaging + "-" + self.tempCoefficient + self.tapingReel
                yNumber = yNumber + vStr
                yNumber = yNumber + "P" # P -> lead free
                seriesNumbers.append(yNumber)

                #print("Value: " + str(v) + " | m: " + str(m) + " | code: " + vStr + " | yP: " + yNumber)
                code = code + 1

        return seriesNumbers

    def sizeToIndex(self, size):
        if size == "0075":
            return "D"
        if size == "0100":
            return "E"
        if size == "0201":
            return "F"
        if size == "0402":
            return "G"
        if size == "0603":
            return "H"
        if size == "0805":
            return "I"
        if size == "1206":
            return "J"
        if size == "1210":
            return "K"
        if size == "1218":
            return "L"
        if size == "2010":
            return "M"
        if size == "2512":
            return "N"
    
    def multiplicatorToIndex(self, multi):
        if multi == 0.001:
            return "Z"
        if multi == 0.01:
            return "Y"
        if multi == 0.1:
            return "X"
        if multi == 1:
            return "A"
        if multi == 10:
            return "B"
        if multi == 100:
            return "C"
        if multi == 1000:
            return "D"
        if multi == 10000:
            return "E"
        if multi == 100000:
            return "F"

    def generateValues(self, series, minMax):
        seriesValues = []
        for m in MultiFact:
            for value in series:
                v = value * m
                v = round(v, 2)
                if v < minMax[0] or v > minMax[1]:
                    continue
                seriesValues.append(str(EngNumber(v)))
        return seriesValues



if __name__ == '__main__':
    myE96Series = yaegoResistors("K", "0603", "F", "R", "", "07")
    ESeries = E96
    E96YaegoNumbers = myE96Series.generateYaegoNumbers(ESeries, MinMaxE96)
    E96Values = myE96Series.generateValues(ESeries, MinMaxE96)

    for n, v in zip(E96YaegoNumbers, E96Values):
        print(n + " -> " + str(v))