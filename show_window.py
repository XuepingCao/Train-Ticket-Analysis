import datetime
import time
import sys
from window import Ui_MainWindow #导入主窗体UI类
#导入PyQt5
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from chart import PlotCanvas
from query_all import *

#窗体初始化类
class Main(QMainWindow,Ui_MainWindow):

    def __init__(self):
        super(Main,self).__init__()
        self.setupUi(self)

def show_MainWindow():
    app=QApplication(sys.argv)         #创建Application对象，作为GUI主程序入口
    main=Main()                   #创建主窗体对象
    main.show()                   #显示主窗体
    sys.exit(app.exec_())         #循环中等待退出程序

#实现车票查询区域数据显示
def on_click(self):
    get_from=self.textEdit.toPlainText()     #获取出发地
    get_to=self.textEdit_2.toPlainText()     #获取目的地
    get_date=self.textEdit_3.toPlainText()   #获取出发日
    #判断车站文件是否存在
    if is_stations('stations.text'):
        stations=eval(read('stations.text'))
        #判断所有参数是否为空，如出发地、目的地、出发日期
        if get_from != "" and get_to != "" and get_date != "":
            #判断输入的车站名称是否存在，以及时间格式是否正确
            if get_from in stations and get_to in stations and self.is_valid_date(get_date):
                #计算时间差
                time_difference=self.time_difference(self.get_time(),get_date).days
                #判断时间差为0，证明查询的是当前的车票，以及29天以后的车票,12306官方要求只能查询30天以内的车票
                if 0 <= time_difference <= 15:
                    #在所有车站文件中找到对应的参数出发地
                    from_station=stations[get_from]
                    to_station=stations[get_to]
                    datas=query(get_date,from_station,to_station)
                    self.checkBox_default()
                    if len(datas) != 0:
                        #如果不是空数据，就将车票信息显示在表格中
                        self.displayTable(len(datas),16,datas)
                    else:
                        show_message('警告','没有返回的网络数据！')
                else:
                    show_message('警告','超出查询日期的范围内，不可查询昨天的车票信息，以及15天以后的车票信息！')
            else:
                show_message('警告','输入的站名不存在，或日期格式不正确！')
        else:
            show_message('警告','请填写车站名称')
    else:
        show_message('警告','未下载车站查询文件')


