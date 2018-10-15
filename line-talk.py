#!/usr/bin/env python3

import os
import requests
from argparse import ArgumentParser
from configparser import ConfigParser
from datetime import datetime


def get_weather():
    payload = {
        'stationId': 'CAAH60',
        'format': 'json'
    }
    headers = {
        'Authorization': config['BASE']['cwb_token']
    }
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0003-001'
    resp = requests.get(url, headers=headers, params=payload)
    data = resp.json()

    print(element_to_dict(data["records"]["location"][0]["weatherElement"]))

def element_to_dict(elements):
    rtn = dict()
    for element in elements:
        rtn[element['elementName']] = element['elementValue']
    return rtn

def get_forecast(args, config):
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/' + config['LOCATION_1']['data_id']
    headers = {
        'Authorization': config['BASE']['cwb_token']
    }

    time_period = get_timeperiod(args)

    payload = {
        'locationName': config[args.location]['location_name'],
        'format': 'json',
        'timeFrom': time_period[0],
        'timeTo': time_period[1],
        'elementName': 'Wx,AT,T,RH,CI'
    }

    resp = requests.get(url, headers=headers, params=payload)
    data = resp.json()
    # print(data['records']["locations"][0])
    top_location = data['records']['locations'][0]
    location = data['records']['locations'][0]['location'][0]
    forecast = {
        'username': config['BASE']['username'],
        'location_name': top_location['locationsName'] + top_location['location'][0]['locationName'],
        'weather_elements': forecast_element(location['weatherElement']),
        'extra_message': config['EXMESSAGE']
    }
    message = combine_message(args, forecast)

    send_message(config, message)

def send_message(config, message):
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': 'Bearer ' + config['BASE']['line_token']
    }
    
    payload = {
        'message': message
    }

    resp = requests.post(url, headers=headers, params=payload)

def forecast_element(elements):
    weather_elements = dict()
    for element in elements:
        if element['elementName'] in ['Wx', 'AT', 'T', 'RH']:
            weather_elements[element['elementName']] = element['time'][0]['elementValue'][0]['value']
        elif element['elementName'] == 'CI':
            weather_elements['CI'] = element['time'][0]['elementValue'][1]['value']
    return weather_elements

def get_timeperiod(args):
    today = datetime.now().strftime('%Y-%m-%d')
    if args.period == 'morning':
        return [today + 'T06:00:00', today + 'T09:00:00']
    elif args.period == 'noon':
        return [today + 'T12:00:00', today + 'T15:00:00']
    elif args.period == 'evening':
        return [today + 'T18:00:00', today + 'T21:00:00']

def combine_message(args, forecast):
    if args.period == 'morning':
        message = '喔嗨呦~ {} <3 今天早上「{}」的天氣是"{}"，體感溫度是{}度，是讓人覺得"{}"的天氣哦！（實際溫度{}度，相對溼度{}%）{}'
        extra_message = forecast['extra_message']['morning']
    elif args.period == 'noon':
        message = '甲奔了！ {} <3 中午「{}」的天氣是"{}"的！體感溫度現在是{}度讓人覺得"{}"~（實際溫度{}度，相對溼度{}%）{}'
        extra_message = forecast['extra_message']['noon']
    elif args.period == 'evening':
        message = '{} 包袱款款準備下班了 ^++++^ 晚上「{}」的天氣是"{}"。外面體感溫度現在是{}度，讓人覺得"{}"~（實際溫度{}度，相對溼度{}%）{}'
        extra_message = forecast['extra_message']['evening']

    return message.format(
                forecast['username'],
                forecast['location_name'],
                forecast['weather_elements']['Wx'],
                forecast['weather_elements']['AT'],
                forecast['weather_elements']['CI'],
                forecast['weather_elements']['T'],
                forecast['weather_elements']['RH'],
                extra_message
                )
    

def find(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find(key, d):
                    yield result


if __name__ == '__main__':
    # get_weather()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser()
    config.read(dir_path + '/config.ini')

    parser = ArgumentParser(description="蜜蜂搖擺舞，Line Notify 天氣通知")
    parser.add_argument("period", choices=['morning', 'noon', 'evening'], 
                        default='morning', help="指定查詢的時段")
    parser.add_argument("location", help="config中的地點")
    args = parser.parse_args()

    get_forecast(args, config)

    # example = {'app_url': '', 'models': [{'perms': {'add': True, 'change': True, 'delete': True, 'admin_url': '/admin/cms/news/222'}, 'add_url': '/admin/cms/news/add/', 'admin_url': '/admin/cms/news/', 'name': ''}], 'has_module_perms': True, 'name': u'CMS'}
    # print(list(find('admin_url', example)))
