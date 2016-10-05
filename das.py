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
from crate import client

idbhost = "10.0.4.161"
idbport = 8086
idbuser = "docker"
idbpass = "docker"
idbname = "docker"

cdbhost = "10.0.4.161:4200"

dockerclient = Client(base_url='unix://var/run/docker.sock')
idbclient = InfluxDBClient(idbhost, idbport, idbuser, idbpass, idbname)

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

def getPolicy(service):
    cdbclient = client.connect(cdbhost)
    cursor = cdbclient.cursor()
    cursor.execute("select service_id, cond_item, min_no, max_no, cur_no, out_cond, in_cond, out_duration, in_duration from das where service_id = ?", (service,))
    result = cursor.fetchall()
    for row in result:
      print row
    cursor.close()
    cdbclient.close()
    
def docker_services():
    services = dockerclient.services()
    for svc in services:
      print svc["ID"], svc["Spec"]["Name"]

def influx_test():
    service = 'cz39bqf8mntal09ihuttinnfh'
#    sql = "select mean(cpu_ratio) from docker where service = '"+service+"' and time > now() - 10m"
    sql = "select mean(cpu_ratio) from docker where service = '"+service+"'"
#    sql = "select mean(cpu_ratio) from docker"
    result = idbclient.query(sql)
    print result.keys()
    print result.items()
    print result.raw

def main():
    docker_services()
    getContainer("web9000")
    getPolicy("6dnh8i971l5h")
#    influx_test()

if __name__ == '__main__':
    args = parse_args()
    main()
