### Docker Auto Scaling

## 구성 및 설치
  * manager : swarm manager
    + influxdb
    + das(docker auto scaler)
  * worker1 : swarm worker1
    + ds(docker stats/service_id -> influxdb)
  * worker2 : swarm worker2
    + ds(docker stats/service_id -> influxdb)

## Flow
1. worker 노드들은 ds(docker stats)를 수행하여 주기적으로 influxdb(manager) 에 적재(container의 service_id 포함)  
2. das는 서비스 id 로 주기적으로 influxdb를 쿼리하여 스케일링 조건에 맞는지 검사

  ex) select mean(cpu_ratio) from docker where service = 'service_id' and time > now() - 10m
3. 조건에 맞을 경우 docker service update --replicas n 를 수행

## docker stats
* tags
  * node
  * container
  * service
* fields
  * cpu_ratio
  * mem_usage
  * mem_limit
  * mem_ratio
  * net_read
  * net_write
  * blk_read
  * blk_write

## Test 
* manager
  + docker service create --name myweb --replicas 3 nginx
  + docker run -d -p 8083:8083 -p 8086:8086 -v $PWD:/var/lib/influxdb influxdb
    + http://manager:8083
    + create database "docker"
    + create user "docker" with password "docker"
  + pip install docker-py
  + pip install influxdb
  + change influxdb setup(dbhost/dbip/dbuser/dbpass/dbname) in das.py
  + $ ./das.py
    
* worker
  + pip install influxdb
  + $ ./ds.py
  
## POLICY
* MIN_NO		최소 컨테이너 수
* MAX_NO		최대 컨테이너 수
* COND_ITEM	조건 대상(cpu_ratio, ...)
* OUT_COND	확장 조건(70%)
* IN_COND		축소 조건(10%)
* OUT_DURATION	확장 조건 충족 시간(10m)
* IN_COND		축소 조건 충족 시간(10m)
* SERVICE_ID	서비스 ID

## Scale sql
* 10분 이내에, 두개의 컨테이너로 구성되는 서비스의 평균 CPU 점유율
  + select mean(cpu_ratio) from docker where container = '1e7563c03ae9' or container = '44fc2346b432' time > now() - 10m

* 10분 이내에, 서비스id를 구성하는 컨테이너의 평균 CPU 점유율
  + select mean(cpu_ratio) from docker where service = 'serviceid' and time > now() - 10m
