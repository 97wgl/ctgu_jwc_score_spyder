import numpy as np
import operator
import os

# KNN还算是比较简单的分类算法，而且这里也是最朴素的KNN
def KNN(k, trainSet, testSet, trainLabel):
    # 训练集的行数
    dataSetSize = trainSet.shape[0] 
    # 将testSet拓展成和训练集同样规模的矩阵
    extendTestSet = np.tile(testSet, (dataSetSize, 1))
    # 计算训练集和测试集的距离
    distances = np.sqrt(np.sum((trainSet - extendTestSet) ** 2, axis=1))
    # 将距离进行排序后的索引
    sortedDistancesIndex = distances.argsort()
    labelCount = {}
    # 选出最接近的k个点，并且计算权重（即出现的次数）
    for i in range(k):
        vote = trainLabel[sortedDistancesIndex[i]]
        labelCount[vote] = labelCount.get(vote, 0) + 1
    # 在k个点里面选出出现次数最多的一个点
    sortedLabelCount = sorted(labelCount.items(), key=operator.itemgetter(1), reverse=True)
    # print(sortedLabelCount)
    return sortedLabelCount[0][0]

# 将imgtxt转化为数组
def dataToArray(filename):
    arr = []
    with open(filename) as fh:
        for i in range(11):
            line = fh.readline()
            for j in range(11):
                arr.append(int(line[j]))
    return arr

# 获取文件前缀xxx_yyy.txt (取xxx)
def getFilePre(filename):
    result = filename.split("_")[0]
    return result

# 建立训练数据集
def traindata(path):
    labels = []
    trainfiles = os.listdir(path)
    rowCount = len(trainfiles)
    # 用一个数组存储所有训练数据  
    #     行数：len(trainfiles)
    #     列数：11X11=121
    trainArr = np.zeros((rowCount, 121))
    for i in range(rowCount):
        currFileName = trainfiles[i]
        currLabel = getFilePre(currFileName)
        labels.append(currLabel)
        trainArr[i, :] = dataToArray(path + currFileName)
    return trainArr, labels

# 测试
def dataTest(k, trainSetPath, testSetPath):
    trainArr, labels = traindata(trainSetPath)
    testFileList = os.listdir(testSetPath)
    code = ""
    for i in range(len(testFileList)):
        currFileName = testFileList[i]
        if (testFileList[i].split(".")[-1] == "txt"):    
            currTestArr = dataToArray(testSetPath + currFileName)
            code += KNN(k, trainArr, currTestArr, labels)
    return code