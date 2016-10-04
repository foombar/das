#!/usr/bin/env python
"""
  pip install docker-py

select mean(cpu_ratio) from docker where (container = '1e7563c03ae9' or container = '44fc2346b432') and time > now() - 10m
select mean(cpu_ratio) from docker where service = 'serviceid' and time > now() - 10m
"""

import argparse
import json
import subprocess
import platform
from docker import Client
from influxdb import InfluxDBClient

dbhost = "172.16.10.130"
dbport = 8086
dbuser = "docker"
dbpass = "docker"
dbname = "docker"

dbclient = InfluxDBClient(dbhost, dbport, dbuser, dbpass, dbname)
dockerclient = Client(base_url='unix://var/run/docker.sock')

def parse_args():
    parser = argparse.ArgumentParser(description='docker stats write to InfluxDB')
    parser.add_argument('--host', type=str, required=False, default='localhost',
                        help='hostname of InfluxDB http API')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port of InfluxDB http API')
    return parser.parse_args()

def getContainer(service):
    # filters = id, name, service, node, label, desired-state
    slots = dockerclient.tasks(filters={"service":service, "desired-state":"running"})
    for container in slots:
      print container["Status"]["ContainerStatus"]["ContainerID"]
    
def docker_services():
    services = dockerclient.services()
    for svc in services:
      print svc["ID"], svc["Spec"]["Name"]

def influx_test():
    service = 'cz39bqf8mntal09ihuttinnfh'
#    sql = "select mean(cpu_ratio) from docker where service = '"+service+"' and time > now() - 10m"
    sql = "select mean(cpu_ratio) from docker where service = '"+service+"'"
    result = dbclient.query(sql)
    print result.keys()
    print result.items()
    print result.raw

def main():
    docker_services()
    getContainer("web9000")
#    influx_test()

if __name__ == '__main__':
    args = parse_args()
    main()
