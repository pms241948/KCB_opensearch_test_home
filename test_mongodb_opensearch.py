#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB와 OpenSearch 직접 연동 테스트
"""

import json
import time
from datetime import datetime
from plugin_test_base import PluginTesterBase
from pymongo import MongoClient
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

class MongoDBOpenSearchTest(PluginTesterBase):
    """MongoDB와 OpenSearch 직접 연동 테스트 클래스"""
    
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
    
    def test_mongodb_data(self):
        """MongoDB 데이터 확인"""
        logging.info("=== 🔍 MongoDB 데이터 확인 ===")
        
        try:
            # 컬렉션 확인
            collections = self.mongodb_db.list_collection_names()
            logging.info(f"📦 사용 가능한 컬렉션: {collections}")
            
            # 각 컬렉션의 문서 수 확인
            for collection_name in collections:
                count = self.mongodb_db[collection_name].count_documents({})
                logging.info(f"   - {collection_name}: {count}개 문서")
            
            # 고객 데이터 샘플 확인
            customers = list(self.mongodb_db.customers.find({}, {'_id': 0, 'name': 1, 'risk_level': 1}).limit(3))
            logging.info(f"📊 고객 데이터 샘플: {customers}")
            
            # 거래 데이터 샘플 확인
            transactions = list(self.mongodb_db.transactions.find({}, {'_id': 0, 'amount': 1, 'is_suspicious': 1}).limit(3))
            logging.info(f"💰 거래 데이터 샘플: {transactions}")
            
            self.test_results.append({
                'test': 'mongodb_data',
                'status': 'success',
                'message': f'총 {len(collections)}개 컬렉션, {sum([self.mongodb_db[col].count_documents({}) for col in collections])}개 문서 확인'
            })
            return True
            
        except Exception as e:
            logging.error(f"❌ MongoDB 데이터 확인 실패: {e}")
            self.test_results.append({
                'test': 'mongodb_data',
                'status': 'error',
                'message': str(e)
            })
            return False
    
    def test_opensearch_connection(self):
        """OpenSearch 연결 확인"""
        logging.info("=== 🔗 OpenSearch 연결 확인 ===")
        
        try:
            info = self.client.info()
            logging.info(f"✅ OpenSearch 버전: {info['version']['number']}")
            logging.info(f"✅ 클러스터: {info['cluster_name']}")
            
            self.test_results.append({
                'test': 'opensearch_connection',
                'status': 'success',
                'message': f'OpenSearch {info["version"]["number"]} 연결 성공'
            })
            return True
            
        except Exception as e:
            logging.error(f"❌ OpenSearch 연결 실패: {e}")
            self.test_results.append({
                'test': 'opensearch_connection',
                'status': 'error',
                'message': str(e)
            })
            return False
    
    def test_data_transfer(self):
        """MongoDB에서 OpenSearch로 데이터 전송 테스트"""
        logging.info("=== 📤 MongoDB → OpenSearch 데이터 전송 테스트 ===")
        
        try:
            # 고객 데이터 전송
            customers_sample = list(self.mongodb_db.customers.find({}, {'_id': 0}).limit(2))
            customer_count = 0
            
            for customer in customers_sample:
                response = self.client.index(
                    index="mongodb-customers-test",
                    body=customer
                )
                if response['result'] == 'created':
                    customer_count += 1
                    logging.info(f"✅ 고객 데이터 인덱싱: {customer.get('name', 'Unknown')}")
            
            # 거래 데이터 전송
            transactions_sample = list(self.mongodb_db.transactions.find({}, {'_id': 0}).limit(2))
            transaction_count = 0
            
            for transaction in transactions_sample:
                response = self.client.index(
                    index="mongodb-transactions-test",
                    body=transaction
                )
                if response['result'] == 'created':
                    transaction_count += 1
                    logging.info(f"✅ 거래 데이터 인덱싱: {transaction.get('transaction_id', 'Unknown')}")
            
            # 인덱스 확인
            indices = self.client.cat.indices(format='json')
            mongodb_indices = [idx for idx in indices if 'mongodb' in idx['index']]
            logging.info(f"📊 MongoDB 관련 인덱스: {len(mongodb_indices)}개")
            
            self.test_results.append({
                'test': 'data_transfer',
                'status': 'success',
                'message': f'고객 {customer_count}개, 거래 {transaction_count}개 전송, 총 {len(mongodb_indices)}개 인덱스'
            })
            return True
            
        except Exception as e:
            logging.error(f"❌ 데이터 전송 실패: {e}")
            self.test_results.append({
                'test': 'data_transfer',
                'status': 'error',
                'message': str(e)
            })
            return False
    
    def test_search_functionality(self):
        """OpenSearch 검색 기능 테스트"""
        logging.info("=== 🔍 OpenSearch 검색 기능 테스트 ===")
        
        try:
            # 고객 데이터 검색
            search_result = self.client.search(
                index="mongodb-customers-test",
                body={
                    "query": {
                        "match": {
                            "risk_level": "HIGH"
                        }
                    }
                }
            )
            
            high_risk_count = search_result['hits']['total']['value']
            logging.info(f"⚠️ 고위험 고객 검색 결과: {high_risk_count}명")
            
            # 거래 데이터 검색
            search_result = self.client.search(
                index="mongodb-transactions-test",
                body={
                    "query": {
                        "match": {
                            "is_suspicious": True
                        }
                    }
                }
            )
            
            suspicious_count = search_result['hits']['total']['value']
            logging.info(f"🚨 의심스러운 거래 검색 결과: {suspicious_count}건")
            
            self.test_results.append({
                'test': 'search_functionality',
                'status': 'success',
                'message': f'고위험 고객 {high_risk_count}명, 의심 거래 {suspicious_count}건 검색 성공'
            })
            return True
            
        except Exception as e:
            logging.error(f"❌ 검색 기능 테스트 실패: {e}")
            self.test_results.append({
                'test': 'search_functionality',
                'status': 'error',
                'message': str(e)
            })
            return False
    
    def run_tests(self):
        """전체 테스트 실행"""
        logging.info("🚀 MongoDB ↔ OpenSearch 직접 연동 테스트 시작")
        
        # MongoDB 연결
        if not self.setup_mongodb_connection():
            return False
        
        # 테스트 실행
        tests = [
            self.test_mongodb_data,
            self.test_opensearch_connection,
            self.test_data_transfer,
            self.test_search_functionality
        ]
        
        success_count = 0
        for test in tests:
            try:
                if test():
                    success_count += 1
            except Exception as e:
                logging.error(f"❌ 테스트 실행 중 오류: {e}")
        
        # 결과 요약
        logging.info(f"\n📊 테스트 결과: {success_count}/{len(tests)} 성공")
        
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            logging.info(f"{status_icon} {result['test']}: {result['message']}")
        
        # MongoDB 연결 종료
        if self.mongodb_client:
            self.mongodb_client.close()
        
        return success_count >= len(tests) * 0.7  # 70% 이상 성공 시 통과

if __name__ == "__main__":
    test = MongoDBOpenSearchTest()
    success = test.run_tests()
    exit(0 if success else 1)
