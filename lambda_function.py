#import time
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta, timezone
# print(soup)

JST = timezone(timedelta(hours=+9), 'JST')


def get51NextBusTimeByString(soup, td_tag_seq, targetTimeString):
    timeString = '***'
    html_list = soup.find_all("td", text=re.compile(targetTimeString))
    html = html_list[td_tag_seq]
    timeString = extractTimeFromString(html)
    return timeString


def extractTimeFromString(htmlString):
    extractedString = str(htmlString)
    extractedString = extractedString.replace('発車予測', '')
    extractedString = extractedString.replace('到着予測', '')
    extractedString = extractedString.replace('予定時刻', '')
    extractedString = extractedString.replace('<td>', '')
    extractedString = extractedString.replace('</td>', '')
    pattern = re.compile(r'\s+')
    extractedString = re.sub(pattern, '', extractedString)
    return extractedString


def create51BusInfoText():
    target_url = 'https://rinkobus.bus-navigation.jp/wgsys/wgp/bus.htm?tabName=searchTab&selectedLandmarkCatCd=&from=%E6%A8%BD%E9%87%8E%E8%B0%B7&fromType=&to=%E7%B6%B1%E5%B3%B6%E9%A7%85&toType=1&locale=ja&fromlat=&fromlng=&tolat=&tolng=&sortBy=3&routeLayoutCd=&fromSignpoleKey=&bsid=1&mapFlag=false&existYn=N'
    r = requests.get(target_url)  # requestsを使って、webから取得
    soup = BeautifulSoup(r.text, 'lxml')  # 要素を抽出
    try:
        next_bus_scheduled_time = get51NextBusTimeByString(soup, 0, '予定時刻')
        next_bus_leaving_time = get51NextBusTimeByString(soup, 0, '発車予測')
        next_bus_goal_time = get51NextBusTimeByString(soup, 0, '到着予測')
        second_bus_scheduled_time = get51NextBusTimeByString(
            soup, 2, '予定時刻')  # '予定時刻'が2つあるためコイツは1つ多くする
        second_bus_leaving_time = get51NextBusTimeByString(soup, 1, '発車予測')
        second_bus_goal_time = get51NextBusTimeByString(soup, 1, '到着予測')
        text = datetime.now(JST).strftime("%H:%M") + '時点、'\
            + 'たるのや発の' + '綱島駅行き' + '川51' + 'バス情報です。' \
            + '直近の予定時刻は' + next_bus_scheduled_time + '、' \
            + '発車予測' + next_bus_leaving_time + '、' \
            + '綱島駅到着予測時間は' + next_bus_goal_time + 'です。'\
            + 'その次のバスは予定時刻' + second_bus_scheduled_time + '、' \
            + '発車予測' + second_bus_leaving_time + '、' \
            + '綱島駅到着予測時間は' + second_bus_goal_time + 'です。'
    except:
        text = datetime.now(JST).strftime("%H:%M") + '時点、'\
            + '川51の60分以内に接近しているバスありません。'
    return text


def getNextBusInformationResponce():
    text = create51BusInfoText()

    response = {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': text
            },
            'shouldEndSession': False
        }
    }
    return response

# lambdaのmain処理


def lambda_handler(event, context):
    response = getNextBusInformationResponce()
    if event['request']['type'] == "LaunchRequest":
        return response
    else:
        response = {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': event['request']['intent']['name']
                },
                'shouldEndSession': False
            }
        }
        return response


# デバッグ用
print(getNextBusInformationResponce())
print()
