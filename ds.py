#!/usr/bin/env python
"""
  docker run -p 8083:8083 -p 8086:8086 \
      -v $PWD:/var/lib/influxdb \
      influxdb

  pip install influxdb
  CREATE USER "docker" WITH PASSWORD 'docker'
  CREATE DATABASE "docker"

"""
import argparse
import json
import subprocess
import platform
import random
from influxdb import InfluxDBClient

dbhost = "10.0.4.161"
dbport = 8086
dbuser = "docker"
dbpass = "docker"
dbname = "docker"

dbclient = InfluxDBClient(dbhost, dbport, dbuser, dbpass, dbname)

def parse_args():
    parser = argparse.ArgumentParser(description='docker stats write to InfluxDB')
    parser.add_argument('--host', type=str, required=False, default='localhost',
                        help='hostname of InfluxDB http API')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port of InfluxDB http API')
    return parser.parse_args()

def tovalue(value, unit):
  v = float(value)
  u = unit[0].lower()
  if u == 'k':
    v *=  1000
  elif u == 'm':
    v *= 1000000
  elif u == 'g':
    v *= 1000000000
  return v


def writeInflux(json_body):
  dbclient.write_points(json_body)

def getServices(containers):
  consvr = {}
  cmds = []
  cmds.append('docker')
  cmds.append('inspect')
  cmds.append('-f')
#  cmds.append('"{{index .Config.Labels \"com.docker.swarm.service.id\"}}","{{index .Config.Labels \"com.docker.swarm.service.name\"}}"')
  cmds.append('"{{index .Config.Labels \"com.docker.swarm.service.id\"}}"')
  for c in containers:
    cmds.append(c)

  proc = subprocess.Popen(cmds, stdout=subprocess.PIPE)
  for c in containers:
    consvr[c] = proc.stdout.readline().rstrip().strip('"')

  # container_id, service_id
  return consvr

def getContainers():
  cmd = "docker ps --format {{.ID}}"
  proc = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
  containers = ""
  while True:
    line = proc.stdout.readline()
    if line == '':
       break
    else:
      containers += line.rstrip() + " "
  cons = containers.split()
  return cons

def getStat(consvr):
  cmd = "docker stats --no-stream"
  proc = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
  skip = True
  """
  CONTAINER         CPU %    MEM USAGE       / LIMIT             MEM %     NET I/O                           BLOCK I/O                          PIDS
  ['1e7563c03ae9', '0.04%', '26.38', 'MiB', '/', '2.922', 'GiB', '0.88%', '100.1', 'kB', '/', '41.29', 'kB', '3.047', 'MB', '/', '7.545', 'MB', '0']
  stats = {c: client.stats(c, stream=0) for c in ids}
  """
  json_body = []
  while True:
    line = proc.stdout.readline()
    if line == '':
       break
    else:
      if skip == True:
        skip = False
        continue
      items = line.rstrip().split()
      cpu_ratio = float(items[1].strip('%'))
      mem_usage = tovalue(items[2], items[3])
      mem_limit = tovalue(items[5], items[6])
      mem_ratio = float(items[7].strip('%'))
      net_read = tovalue(items[8], items[9])
      net_write = tovalue(items[11], items[12])
      blk_read = tovalue(items[13], items[14])
      blk_write = tovalue(items[16], items[17])
      container = items[0]
      json = {
        "measurement": "docker",
        "tags": {
          "node": platform.node(),
          "container": container,
          "service": consvr[container]
        },
        "fields": {
          "cpu_ratio": random.randrange(100)+0.0,
          "mem_usage": mem_usage,
          "mem_limit": mem_limit,
          "mem_ratio": mem_ratio,
          "net_read" : net_read,
          "net_write": net_write,
          "blk_read" : blk_read,
          "blk_write": blk_write
        }
      }
      json_body.append(json)
  return json_body

def main():
  cons = getContainers()
  consvr = getServices(cons)
  json_body = getStat(consvr)
  writeInflux(json_body)

if __name__ == '__main__':
    args = parse_args()
    main()
