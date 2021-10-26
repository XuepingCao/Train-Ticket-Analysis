from get_stations import *

data=[]   #保存车次消息
data_type=[]   #保存车次分类后的数据

today_train_list=[]   #保存今天列车信息，已经处理是否有票
three_train_list=[]   #保存三天列车信息，已经处理是否有票
five_train_list=[]    #保存五天列车信息，已经处理是否有票
today_list=[]         #保存今天列车信息，未处理是否有票
three_list=[]         #保存三天列车信息，未处理是否有票
five_list=[]          #保存五天列车信息，未处理是否有票

station_name_list=[]    #保存起售车站名称列表
station_time_list=[]    #保存起售车站对应时间列表

#查询所有车票信息
def query(date,from_station,to_station):
    data.clear()
    data_type.clear()
    url='https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs={}&ts={}&date={}&flag=N,N,Y'.format(from_station,to_station,date)
    #发送查询请求
    response=requests.get(url)
    #将JSON数据转换为字典类型，通过键值对取数据
    result=response.json()
    result=result['data']['result']
    #判断车站文件是否存在
    if is_stations('stations.text'):
        stations=eval(read('stations.text'))   #读取所有车站并转换为字典类型
        if len(result) != 0:
            for i in result:
                #分割数据并添加到列表中
                tmp_list=i.split('|')
                from_station=list(stations.keys())[list(stations.values()).index(tmp_list[6])]
                to_station=list(stations.keys())[list(stations.values()).index(tmp_list[7])]
                #创建座位数组，由于返回的座位数据中含有空值，所以将空改成"--"，这样好识别
                seat=[tmp_list[3],from_station,to_station,tmp_list[8],tmp_list[9],tmp_list[10],tmp_list[32],tmp_list[31],tmp_list[30],
                      tmp_list[21],tmp_list[23],tmp_list[33],tmp_list[28],tmp_list[24],tmp_list[29],tmp_list[26]]
                newSeat=[]
                #循环将座位信息中的空值，改成"--"这样好识别
                for s in seat:
                    if s=='':
                        s='--'
                    else:
                        s=s
                    newSeat.append(s)
                data.append(newSeat)
        print(data)
        return data


#卧铺票查询
def is_ticket(tmp_list,from_station,to_station):
    #判断高级软卧、软卧、硬卧任何一个有票的话，就说明该趟列车有卧铺车票
    if tmp_list[21]=='有' or tmp_list[23]=='有' or tmp_list[28]=='有':
        tmp_tem='有'
    else:
        #判断高级软卧、软卧、硬卧对应的如果是数字说明也有票，其他为无票
        if tmp_list[21].isdigit() or tmp_list[23].isdigit() or tmp_list[28].isdigit():
            tmp_tem='有'
        else:
            tmp_tem='无'
    #创建新的座位列表，显示某趟列车是否有卧铺票
    new_seat=[tmp_list[3],from_station,to_station,tmp_list[8],tmp_list[9],tmp_list[10],tmp_tem]
    return new_seat


#卧铺售票分析数据
def query_ticket_analysis(date,from_station,to_station,which_day):
    #查询请求地址
    url='https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs={}&ts={}&date={}&flag=N,N,Y'.format(date,from_station,to_station)
    #发送查询请求
    response=requests.get(url)
    #将JSON数据转换为字典类型，通过键值对取数据
    result=response.json()
    result=result['data']['result']
    #判断车站文件是否存在
    if is_stations('stations.text'):
        #读取所有车站信息并转换为字典类型
        stations=eval(read('stations.text'))
        #判断返回数据是否为空
        if len(result) != 0:
            for i in result:
                #分割数据并添加到列表中
                tmp_list=i.split('|')
                #从车站库中找到对应的车站名称
                from_station=list(stations.keys())[list(stations.values()).index(tmp_list[6])]
                to_station=list(stations.keys())[list(stations.values()).index(tmp_list[7])]
                #创建座位数组，其中包含高级软卧、软卧、硬卧
                seat=[tmp_list[3],from_station,to_station,tmp_list[8],tmp_list[9],tmp_list[10],tmp_list[21],tmp_list[23],tmp_list[28]]
                #判断今天的车次信息
                if which_day==1:
                    #将高铁、动、C开头的车次排除
                    if seat[0].startswith('G')==False and seat[0].startswith('D')==False and seat[0].startswith('C')==False:
                        #将高级软卧、软卧、硬卧未处理信息添加到列表中
                        today_list.append(seat)
                        #判断某车次是否有票
                        new_seat=is_ticket(tmp_list,from_station,to_station)
                        #将判断后的车次信息添加至对应的列表当中
                        today_train_list.append(new_seat)
                if which_day==3:
                    if seat[0].startswith('G')==False and seat[0].startswith('D')==False and seat[0].startswith('C')==False:
                        three_list.append(seat)
                        new_seat = is_ticket(tmp_list, from_station, to_station)
                        three_train_list.append(new_seat)
                if which_day==5:
                    if seat[0].startswith('G') == False and seat[0].startswith('D') == False and seat[0].startswith('C') == False:
                        five_list.append(seat)
                        new_seat = is_ticket(tmp_list, from_station, to_station)
                        five_train_list.append(new_seat)
    #return today_train_list,three_train_list,five_train_list


def query_time(station):
    station_name_list.clear()     #清空起售车站名称列表数据
    station_time_list.clear()     #清空起售车站对应时间列表数据
    stations=eval(read('time.text'))   #读取所有车站并转换为字典类型
    url='https://www.12306.cn/index/otn/index12306/queryAllCacheSaleTime'  #请求地址
    #表单参数，station参数为需要搜索车站的英文缩写
    from_data={"station_telecode":station}
    response=requests.post(url,data=from_data,verify=True)     #请求并进行验证
    response.encoding='utf-8'      #对请求所返回的数据进行编码
    json_data=json.loads(response.text)    #解析JSON数据
    data=json_data.get('data')     #获取JSON中可用数据，也就是查询车站所对应的站名
    for i in data:
        if i in stations:          #在站名时间文件中，判断是否存在该站名
            station_name_list.append(i)
    for name in station_name_list:
        time=stations.get(name)    #通过站名获取对应时间
        station_time_list.append(time)
    return station_name_list,station_time_list     #将列表信息返回
