# -*- coding:utf-8 -*-
#! /usr/bin/env python
#
# Ground Truth 文件读取
# 计算剑皇混淆矩阵与相关指标
#
import json
import numpy as np
import pprint

_LABEL_MAP = {"pulp":0,
              "sexy":1,
              "normal":2}

def read_url_list(gt_file):
    """
    read url list
    url\tlabel
    """
    gt = dict()
    with open(gt_file,'r') as f:
        for line in f:
            line = line.strip()
            url = line.split('\t')[0]
            label = line.split('\t')[-1]
            gt[url] = int(label)
    return gt

def read_json(gt_file):
    gt = dict()
    with open(gt_file,'r') as f:
        for line in f:
            line = json.loads(line.strip())
            url = line['url']
            label = line['label'][0]['data'][0]['class']
            gt[url] = _LABEL_MAP[label]
    return gt

def get_true_pred(gt_dict,pred_dict_list):
    y_true=list()
    y_pred=list()
    for pred in pred_dict_list:
        if pred and pred['url'] in gt_dict:
            y_true.append(gt_dict[pred['url']])
            y_pred.append(pred['label'])
    return y_true,y_pred

def logs(infered,log_path):
    with open(log_path,'w',encoding = 'utf-8') as f:
        json.dump(infered,f,indent=4,ensure_ascii = False)

class Metrics(object):
    """
    metrix class
    """
    def __init__(self,y_true,y_pred):
        self.__y_true = y_true
        self.__y_pred = y_pred
        self.__cnf_matrix = np.zeros((3,3),dtype = int)
        self.__classes = ['pulp','sexy','normal']
        self.__eps = 1e-9

    def confusion_matrix(self):
        """
        calc confusion_matrix and return
        """
        y_true = np.array(self.__y_true)
        y_pred = np.array(self.__y_pred)
        for i in range(3):
            for j in range(3):
                self.__cnf_matrix[i][j] = np.where(y_pred[np.where(y_true == i)] == j)[0].shape[0]
        return self.__cnf_matrix

    def accuracy(self):
        return float(self.__cnf_matrix[0][0] + self.__cnf_matrix[1][1] + self.__cnf_matrix[2][2]) / (np.sum(self.__cnf_matrix) + self.__eps)

    def pulp_recall(self):
        return float(self.__cnf_matrix[0][0]) / (np.sum(self.__cnf_matrix[0]) + self.__eps)

    def pulp_precision(self):
        return float(self.__cnf_matrix[0][0]) / (np.sum(self.__cnf_matrix,axis = 0)[0] + self.__eps)

    def sexy_recall(self):
        return float(self.__cnf_matrix[1][1]) / (np.sum(self.__cnf_matrix,axis = 1)[1] + self.__eps)

    def sexy_precision(self):
        return float(self.__cnf_matrix[1][1]) / (np.sum(self.__cnf_matrix,axis = 0)[1] + self.__eps)

    def normal_recall(self):
        return float(self.__cnf_matrix[2][2]) / (np.sum(self.__cnf_matrix,axis = 1)[2] + self.__eps)

    def normal_precision(self):
        return float(self.__cnf_matrix[2][2]) / (np.sum(self.__cnf_matrix,axis = 0)[2] + self.__eps)


    def plot_confusion_matrix(self):
        import matplotlib.pyplot as plt
        import itertools
        np.set_printoptions(precision=2)
        plt.figure()
        plt.imshow(self.__cnf_matrix, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title('Confusion Matrix')
        plt.colorbar()
        tick_marks = np.arange(len(self.__classes))
        plt.xticks(tick_marks, self.__classes, rotation=45)
        plt.yticks(tick_marks, self.__classes)

        fmt = 'd'
        thresh = self.__cnf_matrix.max() / 2.
        for i, j in itertools.product(range(self.__cnf_matrix.shape[0]), range(self.__cnf_matrix.shape[1])):
            plt.text(j, i, format(self.__cnf_matrix[i, j], fmt),
                    horizontalalignment="center",
                    color="white" if self.__cnf_matrix[i, j] > thresh else "black")
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.tight_layout()
        plt.show()

if __name__=='__main__':
    pass