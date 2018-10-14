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

if __name__ == '__main__':
    get_weather()
