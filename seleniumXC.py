from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import pymysql
import pymysql.cursors
import datetime

class demoSpider():
    start_urls = []
    departDArr = ['2019-12-21', '2019-12-22']
    returnDArr = ['2020-01-10','2020-01-11', '2020-01-12']
    origArr = ['ord']
    destArr = ['hkg', 'can']
    orderArr = []
    urlCounter = 5
    # start_urls = ['https://flights.ctrip.com/international/search/round-' + orig + '0-' + dest + '?depdate=' + departD + '_' + returnD + '&cabin=y_s&adult=1&child=0&infant=0']
    # ['https://flights.ctrip.com/international/search/round-ord0-can?depdate=2019-12-21_2020-01-11&cabin=y_s&adult=1&child=0&infant=0']
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.flightsPath = """//*[@id="app"]/div/div[2]"""
        self.counterMax = 120;
        self.counter = 145;
        self.rate = 1 #per minutes
        self.period = 1
        self.errorCounter = 0
        for orig in demoSpider.origArr:
            for dest in demoSpider.destArr:
                demoSpider.getUrl(orig,dest)
    def getUrl(orig, dest):
        for x in demoSpider.departDArr:
            for y in demoSpider.returnDArr:
                demoSpider.orderArr.append([orig, dest, x, y])
                demoSpider.start_urls.append('https://flights.ctrip.com/international/search/round-' + orig + '0-' + dest + '?depdate=' + x + '_' + y + '&cabin=y_s&adult=1&child=0&infant=0')
    def getSqlTableNameDate (date):
        year = date[:4]
        month = date[5:7]
        day = date[8:10]
        return (year + month + day)
    def getName(self, flightNum):
        counter = 0
        for x in flightNum:
            if x == "-":
                break
            counter += 1
        return flightNum[:counter]
    def countDownSys(self):
        print(self.counter)
        result = False
        if self.counter == 0:
            self.counter = self.counterMax
        if self.counter % (60 / self.rate) == 0:
            result = True
        self.counter -= 1;
        time.sleep(self.period)
        return result
    def getSqlTableName(orderArrElem):
        sqlTableName = orderArrElem[0] + orderArrElem[1] + demoSpider.getSqlTableNameDate(orderArrElem[2]) + demoSpider.getSqlTableNameDate(orderArrElem[3])
        return sqlTableName
    def extractDuration(self, flightDur):
        #x天x小时xx分
        elementCounter = 0
        flag = False
        tempResult = ''
        tempList = []
        ins = [0,1,2]
        for x in flightDur:
            if x == '天':
                ins.remove(0)
            if x == '小':
                ins.remove(1)
            if x == '分':
                ins.remove(2)
            if x.isdigit():
                tempResult += x
                flag = False
            else:
                if len(tempResult) == 1:
                    tempResult = '0' + tempResult
                tempList.append(tempResult)
                tempResult = ''
                if not flag:
                    elementCounter += 1
                    flag = True
        if elementCounter <= 2:
            for x in ins:
                tempList.insert(x, '00')
        result = ":".join([str(i) for i in tempList if i])
        return result
    def seperateFlightNum(self, flightNum):
        counterCur = 0
        counterNonDig = 0
        flightList = []
        for x in flightNum:
            if not x.isdigit():
                counterNonDig += 1
            counterCur += 1
            if counterNonDig == 3:
                counterCur -= 1
                flightList.append(flightNum[:counterCur])
                flightList.append(flightNum[counterCur:])
                return flightList
        return [flightNum, None]
    def sendToMySQL(self, flightInfo, counter):
        connection = pymysql.connect(host='localhost', user='root', password='12345678', db='flightInfo', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sqlTable = demoSpider.getSqlTableName(demoSpider.orderArr[counter])
                sql = "INSERT INTO " + sqlTable + " ( flight, price, query_date, flight1, flight2, duration, t_count, departure_time, arrival_time, departure_airport, arrival_airport, t_city) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                curr_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(sql, (flightInfo[0], flightInfo[9], curr_time, flightInfo[10], flightInfo[11], flightInfo[8], flightInfo[6], flightInfo[2], flightInfo[4], flightInfo[3], flightInfo[5], flightInfo[7]))
            connection.commit()
        finally:
            connection.close()
    def errorSys(self, partial, reset):
        if reset:
            self.errorCounter = 0
        else:
            print("There's a problem, error counter = " + str(self.errorCounter) + ", and is " + str(partial) + " partial")
            if partial:
                if self.errorCounter > 3:
                    partial = False
                else:
                    self.errorCounter += 1
            if not partial:
                self.driver.close()
                self.driver = webdriver.Chrome()
                self.driver.implicitly_wait(10)
    def parse(self):
        # self.driver.get(response.url)
        self.driver.get(demoSpider.start_urls[demoSpider.urlCounter])
        delay = 6 # seconds
        while True:
            if self.countDownSys():
                flightDict = {}
                try:
                    lookingFor = EC.presence_of_element_located((By.XPATH, self.flightsPath))
                    myElem = WebDriverWait(self.driver, delay).until(lookingFor)
                    print("Page is ready!")
                except TimeoutException:
                    print("Loading took too much time!")
                    self.driver.get(demoSpider.start_urls[demoSpider.urlCounter])
                    print("Refreshing the same page")
                    self.errorSys(True, False)
                    continue
                try:
                    flightPage = self.driver.find_element_by_xpath(self.flightsPath )
                    flights = flightPage.find_elements_by_class_name('flight-item')
                    print("There's " + str(len(flights)) + " flights!")
                    counter = 0
                    for fli in flights:
#========main-info
                        flightInfo = []
                        flightNum = fli.find_element_by_class_name('airline-name').find_element_by_tag_name('span').get_property('id')
                        flightNum = flightNum[11:]
                        flightNum = self.getName(flightNum)
                        flightName = fli.find_element_by_class_name('airline-name').find_element_by_tag_name('span').text
#========departure
                        flightDetail = fli.find_element_by_class_name("flight-detail")
                        departBox = flightDetail.find_element_by_class_name("depart-box")
                        departT = departBox.find_element_by_class_name("time").text
                        departT = departT[:5] + ':00'
                        departA = departBox.find_element_by_class_name("airport").find_element_by_tag_name('span').text
#========arrival
                        arrivBox = flightDetail.find_element_by_class_name("arrive-box")
                        arrivT = arrivBox.find_element_by_class_name("time").text
                        arrivT = arrivT[:5] + ':00'
                        arrivA = arrivBox.find_element_by_class_name("airport").find_element_by_tag_name('span').text
#========transfer
                        transferCity = ''
                        css_selector = '#flightInfo' + '-' + flightNum + '-' + str(counter*100)
                        transferCount = 0
                        try:
                            arrowBox = flightDetail.find_element_by_class_name('arrow-box')
                            # transferCount = arrowBox.find_element_by_class_name('arrow-transfer').text
                            transferCount = arrowBox.find_element_by_css_selector(css_selector + ' > i').text
                            if len(transferCount) == 0:
                                transferCount = 0
                                raise NoSuchElementException
                            transferCount = transferCount.strip('转')
                            transferCount = transferCount.strip('次')
                            #flightInfo-NH011NH933-0 > div > div > div > i
                            # transferCity = arrowBox.find_element_by_css_selector(css_selector + ' > div > div > div > i').text
                            transferCity = arrowBox.find_element_by_class_name('transfer-info').text
                            transferCity = transferCity.strip('转')
                        except Exception as e:
                            print('========================No transfer')
                        # if transferCount == '':
                        #     transferCount = 0
#========price/duration
                        flightDur = fli.find_element_by_class_name("flight-consume").text
                        flightDur = self.extractDuration(flightDur)
                        price = fli.find_element_by_class_name("flight-price").find_element_by_class_name("price").text
                        price = price.strip('¥')
                        price = price.strip('起')

                        flightInfo.append(flightNum) #0
                        flightInfo.append(flightName) #1
                        flightInfo.append(departT) #2
                        flightInfo.append(departA) #3
                        flightInfo.append(arrivT) #4
                        flightInfo.append(arrivA) #5
                        flightInfo.append(transferCount) #6
                        flightInfo.append(transferCity) #7
                        flightInfo.append(flightDur) #8
                        flightInfo.append(price) #9

                        flightSep = self.seperateFlightNum(flightNum)
                        flightInfo.append(flightSep[0]) #10
                        flightInfo.append(flightSep[1]) #11

                        flightDict[flightNum] = flightInfo
                        counter += 1
                    print("========================/succeed/")
                except Exception as e:
                    print("========================/failed/")
                    print(e)
                    self.errorSys(False, True)
                    break
                for fli in flightDict.values():
                    self.sendToMySQL(fli, demoSpider.urlCounter)
                    print("========================/toSQL/" + fli[0])
                demoSpider.urlCounter += 1
                if demoSpider.urlCounter == (len(demoSpider.start_urls)):
                    demoSpider.urlCounter = 0
                    print("========================/cycle finished/")
                self.driver.get(demoSpider.start_urls[demoSpider.urlCounter]);
                self.errorSys(False, True)
                print(demoSpider.orderArr[demoSpider.urlCounter])
                print("========================/page renewed/")
        self.driver.close()
task = demoSpider()
task.parse()
