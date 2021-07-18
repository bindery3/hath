import csv
import os
import re
import time

import requests
import yaml
from lxml import etree


class HatH(object):
    def __init__(self):
        self.conf_file = 'config.yaml'
        self.csv_path = 'data'
        self.url = 'https://e-hentai.org/hentaiathome.php'
        self.headers = {
            'Cookie': '',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.id_list = []
        self.client_list = []
        self.configuration()

    def configuration(self):
        with open(self.conf_file, 'r', encoding='utf-8') as f:
            conf = yaml.load(f, Loader=yaml.FullLoader)
            self.headers['Cookie'] = conf['cookie']
            if 'client' in conf.keys():
                self.id_list = conf['client']

    def get_static_ranges(self, cid):
        url = self.url + '?cid=' + cid
        r = requests.get(url=url, headers=self.headers, timeout=5)
        html = etree.HTML(r.content)
        ranges = html.xpath('/html/body/div[2]/form/div/table[2]/tr[11]/td[2]/p[1]/span/text()')[0]
        time.sleep(0.1)
        return ranges

    def get_status(self):
        r = requests.get(url=self.url, headers=self.headers, timeout=5)
        html = etree.HTML(r.content)
        c_list = html.xpath('/html/body/div[2]/div[2]/table/*')[1:]
        for c in c_list:
            values = c.xpath('.//*/text()')
            if self.id_list and int(values[1]) not in self.id_list:
                continue
            status = [1 if values[2] == 'Online' else 0,  # Status
                      values[10][1:],  # Trust
                      values[11],  # Quality
                      re.sub(r'[^\d.]', '', values[12]),  # Hitrate
                      re.sub(r'[^\d.]', '', values[13]),  # Hathrate
                      self.get_static_ranges(values[1])  # Static Ranges
                      ]
            client = {'name': values[0],
                      'id': values[1],
                      'status': status
                      }
            self.client_list.append(client)

    def write(self):
        if not os.path.exists(self.csv_path):
            os.mkdir(self.csv_path)
        for c in self.client_list:
            csv_file = os.path.join(self.csv_path, c['id'] + '_' + c['name'] + '.csv')
            with open(csv_file, 'a', encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                data = c['status']
                writer.writerow(data)


def main():
    h = HatH()
    h.get_status()
    h.write()


if __name__ == '__main__':
    main()
