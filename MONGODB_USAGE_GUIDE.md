# MongoDB & Logstash 사용 가이드

> **작성자**: KCB IT AI 추진단  
> **날짜**: 2025-08-12  
> **버전**: 1.0.0

---

## 📋 개요

이 가이드는 OpenSearch 플러그인 테스트 환경에서 MongoDB와 Logstash를 사용하는 방법을 설명합니다.

---

## 🚀 빠른 시작

### 1. 환경 시작
```bash
# 전체 환경 시작
docker-compose up -d

# MongoDB만 시작
docker-compose up -d mongodb

# Logstash만 시작
docker-compose up -d logstash
```

### 2. 연결 확인
```bash
# MongoDB 연결 확인
docker exec -it test-mongodb mongosh --eval "db.adminCommand('ping')"

# Logstash 상태 확인
curl http://localhost:9600

# OpenSearch 연결 확인
curl -k -u admin:Kcb2025opSLabAi9 https://localhost:9200
```

---

## 🗄️ MongoDB 사용법

### 📊 데이터베이스 접속
```bash
# MongoDB 컨테이너 접속
docker exec -it test-mongodb mongosh

# 데이터베이스 선택
use opensearch_test

# 컬렉션 목록 확인
show collections
```

### 🔍 기본 쿼리
```javascript
// 고객 데이터 조회
db.customers.find({})

// 고위험 고객 조회
db.customers.find({risk_level: "HIGH"})

// 의심스러운 거래 조회
db.transactions.find({is_suspicious: true})

// 에러 로그 조회
db.system_logs.find({level: "ERROR"})

// 위치 기반 쿼리 (서울 지역)
db.customers.find({"location.city": "서울"})

// 집계 쿼리 (카테고리별 거래 금액)
db.transactions.aggregate([
  {$group: {_id: "$category", total: {$sum: "$amount"}}},
  {$sort: {total: -1}}
])
```

### 📤 데이터 내보내기
```bash
# 전체 컬렉션 내보내기
docker exec -it test-mongodb mongodump --db opensearch_test --out /tmp/backup

# 특정 컬렉션 내보내기
docker exec -it test-mongodb mongoexport --db opensearch_test --collection customers --out /tmp/customers.json

# JSON 형식으로 내보내기
docker exec -it test-mongodb mongoexport --db opensearch_test --collection transactions --out /tmp/transactions.json --jsonArray
```

---

## 🔄 Logstash 사용법

### 📊 파이프라인 상태 확인
```bash
# Logstash 상태 확인
curl http://localhost:9600/_node/stats/pipeline

# 파이프라인 목록 확인
curl http://localhost:9600/_node/pipeline

# 플러그인 목록 확인
curl http://localhost:9600/_node/plugins
```

### 📤 데이터 전송 방법

#### 1. HTTP를 통한 데이터 전송
```bash
# 고객 데이터 전송
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "customers",
    "customer_id": "CUST006",
    "name": "홍길동",
    "age": 30,
    "income": 50000000,
    "credit_score": 700,
    "risk_level": "LOW"
  }'

# 거래 데이터 전송
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "transactions",
    "transaction_id": "TXN006",
    "customer_id": "CUST001",
    "amount": 200000,
    "category": "온라인쇼핑",
    "merchant": "쿠팡",
    "timestamp": "2025-08-12T15:30:00Z",
    "is_suspicious": false,
    "risk_score": 0.1
  }'

# 시스템 로그 전송
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "system_logs",
    "log_id": "LOG006",
    "timestamp": "2025-08-12T15:35:00Z",
    "level": "INFO",
    "service": "user_service",
    "message": "사용자 로그인 성공",
    "details": {
      "cpu_usage": 45.2,
      "memory_usage": 67.8,
      "response_time": 120,
      "active_connections": 150
    }
  }'
```

#### 2. TCP를 통한 데이터 전송
```bash
# TCP 연결로 데이터 전송
echo '{"collection": "transactions", "transaction_id": "TXN007", "amount": 150000}' | nc localhost 5000
```

#### 3. 파일을 통한 데이터 전송
```bash
# JSON 파일을 Logstash 데이터 디렉토리에 복사
cp your_data.json logstash/data/mongodb-export/

# Logstash가 자동으로 파일을 감지하고 처리
```

### 🔧 파이프라인 설정 수정
```bash
# 파이프라인 설정 파일 수정
vim logstash/pipeline/mongodb-simple.conf

# Logstash 재시작
docker-compose restart logstash
```

---

## 🔗 OpenSearch 연동

