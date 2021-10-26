import re             #用于正则表达式
import requests        #导入网络请求模块
import os              #用于获取路径
import json

def get_station():
    #发送请求获取所有车站名称，通过输入的站名称转化查询地址的参数
    url="https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9207"
    response=requests.get(url,verify=True)   #请求并进行验证
    #获取需要的车站名称
    stations=re.findall('([\u4e00-\u9fa5]+)\|([A-Z]+)',response.text)
    stations=dict(stations)         #转换为字典
    stations=str(stations)          #转换为字符串类型，否则无法写入文件
    write(stations,'stations.text')  #调用写入方法


def get_sellingtime():
    #发送请求获取所有车站开售时间
    url='https://www.12306.cn/index/script/core/common/qss.js'
    response=requests.get(url,verify=True)
    sellingtime=re.findall('{[^}]+}',response.text)   #匹配括号内所有内容
    time_js=json.loads(sellingtime[0])     #解析JSON数据
    write(str(time_js),'time.text')        #调用写入方法


def write(stations,file_name):
    file=open(file_name,'w',encoding='utf_8_sig')   #以写模式打开文件
    file.write(stations)
    file.close()

def read(file_name):
    file=open(file_name,'r',encoding='utf_8_sig')
    data=file.raedline()
    file.close()
    return data

def is_stations(file_name):
    is_stations=os.path.exists(file_name)
    return is_stations

