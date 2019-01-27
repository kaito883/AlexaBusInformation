#import time
import requests
from bs4 import BeautifulSoup
import re
import json

target_url = 'https://rinkobus.bus-navigation.jp/wgsys/wgp/bus.htm?tabName=searchTab&selectedLandmarkCatCd=&from=%E6%A8%BD%E9%87%8E%E8%B0%B7&fromType=&to=%E7%B6%B1%E5%B3%B6%E9%A7%85&toType=1&locale=ja&fromlat=&fromlng=&tolat=&tolng=&sortBy=3&routeLayoutCd=&fromSignpoleKey=&bsid=1&mapFlag=false&existYn=N'
r = requests.get(target_url)         #requestsを使って、webから取得
soup = BeautifulSoup(r.text, 'lxml') #要素を抽出

bus_time = soup.find_all(attrs={"id": "errInfo"})

#print(soup)

def getNextBusTimeByString(soup, targetTimeString):
	next_bus_leaving_time = '***'
	next_bus_leaving_time_html_list = soup.find_all("td", text=re.compile(targetTimeString))
	next_bus_leaving_time_html = next_bus_leaving_time_html_list[0]
	next_bus_leaving_time = extractTimeFromString(next_bus_leaving_time_html)
	return next_bus_leaving_time


def extractTimeFromString(htmlString):
	extractedString = str(htmlString)
	extractedString = extractedString.replace('発車予測', '')
	extractedString = extractedString.replace('<td>', '')
	extractedString = extractedString.replace('</td>', '')
	pattern = re.compile(r'\s+')
	extractedString =  re.sub(pattern, '', extractedString)
	return extractedString


def getNextBusInformation():
	next_bus_leaving_time = getNextBusTimeByString(soup, '発車予測')
	next_bus_goal_time = getNextBusTimeByString(soup, '到着予測')
	text = '次の綱島駅行きのバスは' + '川51' + '-' + next_bus_leaving_time + '樽野谷発車予定です。' + '綱島駅到着予定時間は' + next_bus_goal_time + 'です。'
	response = {
       'version': '1.0',
       'response': {
           'outputSpeech': {
               'type': 'PlainText',
               'text': text
           }
       }
   }	
	return response

#lambdaのmain処理
def lambda_handler(event, context):
	response = getNextBusInformation()
	return response


#デバッグ用
print(getNextBusInformation())
#print(lambda_handler())
