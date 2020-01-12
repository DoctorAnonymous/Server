import requests
import random
import datetime
import time
import json
import threading
import os
import sys

user_agents = {
    'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5',
    'Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5',
    'Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5 ',
    'Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5',
    'Mozilla/5.0 (Linux; U; Android 2.2.1; zh-cn; HTC_Wildfire_A3333 Build/FRG83D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1 ',
    'Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
}


class seatKiller(object):
    def __init__(self, userID, passWord, devID, startTime='07:30', endTime='21:30'):
        self.userID = userID
        self.passWord = passWord
        self.devID = devID
        self.labID = '100455340'
        self.kindID = '100455550'
        self.headers = {'user-agent': random.sample(user_agents, 1)[0]}
        localTime = time.localtime(time.time() + 3600 * 24)
        year, month, mday, hour, minute, second, wday = localTime.tm_year, localTime.tm_mon, localTime.tm_mday, localTime.tm_hour, localTime.tm_min, localTime.tm_sec, localTime.tm_wday
        self.dateStr = '%d-%02d-%02d' % (year, month, mday)
        if wday == 2:
            self.reserveTime = [[startTime, '13:00'], ['18:05', endTime]]
            self.flagReserve = [0, 0]
        else:
            self.reserveTime = [[startTime, endTime]]
            self.flagReserve = [0]
        self.flagLogin = 0
        threading._start_new_thread(seatKiller.watchDog, (self,))

    def userLogin(self):
        self.session = requests.session()
        login = self.session.get('http://seat.hhit.edu.cn/ClientWeb/pro/ajax/login.aspx?act=login&id=%s&pwd=%s&role=512&aliuserid=&schoolcode=&wxuserid=' % (self.userID, self.passWord), headers=self.headers)
        localTime = time.localtime(time.time())
        year, month, mday, hour, minute, second, wday = localTime.tm_year, localTime.tm_mon, localTime.tm_mday, localTime.tm_hour, localTime.tm_min, localTime.tm_sec, localTime.tm_wday
        print(year, month, mday, hour, minute, second, end='\t')
        print(login.content.decode('utf8'))
        return 1

    def seatReserve(self, index, requestTime=['07:30', '21:30']):
        #print('http://seat.hhit.edu.cn/ClientWeb/pro/ajax/reserve.aspx?dev_id=%s&lab_id=%s&room_id=&kind_id=%s&type=dev&prop=&test_id=&resv_id=&term=&min_user=&max_user=&mb_list=&test_name=&start=%s%%20%s&end=%s%%20%s&memo=&act=set_resv' % (self.devID, self.labID, self.kindID, self.dateStr, requestTime[0], self.dateStr, requestTime[1]))
        reserve = self.session.get('http://seat.hhit.edu.cn/ClientWeb/pro/ajax/reserve.aspx?dev_id=%s&lab_id=%s&room_id=&kind_id=%s&type=dev&prop=&test_id=&resv_id=&term=&min_user=&max_user=&mb_list=&test_name=&start=%s%%20%s&end=%s%%20%s&memo=&act=set_resv' % (self.devID, self.labID, self.kindID, self.dateStr, requestTime[0], self.dateStr, requestTime[1]), headers=self.headers)
        self.flagReserve[index] = seatKiller.flagReserveFunc(reserve.content.decode('utf8'))

    def flagReserveFunc(contentStr):
        # 0-Unknown, 1-Success, 2-Fail
        localTime = time.localtime(time.time())
        year, month, mday, hour, minute, second, wday = localTime.tm_year, localTime.tm_mon, localTime.tm_mday, localTime.tm_hour, localTime.tm_min, localTime.tm_sec, localTime.tm_wday
        if "成功" in contentStr:
            print(year, month, mday, hour, minute, second, end='\t')
            print(contentStr)
            return 1
        if "冲突" in contentStr:
            #print(year, month, mday, hour, minute, second, end='\t')
            #print(contentStr)
            return 2
        return 0

    def watchDog(self):
        while True:
            localTime = time.localtime(time.time())
            year, month, mday, hour, minute, second, wday = localTime.tm_year, localTime.tm_mon, localTime.tm_mday, localTime.tm_hour, localTime.tm_min, localTime.tm_sec, localTime.tm_wday
            sys.stdout.flush()
            #print(year, month, mday, hour, minute, second)
            if hour == 5 and minute > 28 and self.flagLogin == 0:
                try:
                    self.flagLogin = self.userLogin()
                except:
                    pass
            elif hour == 5 and ((minute == 29 and second > 50) or minute > 30):
                for i in range(len(self.flagReserve)):
                    try:
                        threading._start_new_thread(seatKiller.seatReserve, (self, i, self.reserveTime[i]))
                    except:
                        pass
            if sum([i != 0 for i in self.flagReserve]) >= len(self.flagReserve):
                print(self.flagReserve)
                break
            if hour == 5 and minute > 35:
                print(self.userID + ' end of the day')
                break
            if hour == 5 and minute > 25 and minute < 33:
                time.sleep(0.2)
            else:
                time.sleep(60)
            #sys.stdout.flush()


while True:
    localTime = time.localtime(time.time())
    year, month, mday, hour, minute, second, wday = localTime.tm_year, localTime.tm_mon, localTime.tm_mday, localTime.tm_hour, localTime.tm_min, localTime.tm_sec, localTime.tm_wday
    if hour == 5 and minute < 10:
        info = json.load(open('json/activate.json'))
        for userID in info:
            tmp = seatKiller(userID, info[userID]['passWord'], info[userID]['devID'])
            print('%s started' % userID)
        time.sleep(3500 * 24)
    else:
        time.sleep(300)
