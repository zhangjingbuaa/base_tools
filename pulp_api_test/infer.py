# -*- coding: utf-8 -*-
#! /usr/bin/env python
#
# 调用剑皇线上服务
# 七牛/图普/阿里/百度
#
import json
import random
import requests
from concurrent.futures import ThreadPoolExecutor
from threading import RLock
from time import sleep
import utils
lock=RLock()

__BAIDU_MAP={u'色情':0,
             u'性感':1,
             u'正常':2
}

def qpulp(url):
    """
    qpulp api
    Args:
        url : image url
    return:
        res:  dict of response. {url:xxx,label:xxx,score:xxx,review:xxx}
    """
    headers = {'Content-Type':'application/json'}
    ret = dict()
    try:
        rd = random.randint(100,9999) # CDN缓存问题
        r = requests.get(url + '?qpulp&token=' + str(rd),headers = headers,timeout = 30)
    except Exception as e:
        # http error
        with lock:
            print("%s : %s"%(url,e))
    else:
        with lock:
            if r.status_code == 200:
                r = r.json()
                ret['url'] = url
                ret['label'] = r["result"]['label']
                ret['score'] = r['result']['score']
                ret['review'] = r['result']['review']
                print(ret)
            else:
                print('%s : error code %d'%(url,r.status_code))
    return ret

def nrop(url):
    headers = {'Content-Type':'application/json'}
    ret = dict()
    try:
        r = requests.get(url + '?nrop',headers = headers,timeout = 30)
    except Exception as e:
        with lock:
            print("%s : %s"%(url,e))
    else:
        with lock:
            if r.status_code == 200:
                r = r.json()
                ret['url'] = url
                ret['label'] = r['fileList'][0]['label']
                ret['score'] = r['fileList'][0]['rate']
                ret['review'] = r['fileList'][0]['review']
                print(ret)
            else:
                print('%s : error code %d'%(url,r.status_code))
    return ret

def ali(url,sleep_time=2,retry=3):
    # 递归retry
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36','Content-Type': 'text/plain'}
    ret = dict()
    payLoad = {"data": {"imageUrls": [url], "scene": "porn"}}
    try:
        r = requests.post('http://jaq.alibaba.com/aligreen/demo/api/image/detect.json',json = payLoad,headers = headers,timeout = 30)
    except Exception as e:
        # http error
        with lock:
            if retry != 0:
                print('%s : HTTP ERROR， RETRY %d'%(url,(4-retry)))
                sleep(sleep_time)
                return ali(url,sleep_time = sleep_time*2,retry = retry-1)
            else:
                print("%s : %s"%(url,e))
    else:
        with lock:
            r = r.json()
            if r['code'] == 200:
                if r['data'][0]['code'] == '200' and r['data'][0]['images'][0]['porn']['label'] != -1:
                    label = r['data'][0]['images'][0]['porn']['label']
                    label = 2 if label == 0 else label-1
                    ret['url'] = url
                    ret['label'] = label
                    ret['score'] = r['data'][0]['images'][0]['porn']['rate']
                    print(ret)
                else:
                    if retry != 0:
                        print('%s : RESOPONSE ERROR， RETRY %d'%(url,(4-retry)))
                        sleep(sleep_time)
                        return ali(url,sleep_time = sleep_time*2,retry = retry-1)
                    else:
                        print('%s : error code %d'%(url,r['code']))
            else:
                print("%s : %s"%(url,r))
    finally:
        return ret

def _token(ak,sk):
    '''
    baidu token
    client_id 为官网获取的AK， client_secret 为官网获取的Sk
    token 有效期30天，请定期更换
    '''
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s'%(ak,sk)
    r = requests.post(host,headers = {'Content-Type': 'application/json; charset=UTF-8'})
    return r.json()['access_token']

def baidu(url,access_token):
    '''
    百度单张图片请求结果
    '''
    ret = {}
    head = {'Content-Type':'application/json;charset=utf-8'}
    request_url = 'https://aip.baidubce.com/api/v1/solution/direct/img_censor'
    request_url = request_url + "?access_token=" + access_token
    params = json.dumps({'imgUrl':url,"scenes":["antiporn"]})

    try:
        r = requests.post(request_url,data = params,headers = head,timeout = 30)
        r = r.json()
        score = r['result']['antiporn']['result']
        conclusion = r['result']['antiporn']['conclusion']
        label = __BAIDU_MAP[conclusion]
        ret['url'] = url
        ret['label'] = label
        ret['score'] = score
    except :
        print('%s : err'%(url))
    else:
        print (ret)
    return ret


def infer(data,tool,ak = None,sk = None):
    result = list()
    if tool == 'ali':
        with ThreadPoolExecutor(max_workers = 5) as executor:
            tmp = list(executor.map(ali,data))
            result = list(filter(lambda x: x,tmp))     # 剔除空dict {}

    elif tool == 'qpulp':
        with ThreadPoolExecutor(max_workers = 5) as executor:
            tmp = list(executor.map(qpulp,data))
            result = list(filter(lambda x: x,tmp))

    elif tool == 'nrop':
        with ThreadPoolExecutor(max_workers = 5) as executor:
            tmp = list(executor.map(nrop,data))
            result = list(filter(lambda x: x,tmp))
    elif tool == 'baidu':
        token = _token(ak,sk)
        for url in data.keys():
            result.append(baidu(url,token))
        result = list(filter(lambda x: x,result))
    return result

if __name__=='__main__':
    pass