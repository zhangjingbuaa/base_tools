# -*- coding:utf-8 -*-
#! /usr/bin/env python
# 测试七牛、图谱、阿里剑皇指标 
#
import sys
import argparse
import json
import infer
import utils
import numpy as np

__NAME = {'qpulp':u'七牛',
          'nrop':u'图普',
          'ali':u'阿里',
          'baidu':u'百度'}

def argparser():
    parser = argparse.ArgumentParser(description = '剑皇测试工具，可测试【七牛、图普、阿里、百度】')
    parser.add_argument('--gt',type = str,required = True,
                        help = 'labeled url list')
    parser.add_argument('--tool',type = str,choices = ['qpulp','nrop','ali','baidu','tencent'],required = True,
                        help = '七牛: qpulp. 图普: nrop. 阿里: ali. 百度: baidu.')
    parser.add_argument('--log',type = str,help = 'log path')
    parser.add_argument('--vis',action = "store_true",default = False,help = 'plot confusion_matrix, default = False')
    parser.add_argument('--ak',type = str,help = 'baidu ak')
    parser.add_argument('--sk',type = str,help = 'baidu sk')
    return parser.parse_args()


def main():
    args=argparser()
    # json 格式的 ground truth
    gt_dict = utils.read_json(args.gt)
    # gt_dict = utils.read_url_list(args.gt)
    infered_dict_list = infer.infer(gt_dict,args.tool,ak = args.ak,sk = args.sk)
    if args.log:
        utils.logs(infered_dict_list,args.log)
    y_true,y_pred=utils.get_true_pred(gt_dict,infered_dict_list)
    metric = utils.Metrics(y_true,y_pred)

    conf_matrix = metric.confusion_matrix()
    acc = metric.accuracy()
    pulp_recall = metric.pulp_recall()
    pulp_precision = metric.pulp_precision()
    sexy_recall = metric.sexy_recall()
    sexy_precision = metric.sexy_precision()
    normal_recall = metric.normal_recall()
    normal_precision = metric.normal_precision()

    print('\n')
    print('【%s】剑皇测试'%__NAME[args.tool])
    print('~'*50)
    print('Ground Truth: ')
    print('总样本:      %d'%len(gt_dict))
    print('有效识别样本: %d'%np.sum(conf_matrix))
    
    print('~'*50)
    print('测试集分布： ')
    print('%d 个色情样本'%(np.sum(conf_matrix,axis=1)[0]))
    print('%d 个性感样本'%(np.sum(conf_matrix,axis=1)[1]))
    print('%d 个正常样本'%(np.sum(conf_matrix,axis=1)[2]))

    print('~'*50)
    print('模型指标： ')
    print('accuracy:         %f '%acc)
    print('pulp_recall:      %f '%pulp_recall)
    print('pulp_precision:   %f '%pulp_precision)
    print('sexy_recall:      %f '%sexy_recall)
    print('sexy_precision:   %f '%sexy_precision)
    print('normal_recall:    %f '%normal_recall)
    print('normal_precision: %f '%normal_precision)

    print('~'*50)
    print('Confusion Matrix: ')
    print(conf_matrix)
    print('\n')

    if args.vis:
        metric.plot_confusion_matrix()

if __name__=='__main__':
    main()