#卧铺售票分析查询按钮的事件处理
def query_ticket_analysis_click(self):
    self.info_table=[]

    today_train_list.clear()  #清空今天列车信息，已处理是否有票
    three_train_list.clear()   #清空三天内列车信息，已处理是否有票
    five_train_list.clear()    #清空今天列车信息，已处理是否有票

    today_list.clear()   #清空今天列车信息，未处理是否有票
    three_list.clear()   #清空三天内列车信息，未处理是否有票
    five_list.clear()    #清空五天内列车信息，未处理是否有票

    get_from = self.textEdit_analysis_from.toPlainText()  # 获取出发地
    get_to = self.textEdit_analysis_to.toPlainText()  # 获取目的地

    # 判断车站文件是否存在
    if is_stations('stations.text'):
        stations = eval(read('stations.text'))
        # 判断所有参数是否为空，如出发地、目的地、出发日期
        if get_from != "" and get_to != "":
            if get_from in stations and get_to in stations:
                from_station=stations[get_from]
                to_station=stations[get_to]

                today=datetime.datetime.now()   #获取当天日期
                three_set=datetime.timedelta(days=+2)    #三天内偏移天数
                five_set=datetime.timedelta(days=+4)     #五天内偏移天数

                three_day=(today+three_set).strftime('%Y-%m-%d')   #三天格式化后的日期
                five_day=(today+five_set).strftime('%Y-%m-%d')    #五天格式化后的日期
                today=today.strftime('%Y-%m-%d')            #今天格式化后的日全球
                #发送查询今天卧铺票信息的网络请求
                query_ticket_analysis(today,from_station,to_station,1)
                #发送查询三天内卧铺票信息的网络请求
                query_ticket_analysis(three_day,from_station,to_station,3)
                #发送查询五天内卧铺票信息的网络请求
                query_ticket_analysis(five_day,from_station,to_station,5)

                info_set=set()
                for i in today_train_list+three_train_list+five_train_list:
                    #在集合总必须是字符才能进行整合，所以将车次信息转换位字符串类型，方便车次整合
                    info_set.add(str(i[0:6]))
                for info in info_set:    #遍历车次信息
                    info=eval(info)      #转化为列表
                    is_today_true=False    #判断今天是否存在某趟列车的标记
                    for i in today_train_list:  #遍历今天的车次信息，该车次信息是没有筛选的信息
                        if info[0] in i:    #判断整合后的车次信息是否存在
                            is_today_true=True    #存在就进行标记
                            #如果存在就将车次信息中是否有卧铺的信息添加至整合后的车次信息中
                            info.append(i[6])
                            break
                    if is_today_true==False:     #如果今天没有某一趟列车信息就标记为“--”
                        info.append('--')

                    is_three_true=False
                    for i in three_train_list:  #遍历今天的车次信息，该车次信息是没有筛选的信息
                        if info[0] in i:    #判断整合后的车次信息是否存在
                            is_three_true=True    #存在就进行标记
                            #如果存在就将车次信息中是否有卧铺的信息添加至整合后的车次信息中
                            info.append(i[6])
                            break
                    if is_three_true==False:
                        info.append('--')

                    is_five_true = False
                    for i in five_train_list:  # 遍历今天的车次信息，该车次信息是没有筛选的信息
                        if info[0] in i:  # 判断整合后的车次信息是否存在
                            is_five_true = True  # 存在就进行标记
                            # 如果存在就将车次信息中是否有卧铺的信息添加至整合后的车次信息中
                            info.append(i[6])
                            break
                    if is_five_true==False:
                        info.append('--')
                    self.info_table.append(info)    #将最后结果添加至窗体表格的列表中

                self.tableWidget.setRowCount(len(self.info_table))  #设置表格行数
                self.tableWidget.setColumnCount(9)
                #设置表格内容文字大小
                font=QtGui.QFont()
                font.setPointSize(12)
                self.tableWidget.setFont(font)
                #根据窗体大小拉伸表格
                self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
                #遍历最终信息
                for row in range(len(self.info_table)):
                    fraction=0      #分数，根据该分数判断列车的紧张程度
                    for column in range(9):
                        if column==6:
                            if self.info_table[row][column]=='无' or self.info_table[row][column]=='--':
                                fraction+=3     #计3分
                        if column==7:
                            if self.info_table[row][column]=='无' or self.info_table[row][column]=='--':
                                fraction+=2     #计2分
                        if column==8:
                            if self.info_table[row][column]=='无' or self.info_table[row][column]=='--':
                                fraction+=1     #计1分

                    #分数大于或等于5分的车次为红色，说明该车次卧铺非常紧张
                    if fraction>=5:
                        #定位是哪趟车次符合该条件，遍历该车次信息
                        for i in range(len(self.info_table[row])):
                            #表格列中信息
                            item=QtWidgets.QTableWidgetItem(self.info_table[row][i])
                            item.setBackground(QColor(255,0,0))    #设置车次背景颜色红色
                            self.tableWidget.setItem(row,i,item)   #设置表格显示的内容
                    if 1<=fraction<=4:
                        for i in range(len(self.info_table[row])):
                            item = QtWidgets.QTableWidgetItem(self.info_table[row][i])
                            item.setBackground(QColor(255, 170, 0))  # 设置车次背景颜色橙色
                            self.tableWidget.setItem(row, i, item)  # 设置表格显示的内容
                    if fraction==0:
                        for i in range(len(self.info_table[row])):
                            item = QtWidgets.QTableWidgetItem(self.info_table[row][i])
                            item.setBackground(QColor(85, 170, 0))  # 设置车次背景颜色绿色
                            self.tableWidget.setItem(row, i, item)  # 设置表格显示的内容


#统计车票数量
def statistical_quantity(self,msg):
    number=0   #车票初始值
    for i in msg:
        if i=='有':   #如果有，增加20张车票
            number += 20
        if i=='无' or i=='':   #如果是无或空，就增加0
            number += 0
        if i.isdigit():   #如果是数字，就直接增加对应的数字
            number += int(i)
    return number


#显示卧铺车票数量折线图
def show_broken_line(self):
    train_number_list=[]     #保存车次
    tickets_number_list=[]   #保存今天，三天内，五天内所有车次的卧铺数量

    #遍历车次信息
    for train_number in self.info_table:
        number_list=[]                                  # 临时保存车票数量
        if self.horizontalLayout.count()!=0:      #判断水平布局内是否为空
            # 循环删除管理器的组件
            while self.horizontalLayout.count():
                item=self.horizontalLayout.takeAt(0)  # 获取第一个组件
                widget=item.widget()                   # 删除组件
                widget.deleteLater()

        is_today_true = False  # 判断今天是否存在某趟列车的标记
        for today in today_list:
            # 判断今天的车次信息中是否有该车次
            if train_number[0] in today:
                is_today_true = True  # 存在就进行标记
                number = self.statistical_quantity(today[6:9])  # 调用统计车票数量的方法
                number_list.append(number)  # 将车票数量添加至临时列表中
                break
        if is_today_true == False:  # 如果今天没有某一趟列车，说明该车次无票为0
            number_list.append(0)

        is_three_true = False      #判断三天内是否存在某趟列车的标记
        for three_today in three_list:
            if train_number[0] in three_today:
                is_three_true = True
                number = self.statistical_quantity(three_today[6:9])
                number_list.append(number)
                break
        if is_three_true == False:
            number_list.append(0)

        is_five_true = False    #判断五天内是否存在某趟列车的标记
        for five_today in five_list:
            if train_number[0] in five_today:
                is_five_true = True
                number = self.statistical_quantity(five_today[6:9])
                number_list.append(number)
                break
        if is_five_true == False:
            number_list.append(0)

        tickets_number_list.append(number_list)   #添加车票数量列表
        train_number_list.append(train_number[0])  #添加车次列表

        # 车次信息大时，添加滚动条扩大折线图高度
        if len(train_number_list) >= 9:
            self.scrollAreaWidgetContents.setMinimumHeight(len(train_number_list) * 30)
            self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 951, (len(train_number_list) * 30)))
        # 创建画布对象
        line = PlotCanvas()
        line.broken_line(tickets_number_list, train_number_list)  # 调用折线图方法
        self.horizontalLayout.addWidget(line)  # 将折线图添加至底部水平布局当中


