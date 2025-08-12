#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB 플러그인 테스트
OpenSearch와 MongoDB 연동 테스트
"""

import json
import time
from datetime import datetime
from plugin_test_base import PluginTesterBase
import requests
from pymongo import MongoClient
import logging

class MongoDBPluginTest(PluginTesterBase):
    """MongoDB 플러그인 테스트 클래스"""
    
    def __init__(self):
        super().__init__()
        self.mongodb_client = None
        self.mongodb_db = None
        self.test_results = []
        
    def setup_mongodb_connection(self):
        """MongoDB 연결 설정"""
        try:
            self.mongodb_client = MongoClient('mongodb://localhost:27017/')
            self.mongodb_db = self.mongodb_client['opensearch_test']
            logging.info("✅ MongoDB 연결 성공")
            return True
        except Exception as e:
            logging.error(f"❌ MongoDB 연결 실패: {e}")
            return False
    
    def test_mongodb_data_availability(self):
        """MongoDB 데이터 가용성 테스트"""
        logging.info("=== 🔍 MongoDB 데이터 가용성 테스트 ===")
        
        try:
            # 컬렉션 확인
            collections = self.mongodb_db.list_collection_names()
            logging.info(f"📦 사용 가능한 컬렉션: {collections}")
            
            # 각 컬렉션의 문서 수 확인
            for collection_name in collections:
                count = self.mongodb_db[collection_name].count_documents({})
                logging.info(f"   - {collection_name}: {count}개 문서")
            
            # 고객 데이터 확인
            customers = list(self.mongodb_db.customers.find({}, {'_id': 0, 'name': 1, 'risk_level': 1}).limit(3))
            logging.info(f"📊 고객 데이터 샘플: {customers}")
            
            # 거래 데이터 확인
            transactions = list(self.mongodb_db.transactions.find({}, {'_id': 0, 'amount': 1, 'is_suspicious': 1}).limit(3))
            logging.info(f"💰 거래 데이터 샘플: {transactions}")
            
            # 시스템 로그 확인
            logs = list(self.mongodb_db.system_logs.find({}, {'_id': 0, 'level': 1, 'service': 1}).limit(3))
            logging.info(f"📝 시스템 로그 샘플: {logs}")
            
            self.test_results.append({
                'test': 'mongodb_data_availability',
                'status': 'success',
                'message': f'총 {len(collections)}개 컬렉션 확인'
            })
            return True
            
        except Exception as e:
            logging.error(f"❌ MongoDB 데이터 확인 실패: {e}")
            self.test_results.append({
                'test': 'mongodb_data_availability',
                'status': 'error',
                'message': str(e)
            })
            return False
    
    def test_mongodb_queries(self):
        """MongoDB 쿼리 테스트"""
        logging.info("=== 🔍 MongoDB 쿼리 테스트 ===")
        
        try:
            # 1. 고위험 고객 조회
            high_risk_customers = list(self.mongodb_db.customers.find(
                {'risk_level': 'HIGH'}, 
                {'_id': 0, 'name': 1, 'credit_score': 1, 'risk_level': 1}
            ))
            logging.info(f"⚠️ 고위험 고객: {len(high_risk_customers)}명")
            
            # 2. 의심스러운 거래 조회
            suspicious_transactions = list(self.mongodb_db.transactions.find(
                {'is_suspicious': True},
                {'_id': 0, 'amount': 1, 'merchant': 1, 'risk_score': 1}
            ))
            logging.info(f"🚨 의심스러운 거래: {len(suspicious_transactions)}건")
            
            # 3. 에러 로그 조회
            error_logs = list(self.mongodb_db.system_logs.find(
                {'level': 'ERROR'},
                {'_id': 0, 'service': 1, 'message': 1}
            ))
            logging.info(f"❌ 에러 로그: {len(error_logs)}건")
            
            # 4. 위치 기반 쿼리 (서울 지역)
            seoul_customers = list(self.mongodb_db.customers.find(
                {'location.city': '서울'},
                {'_id': 0, 'name': 1, 'location.district': 1}
            ))
            logging.info(f"🏙️ 서울 지역 고객: {len(seoul_customers)}명")
            
            # 5. 집계 쿼리 (카테고리별 거래 금액)
            pipeline = [
                {'$group': {'_id': '$category', 'total_amount': {'$sum': '$amount'}, 'count': {'$sum': 1}}},
                {'$sort': {'total_amount': -1}}
            ]
            category_stats = list(self.mongodb_db.transactions.aggregate(pipeline))
            logging.info(f"📊 카테고리별 통계: {category_stats}")
            
            self.test_results.append({
                'test': 'mongodb_queries',
                'status': 'success',
                'message': f'5개 쿼리 성공 실행'
            })
            return True
            
        except Exception as e:
            logging.error(f"❌ MongoDB 쿼리 테스트 실패: {e}")
            self.test_results.append({
                'test': 'mongodb_queries',
                'status': 'error',
                'message': str(e)
            })
            return False
    
    def test_logstash_integration(self):
        """Logstash 연동 테스트"""
        logging.info("=== 🔄 Logstash 연동 테스트 ===")
        
        try:
            # Logstash 상태 확인
            logstash_url = "http://localhost:9600"
            response = requests.get(logstash_url, timeout=5)
            
            if response.status_code == 200:
                logging.info("✅ Logstash 서비스 정상 동작")
                
                # 테스트 데이터를 Logstash로 전송
                test_data = {
                    "collection": "transactions",
                    "transaction_id": "TEST001",
                    "customer_id": "CUST001",
                    "amount": 100000,
                    "category": "테스트",
                    "merchant": "테스트상점",
                    "timestamp": datetime.now().isoformat(),
                    "is_suspicious": False,
                    "risk_score": 0.1
                }
                
                # HTTP를 통해 Logstash로 데이터 전송
                logstash_http_url = "http://localhost:8080"
                response = requests.post(
                    logstash_http_url,
                    json=test_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    logging.info("✅ Logstash로 테스트 데이터 전송 성공")
                    self.test_results.append({
                        'test': 'logstash_integration',
                        'status': 'success',
                        'message': 'Logstash 연동 성공'
                    })
                    return True
                else:
                    logging.warning(f"⚠️ Logstash 데이터 전송 실패: {response.status_code}")
                    self.test_results.append({
                        'test': 'logstash_integration',
                        'status': 'warning',
                        'message': f'데이터 전송 실패: {response.status_code}'
                    })
                    return False
            else:
                logging.warning(f"⚠️ Logstash 서비스 응답: {response.status_code}")
                self.test_results.append({
                    'test': 'logstash_integration',
                    'status': 'warning',
                    'message': f'Logstash 서비스 응답: {response.status_code}'
                })
                return False
                
        except requests.exceptions.RequestException as e:
            logging.warning(f"⚠️ Logstash 연결 실패: {e}")
            self.test_results.append({
                'test': 'logstash_integration',
                'status': 'warning',
                'message': f'Logstash 연결 실패: {str(e)}'
            })
            return False
        except Exception as e:
            logging.error(f"❌ Logstash 연동 테스트 실패: {e}")
            self.test_results.append({
                'test': 'logstash_integration',
                'status': 'error',
                'message': str(e)
            })
            return False
    
    def test_opensearch_integration(self):
        """OpenSearch 연동 테스트"""
        logging.info("=== 🔗 OpenSearch 연동 테스트 ===")
        
        try:
            # MongoDB 데이터를 OpenSearch로 직접 전송
            # 고객 데이터 샘플 전송
            customers_sample = list(self.mongodb_db.customers.find({}, {'_id': 0}).limit(2))
            
            for customer in customers_sample:
                # OpenSearch에 직접 인덱싱
                index_name = "mongodb-customers-direct"
                response = self.client.index(
                    index=index_name,
                    body=customer
                )
                
                if response['result'] == 'created':
                    logging.info(f"✅ 고객 데이터 인덱싱 성공: {customer.get('name', 'Unknown')}")
            
            # 거래 데이터 샘플 전송
            transactions_sample = list(self.mongodb_db.transactions.find({}, {'_id': 0}).limit(2))
            
            for transaction in transactions_sample:
                index_name = "mongodb-transactions-direct"
                response = self.client.index(
                    index=index_name,
                    body=transaction
                )
                
                if response['result'] == 'created':
                    logging.info(f"✅ 거래 데이터 인덱싱 성공: {transaction.get('transaction_id', 'Unknown')}")
            
            # 인덱스 확인
            indices = self.client.cat.indices(format='json')
            mongodb_indices = [idx for idx in indices if 'mongodb' in idx['index']]
            logging.info(f"📊 MongoDB 관련 인덱스: {len(mongodb_indices)}개")
            
            self.test_results.append({
                'test': 'opensearch_integration',
                'status': 'success',
                'message': f'OpenSearch 연동 성공, {len(mongodb_indices)}개 인덱스 생성'
            })
            return True
            
        except Exception as e:
            logging.error(f"❌ OpenSearch 연동 테스트 실패: {e}")
            self.test_results.append({
                'test': 'opensearch_integration',
                'status': 'error',
                'message': str(e)
            })
            return False
    
    def test_plugin(self):
        """MongoDB 플러그인 전체 테스트"""
        logging.info("🚀 MongoDB 플러그인 테스트 시작")
        
        # MongoDB 연결
        if not self.setup_mongodb_connection():
            return False
        
        # 테스트 실행
        tests = [
            self.test_mongodb_data_availability,
            self.test_mongodb_queries,
            self.test_logstash_integration,
            self.test_opensearch_integration
        ]
        
        success_count = 0
        for test in tests:
            try:
                if test():
                    success_count += 1
            except Exception as e:
                logging.error(f"❌ 테스트 실행 중 오류: {e}")
        
        # 결과 요약
        logging.info(f"\n📊 MongoDB 플러그인 테스트 결과: {success_count}/{len(tests)} 성공")
        
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'success' else "⚠️" if result['status'] == 'warning' else "❌"
            logging.info(f"{status_icon} {result['test']}: {result['message']}")
        
        # MongoDB 연결 종료
        if self.mongodb_client:
            self.mongodb_client.close()
        
        return success_count >= len(tests) * 0.7  # 70% 이상 성공 시 통과

if __name__ == "__main__":
    test = MongoDBPluginTest()
    success = test.test_plugin()
    exit(0 if success else 1)
