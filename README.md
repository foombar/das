Docker Auto Scaling

* Test

docker service create --name myweb --replicas 3 nginx
service 목록에서 컨테이너ID 찾기
docker service ls
[service id]
docker service ps [service id]
[task id]
docker inspect [task id]
[container id] ... array

* POLICY

MIN_NO		최소 컨테이너 수
MAX_NO		최대 컨테이너 수
COND_ITEM	조건 대상(cpu_ratio)
OUT_COND	확장 조건
IN_COND		축소 조건
OUT_DURATION	확장 조건 충족 시간
IN_COND		축소 조건 축소 시간
SERVICE_ID	서비스 ID

// 10분 이내에, 두개의 컨테이너로 구성되는 서비스의 평균 CPU 점유율
select mean(cpu_ratio) from docker where container = '1e7563c03ae9' or container = '44fc2346b432' time > now() - 10m
