#!/usr/bin/env python
import requests
import os
import sys
import time

cache_file = "/tmp/nginx.stat"
life_time = 30


def parse(text):
    lines = text.split("\n")
    l = lines[0].strip()
    # "Active connections: 1"
    t = dict()
    t['active'] = int(l[l.rfind(":") + 1:].strip())
    # "server accepts handled requests"
    # " 9 9 25"
    l = lines[2].strip()
    tmp = l.split(" ")
    t['accepts'] = int(tmp[0])
    t['handled'] = int(tmp[1])
    t['requests'] = int(tmp[2])

    # "Reading: 0 Writing: 1 Waiting: 0"
    l = lines[3].strip()
    tmp = l.split(" ")
    t['reading'] = int(tmp[1])
    t['writing'] = int(tmp[3])
    t['waiting'] = int(tmp[5])
    # print metric
    return t


def run():
    if len(sys.argv) < 2:
        return 0
    metric = sys.argv[1].lower()
    now = time.time()
    if os.path.isfile(cache_file) and (abs(now - os.path.getctime(cache_file)) < life_time):
        result = open(cache_file).read()
    else:
        result = requests.get("http://localhost/nginx_status").text
        c = open(cache_file, "w")
        c.write(result)
        c.close()
    t = parse(result)
    if metric in t.keys():
        return t.get(metric)
    return 0


if __name__ == "__main__":
    print run()