#车票起售时间查询按钮的事件处理
def query_time_click(self):
    station=self.lineEdit.text()      # 获取需要查询的起售车站
    stations_time = eval(read('time.text'))  # 读取所有车站与起售时间并转换为字典类型
    stations = eval(read('stations.text'))  # 读取所有车站并转换为字典类型
    if station in stations_time:
        # 查询起售车站对应的站名与起售时间
        name_lit, time_list = query_time(stations.get(station))
        # 循环删除管理器的控件
        if self.gridLayout.count() != 0:
            while self.gridLayout.count():
                item = self.gridLayout.takeAt(0)  # 获取第一个控件
                widget = item.widget()  # 删除控件
                widget.deleteLater()

        #根据起售时间信息的数量创建对应的控件并为控件设置属性
        i = -1  # 行数标记
        for n in range(len(name_lit)):
            x = n % 4  # x 确定每行显示的个数 0，1，2,3 每行4个
            # 当x为0的时候设置换行 行数+1
            if x == 0:
                i += 1
            self.widget = QtWidgets.QWidget()  # 创建布局
            self.widget.setObjectName("widget" + str(n))  # 给布局命名
            # 设置布局样式
            self.widget.setStyleSheet('QWidget#' + "widget" + str(
                n) + "{border:2px solid rgb(175, 175, 175);background-color: rgb(255, 255, 255);}")
            # 创建个Qlabel控件用于显示图片 设置控件在QWidget中
            self.label = QtWidgets.QLabel(self.widget)
            self.label.setAlignment(QtCore.Qt.AlignCenter)
            # 设置大小
            self.label.setGeometry(QtCore.QRect(10, 10, 210, 65))
            font = QtGui.QFont()  # 创建字体对象
            font.setPointSize(11)  # 设置字体大小
            font.setBold(True)  # 开启粗体属性
            font.setWeight(75)  # 设置文字粗细
            self.label.setFont(font)  # 设置字体
            # 设置显示站名与起售时间
            self.label.setText(name_lit[n] + '        ' + time_list[n])
            # 把动态创建的widegt布局添加到gridLayout中 i，x分别代表：行数以及每行的个数
            self.gridLayout.addWidget(self.widget, i, x)
        # 设置高度为动态高度根据行数确定高度 每行300
        self.scrollAreaWidgetContents_2.setMinimumHeight((i + 1) * 100)
        # 设置网格布局控件动态高度
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 950, ((i + 1) * 100)))

#显示消息提示框，参数title为提示框标题文字，message为提示消息
def show_message(title,message):
    message_box=QMessageBox(QMessageBox.Warning,title,message)
    message_box.exec_()


#判断是否是一个有效的日期字符串
def is_valid_date(self,str):
    try:
        time.strptime(str,'%Y-%m-%d')
        return True
    except:
        return False

#获取系统当前时间并转换为请求数据所需的格式
def get_time(self):
    #获取当前时间戳
    now=int(time.time())
    timeStruct=time.localtime(now)
    strTime=time.strftime('%Y-%m-%d',timeStruct)
    return strTime

#计算购票时间差
def time_difference(self,in_time,new_time):
    in_time=time.strptime(in_time,'%Y-%m-%d')
    new_time=time.strptime(new_time,'%Y-%m-%d')
    in_time=datetime.datetime(in_time[0],in_time[1],in_time[2])
    new_time=datetime.datetime(new_time[0],new_time[1],new_time[2])
    return new_time - in_time

#将所有车次分类复选框取消勾选
def checkBox_default(self):
    self.checkBox_G.setChecked(False)
    self.checkBox_D.setChecked(False)
    self.checkBox_Z.setChecked(False)
    self.checkBox_T.setChecked(False)
    self.checkBox_K.setChecked(False)


#显示车次信息的表格
#train参数为共有多少趟列车，该参数作为表格的行
#info参数为每趟列车的具体信息，例如有座、无座、卧铺等，该参数作为表格的列
def displayTable(self,train,info,data):
    self.model.clear()
    for row in range(train):
        for column in range(info):
            #添加表格内容
            item=QStandardItem(data[row][column])
            #向表格存储模式中添加表格具体信息
            self.model.setItem(row,column,item)
    self.tableView.setModel(self.model)



if __name__=='__main__':
    if is_stations('stations.text') == False and is_stations('time.text')==False:
        get_station()
        get_sellingtime()
    #判断两种文件存在时显示窗体
    if is_stations('stations.text') == True and is_stations('time.text') == True:
        show_MainWindow()           #调用显示窗体的方法
    else:
        show_message('警告','车站文件或起售时间文件下载异常！')