### 📊 인덱스 확인
```bash
# MongoDB 관련 인덱스 확인
curl -k -u admin:Kcb2025opSLabAi9 https://localhost:9200/_cat/indices/mongodb*?v

# 인덱스 매핑 확인
curl -k -u admin:Kcb2025opSLabAi9 https://localhost:9200/mongodb-customers-*/_mapping
```

### 🔍 데이터 검색
```bash
# 고객 데이터 검색
curl -k -u admin:Kcb2025opSLabAi9 https://localhost:9200/mongodb-customers-*/_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "match": {
        "risk_level": "HIGH"
      }
    }
  }'

# 거래 데이터 검색
curl -k -u admin:Kcb2025opSLabAi9 https://localhost:9200/mongodb-transactions-*/_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"match": {"is_suspicious": true}},
          {"range": {"amount": {"gte": 100000}}}
        ]
      }
    }
  }'
```

---

## 🐍 Python 스크립트 사용법

### 📊 MongoDB 테스트 실행
```bash
# MongoDB 플러그인 테스트
python plugin_test_mongodb.py

# 특정 테스트만 실행
python -c "
from plugin_test_mongodb import MongoDBPluginTest
test = MongoDBPluginTest()
test.setup_mongodb_connection()
test.test_mongodb_data_availability()
"
```

### 🔧 커스텀 스크립트 작성
```python
from pymongo import MongoClient
from opensearchpy import OpenSearch

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017/')
db = client['opensearch_test']

# OpenSearch 연결
opensearch = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'Kcb2025opSLabAi9'),
    use_ssl=True,
    verify_certs=False
)

# 데이터 처리 예시
customers = db.customers.find({})
for customer in customers:
    # OpenSearch에 인덱싱
    opensearch.index(
        index='customers',
        body=customer
    )
```

---

## 🚨 문제 해결

### ❌ MongoDB 연결 실패
```bash
# 컨테이너 상태 확인
docker ps | grep mongodb

# 로그 확인
docker logs test-mongodb

# 컨테이너 재시작
docker-compose restart mongodb
```

### ❌ Logstash 파이프라인 오류
```bash
# Logstash 로그 확인
docker logs opensearch-logstash

# 파이프라인 설정 검증
docker exec -it opensearch-logstash logstash -t -f /usr/share/logstash/pipeline/

# Logstash 재시작
docker-compose restart logstash
```

### ❌ OpenSearch 인덱싱 실패
```bash
# OpenSearch 상태 확인
curl -k -u admin:Kcb2025opSLabAi9 https://localhost:9200/_cluster/health

# 인덱스 상태 확인
curl -k -u admin:Kcb2025opSLabAi9 https://localhost:9200/_cat/indices?v
```

---

## 📈 모니터링

### 📊 성능 모니터링
```bash
# MongoDB 성능 통계
docker exec -it test-mongodb mongosh --eval "db.stats()"

# Logstash 성능 통계
curl http://localhost:9600/_node/stats

# OpenSearch 성능 통계
curl -k -u admin:Kcb2025opSLabAi9 https://localhost:9200/_cluster/stats
```

### 🔍 로그 모니터링
```bash
# MongoDB 로그 실시간 확인
docker logs -f test-mongodb

# Logstash 로그 실시간 확인
docker logs -f opensearch-logstash

# OpenSearch 로그 실시간 확인
docker logs -f opensearch
```

---

## 🎯 활용 예시

### 💼 실시간 거래 모니터링
```python
# 실시간 거래 데이터 수집 및 분석
import time
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['opensearch_test']

# 실시간 거래 모니터링
pipeline = [
    {'$match': {'operationType': 'insert'}},
    {'$project': {'fullDocument': 1}}
]

with db.transactions.watch(pipeline) as stream:
    for change in stream:
        transaction = change['fullDocument']
        if transaction['is_suspicious']:
            print(f"🚨 의심스러운 거래 감지: {transaction['transaction_id']}")
```

### 📊 대시보드 구축
```bash
# OpenSearch Dashboards에서 대시보드 생성
# 1. http://opensearch.local 접속
# 2. Dashboard > Create Dashboard
# 3. Visualizations 추가:
#    - 거래 금액 분포
#    - 위험도별 고객 분포
#    - 시간대별 거래 패턴
#    - 시스템 성능 메트릭
```

---

## 📚 추가 자료

- [MongoDB 공식 문서](https://docs.mongodb.com/)
- [Logstash 공식 문서](https://www.elastic.co/guide/en/logstash/current/index.html)
- [OpenSearch 공식 문서](https://opensearch.org/docs/)

---

**문서 버전**: 1.0.0  
**마지막 업데이트**: 2025-08-12
