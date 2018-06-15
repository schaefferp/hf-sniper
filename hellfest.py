#!/usr/bin/python
# coding=utf-8

""" Quick'n'dirty sniper"""

import random
import re
import subprocess
import sys
import time

import bs4
import json
import requests

RECIPIENT_EMAIL = ''

log = sys.stdout.write

hf = requests.get('https://hellfest.zepass.com/achat-billet/r/462365')

cookies = { 'PHPSESSID': hf.cookies['PHPSESSID'] }

headers = { 'x-csrf-token': re.search('updateHeaderCsrfToken\(\"(.*?)\"\)', hf.text).group(1).replace('\\', '') }

data = [
    ('sEcho', '1'),
    ('iColumns', '6'),
    ('sColumns', ''),
    ('iDisplayStart', '0'),
    ('iDisplayLength', '15'),
    ('mDataProp_0', '0'),
    ('mDataProp_1', '1'),
    ('mDataProp_2', '2'),
    ('mDataProp_3', '3'),
    ('mDataProp_4', '4'),
    ('mDataProp_5', '5'),
    ('sSearch', ''),
    ('bRegex', 'false'),
    ('sSearch_0', ''),
    ('bRegex_0', 'false'),
    ('bSearchable_0', 'true'),
    ('sSearch_1', ''),
    ('bRegex_1', 'false'),
    ('bSearchable_1', 'true'),
    ('sSearch_2', ''),
    ('bRegex_2', 'false'),
    ('bSearchable_2', 'true'),
    ('sSearch_3', ''),
    ('bRegex_3', 'false'),
    ('bSearchable_3', 'true'),
    ('sSearch_4', ''),
    ('bRegex_4', 'false'),
    ('bSearchable_4', 'true'),
    ('sSearch_5', ''),
    ('bRegex_5', 'false'),
    ('bSearchable_5', 'true'),
    ('iSortingCols', '0'),
    ('bSortable_0', 'false'),
    ('bSortable_1', 'false'),
    ('bSortable_2', 'false'),
    ('bSortable_3', 'true'),
    ('bSortable_4', 'false'),
    ('bSortable_5', 'false'),
    ('id', 'tab-mb_billets')
]

raw = requests.post('https://hellfest.zepass.com/tabdyn/index', headers=headers, data=data, cookies=cookies).text
js = json.loads(raw)

while True:
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    log('{0} | Checking... '.format(now))
    if js['aaData']:
        price_list = []
        for item in js['aaData']:
            soup = bs4.BeautifulSoup(item[2].encode('utf-8').replace('\n', ''), 'lxml')
            price = int(soup.find('span', attrs={'class': 'montant-numeric'}).string)
            price_list.append(price)
        if min(price_list) <= 100:
            buy_list = [str(price) + ' €' for price in sorted(price_list)[:3]]
            log('YAY ! \\o/ Cheapest tickets : {0}'.format(', '.join(buy_list)))
            subprocess.call('echo -e "Subject:HF ticket : {0}\n\nTop 3 prices : {1}\n" | sendmail {2}'.format(buy_list[0], ', '.join(buy_list), RECIPIENT_EMAIL), shell=True)
        else:
            log('No interesting prices. :/ (min: {0} €)'.format(min(price_list)))
    else:
        log('Nope, no tickets. =(')
    log('\n')
    time.sleep(random.randrange(300, 600))
