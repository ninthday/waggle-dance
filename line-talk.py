#!/usr/bin/env python3

import os
import requests
from configparser import ConfigParser


def get_weather():
    payload = {
        'stationId': 'CAAH60',
        'format': 'json'
    }
    headers = {
        'Authorization': 'CWB-F0360097-400B-4F49-8DAE-AB8B7C4457DF'
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

def get_forecast(config):
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/' + config['LOCATION_1']['data_id']
    headers = {
        'Authorization': config['BASE']['cwb_token']
    }
    payload = {
        'locationName': config['LOCATION_1']['location_name'],
        'format': 'json',
        'timeFrom': '2018-10-15T06:00:00',
        'timeTo': '2018-10-15T09:00:00',
        'elementName': 'Wx,AT,T,RH,CI'
    }

    resp = requests.get(url, headers=headers, params=payload)
    data = resp.json()
    # print(data['records']["locations"][0])
    top_location = data['records']['locations'][0]
    location_name = top_location['locationsName'] + top_location['location'][0]['locationName']
    print(location_name)
    location = data['records']['locations'][0]['location'][0]
    # location_name = find('locationsName', data['records']["locations"][0])
    weather_elements = forecast_element(location['weatherElement'])
    print(weather_elements)

def forecast_element(elements):
    weather_elements = dict()
    for element in elements:
        if element['elementName'] in ['Wx', 'AT', 'T', 'RH']:
            weather_elements[element['elementName']] = element['time'][0]['elementValue'][0]['value']
        elif element['elementName'] == 'CI':
            weather_elements['CI'] = element['time'][0]['elementValue'][1]['value']
    return weather_elements

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
    get_forecast(config)

    # example = {'app_url': '', 'models': [{'perms': {'add': True, 'change': True, 'delete': True, 'admin_url': '/admin/cms/news/222'}, 'add_url': '/admin/cms/news/add/', 'admin_url': '/admin/cms/news/', 'name': ''}], 'has_module_perms': True, 'name': u'CMS'}
    # print(list(find('admin_url', example)))
