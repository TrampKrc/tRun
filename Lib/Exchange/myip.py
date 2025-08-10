
import re
import json

import os
import sys

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

"""
from urllib import urlopen

url = 'http://ipinfo.io/json'
response = urlopen(url)
data = json.load(response)

IP=data['ip']
org=data['org']
city = data['city']
country=data['country']
region=data['region']
"""
"""
from urllib.request import urlopen
from json import load
#if addr == '':
url = 'https://ipinfo.io/json'
#else:
#    url = 'https://ipinfo.io/' + addr + '/json'

res = urlopen(url)
#response from url(if res==None then check connection)
data = load(res)
#will load the json response into data
for attr in data.keys():
    #will print the data line by line
    print(attr,' '*13+'\t->\t',data[attr])
"""
"""
import urllib.request
import json

with urllib.request.urlopen("https://geolocation-db.com/jsonp/8.8.8.8") as url:
    data = url.read().decode()
    data = data.split("(")[1].strip(")")
    print(data)
"""

import socket


def get_ip():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.settimeout(0)
  try:
    # doesn't even have to be reachable
    s.connect(('10.254.254.254', 1))
    IP = s.getsockname()[0]
  except Exception:
    IP = '127.0.0.1'
  finally:
    s.close()
  return IP


print(get_ip())


"""
import urllib.request
import json

with urllib.request.urlopen("https://geolocation-db.com/json") as url:
    data = json.loads(url.read().decode())
    print(data)
"""

