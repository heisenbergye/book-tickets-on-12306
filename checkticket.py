# -*- coding: utf-8 -*-

from splinter.browser import Browser
from configparser import ConfigParser
from time import sleep
import traceback
import time, sys
import codecs
import argparse
import os

class hackTickets(object):
    """读取配置文件"""
    def readConfig(self, config_file='config.ini'):
        print("加载配置文件...")
        # 补充文件路径，获得config.ini的绝对路径，默认为主程序当前目录
        path = os.path.join(os.getcwd(), config_file)

        cp = ConfigParser()
        try:
            # 指定读取config.ini编码格式，防止中文乱码（兼容windows）
            cp.readfp(codecs.open(config_file, "r", "utf-8-sig"))
        except IOError as e:
            print(u'打开配置文件"%s"失败, 请先创建或者拷贝一份配置文件config.ini' % (config_file))
            input('Press any key to continue')
            sys.exit()
        # 始发站
        starts_city = cp.get("cookieInfo", "starts")
        # 地名编码为cookie值
        self.starts = self.convertCityToCode(starts_city).encode('unicode_escape').decode("utf-8").replace("\\u", "%u").replace(",", "%2c")
        # 终点站
        ends_city = cp.get("cookieInfo", "ends")
        self.ends = self.convertCityToCode(ends_city).encode('unicode_escape').decode("utf-8").replace("\\u", "%u").replace(",", "%2c")
        # 出发日
        self.dtime = cp.get("cookieInfo", "dtime")
        # 车次类型
        self.train_types = cp.get("trainInfo", "train_types").split(",")
        # 发车时间
        self.start_time = cp.get("trainInfo", "start_time")
        # 网址
        self.ticket_url = cp.get("urlInfo", "ticket_url")
        # 调用浏览器
        self.driver_name = cp.get("pathInfo", "driver_name")
        # 调用浏览器驱动
        self.executable_path = cp.get("pathInfo", "executable_path")

    def loadConfig(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config', help='Specify config file, use absolute path')
        args = parser.parse_args()
        if args.config:
            # 使用指定的配置文件
            self.readConfig(args.config)
        else:
            # 使用默认的配置文件config.ini
            self.readConfig()

    """
        加载映射文件，并将中文"南京"转换成编码后的格式：“南京,NJH“
    """
    def loadCityCode(self):
        print("映射出发地、目的地...")
        city_codes = {}
        path = os.path.join(os.getcwd(), 'city_code.txt')
        with codecs.open(path, "r", "utf-8-sig") as f:
            for l in f.readlines():
                city = l.split(':')[0]
                code = l.split(':')[1].strip()
                city_codes[city] = city + "," + code
        return city_codes

    def convertCityToCode(self, c):
        try:
            return self.city_codes[c]
        except KeyError:
            print("转换城市错误，请修改config.ini中starts或者ends值为中文城市名")
            return False

    def __init__(self):
        # 读取地名到city_code.txt转换为对应三字码，比如：“南京”: "南京,NJH"
        self.city_codes = self.loadCityCode();
        # 读取配置文件，获得初始化参数
        self.loadConfig();

    def searchMore(self):
        # 选择车次类型
        for type in self.train_types:
            # 车次类型选择
            train_type_dict = {'T': u'T-特快',                # 特快
                                'G': u'GC-高铁/城际',         # 高铁
                                'D': u'D-动车',               # 动车
                                'Z': u'Z-直达',               # 直达
                                'K': u'K-快速'                # 快速
                                }
            if type == 'T' or type == 'G' or type == 'D' or type == 'Z' or type == 'K':
                print(u'--------->选择的车次类型', train_type_dict[type])
                self.driver.find_by_text(train_type_dict[type]).click()
            else:
                print(u"车次类型异常或未选择!(train_type=%s)" % type)

        # 选择发车时间
        print(u'--------->选择的发车时间', self.start_time)
        if self.start_time:
            self.driver.find_option_by_text(self.start_time).first.click()
        else:
            print(u"未指定发车时间，默认00:00-24:00")

    def preStart(self):
        # 加载查询信息
        # 出发地
        self.driver.cookies.add({"_jc_save_fromStation": self.starts})
        # 目的地
        self.driver.cookies.add({"_jc_save_toStation": self.ends})
        # 出发日
        self.driver.cookies.add({"_jc_save_fromDate": self.dtime})

    def clickcheck(self):
        # 勾选车次类型
        self.searchMore();
        sleep(0.03)
        self.driver.find_by_text(u"查询").click()

    def checkTickets(self):
        # 填充查询条件
        self.preStart()

        # 带着查询条件，重新加载页面
        self.driver.reload()

        # 确认查询
        self.clickcheck()

    def start(self):
        # 初始化驱动
        self.driver=Browser(driver_name=self.driver_name,executable_path=self.executable_path)
        # 初始化浏览器窗口大小
        self.driver.driver.set_window_size(1400, 1000)

        # 访问余票查询页面
        self.driver.visit(self.ticket_url)

        # 查询要购买车票
        self.checkTickets();

if __name__ == '__main__':
    print("===========开始查询余票===========")
    hackTickets = hackTickets()
    hackTickets.start()
