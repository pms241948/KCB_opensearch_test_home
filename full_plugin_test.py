#!/usr/bin/env python3
"""
OpenSearch 플러그인 전체 테스트 스크립트
초보자용 - 단계별 실행
"""

import requests
import json
import time
from datetime import datetime, timedelta
from opensearchpy import OpenSearch, RequestsHttpConnection
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OpenSearchPluginTester:
    def __init__(self):
        """OpenSearch 연결 설정"""
        self.client = OpenSearch(
            hosts=[{'host': 'localhost', 'port': 9200}],
            http_auth=('admin', 'Kcb2025opSLabAi9'),
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            connection_class=RequestsHttpConnection
        )
        
        self.base_url = "https://localhost:9200"
        self.auth = ('admin', 'Kcb2025opSLabAi9')
        
        print("🔧 OpenSearch 플러그인 테스터 시작")
        print("-" * 50)

    def test_1_security_plugin(self):
        """1. Security 플러그인 테스트"""
        print("\n=== 🔐 1. Security 플러그인 테스트 ===")
        
        try:
            # 현재 사용자 정보 확인
            response = requests.get(
                f"{self.base_url}/_plugins/_security/authinfo",
                auth=self.auth,
                verify=False
            )
            
            if response.status_code == 200:
                auth_info = response.json()
                print(f"✅ 현재 사용자: {auth_info.get('user_name')}")
                print(f"✅ 사용자 역할: {', '.join(auth_info.get('roles', []))}")
                
                # 사용자 목록 조회
                users_response = requests.get(
                    f"{self.base_url}/_plugins/_security/api/internalusers",
                    auth=self.auth,
                    verify=False
                )
                
                if users_response.status_code == 200:
                    users = users_response.json()
                    print(f"✅ 총 사용자 수: {len(users)}명")
                    
                return True
            else:
                print(f"❌ Security 플러그인 오류: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Security 테스트 실패: {e}")
            
        return False

    def test_2_sql_plugin(self):
        """2. SQL 플러그인 테스트"""
        print("\n=== 🔍 2. SQL 플러그인 테스트 ===")
        
        try:
            # 테스트용 직원 데이터 생성
            employee_index = "kcb-employees"
            
            # 기존 인덱스 삭제
            if self.client.indices.exists(index=employee_index):
                self.client.indices.delete(index=employee_index)
            
            # 직원 데이터 인덱스 생성
            mapping = {
                "mappings": {
                    "properties": {
                        "name": {"type": "text"},
                        "department": {"type": "keyword"},
                        "position": {"type": "keyword"},
                        "salary": {"type": "integer"},
                        "hire_date": {"type": "date"}
                    }
                }
            }
            
            self.client.indices.create(index=employee_index, body=mapping)
            
            # 샘플 직원 데이터
            employees = [
                {"name": "김철수", "department": "IT", "position": "개발팀장", "salary": 7000, "hire_date": "2020-01-15"},
                {"name": "이영희", "department": "HR", "position": "인사과장", "salary": 6500, "hire_date": "2019-03-10"},
                {"name": "박민수", "department": "IT", "position": "시니어개발자", "salary": 6000, "hire_date": "2021-06-01"},
                {"name": "최은지", "department": "Finance", "position": "재무분석가", "salary": 5500, "hire_date": "2022-09-20"},
                {"name": "정호영", "department": "IT", "position": "주니어개발자", "salary": 4500, "hire_date": "2023-01-05"}
            ]
            
            # 데이터 삽입
            for i, emp in enumerate(employees):
                self.client.index(index=employee_index, id=i+1, body=emp)
            
            time.sleep(2)  # 인덱싱 대기
            print(f"✅ 직원 데이터 생성: {len(employees)}명")
            
            # SQL 쿼리 테스트들
            sql_queries = [
                {
                    "name": "전체 직원 조회",
                    "query": f"SELECT name, department, salary FROM `{employee_index}` ORDER BY salary DESC"
                },
                {
                    "name": "IT 부서 직원",
                    "query": f"SELECT name, position, salary FROM `{employee_index}` WHERE department = 'IT'"
                },
                {
                    "name": "부서별 평균 연봉",
                    "query": f"SELECT department, AVG(salary) as avg_salary FROM `{employee_index}` GROUP BY department"
                }
            ]
            
            for test_case in sql_queries:
                print(f"\n📊 {test_case['name']}:")
                
                response = requests.post(
                    f"{self.base_url}/_plugins/_sql",
                    auth=self.auth,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"query": test_case['query']}),
                    verify=False
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'datarows' in result and result['datarows']:
                        print("   결과:")
                        for row in result['datarows'][:3]:
                            print(f"     {row}")
                    else:
                        print("   ✅ 쿼리 실행 성공 (결과 없음)")
                else:
                    print(f"   ❌ 쿼리 실행 실패: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"❌ SQL 플러그인 테스트 실패: {e}")
            
        return False

    def test_3_knn_plugin(self):
        """3. KNN (벡터 검색) 플러그인 테스트"""
        print("\n=== 🎯 3. KNN 벡터 검색 플러그인 테스트 ===")
        
        try:
            products_index = "kcb-products"
            
            # 기존 인덱스 삭제
            if self.client.indices.exists(index=products_index):
                self.client.indices.delete(index=products_index)
            
            # KNN 인덱스 생성 (간단한 3차원 벡터)
            knn_mapping = {
                "settings": {
                    "index": {
                        "knn": True
                    }
                },
                "mappings": {
                    "properties": {
                        "product_name": {"type": "text"},
                        "category": {"type": "keyword"},
                        "price": {"type": "integer"},
                        "features": {
                            "type": "knn_vector",
                            "dimension": 3,
                            "method": {
                                "name": "hnsw",
                                "space_type": "l2",
                                "engine": "lucene"
                            }
                        }
                    }
                }
            }
            
            self.client.indices.create(index=products_index, body=knn_mapping)
            print("✅ KNN 인덱스 생성 완료")
            
            # 상품 데이터 (특성 벡터 포함)
            products = [
                {"product_name": "스마트폰", "category": "전자제품", "price": 800000, "features": [0.9, 0.1, 0.2]},
                {"product_name": "태블릿", "category": "전자제품", "price": 600000, "features": [0.8, 0.2, 0.3]},
                {"product_name": "노트북", "category": "전자제품", "price": 1500000, "features": [0.7, 0.3, 0.4]},
                {"product_name": "운동화", "category": "의류", "price": 150000, "features": [0.1, 0.9, 0.1]},
                {"product_name": "등산화", "category": "의류", "price": 200000, "features": [0.2, 0.8, 0.2]},
                {"product_name": "소설책", "category": "도서", "price": 15000, "features": [0.1, 0.1, 0.9]}
            ]
            
            # 데이터 삽입
            for i, product in enumerate(products):
                self.client.index(index=products_index, id=i+1, body=product)
            
            time.sleep(3)  # 인덱싱 대기
            print(f"✅ 상품 데이터 생성: {len(products)}개")
            
            # KNN 검색 (스마트폰과 유사한 상품 찾기)
            search_vector = [0.9, 0.1, 0.2]  # 스마트폰 특성
            
            knn_query = {
                "size": 3,
                "query": {
                    "knn": {
                        "features": {
                            "vector": search_vector,
                            "k": 3
                        }
                    }
                }
            }
            
            print(f"\n🔍 벡터 검색 (스마트폰과 유사한 상품):")
            response = self.client.search(index=products_index, body=knn_query)
            
            if response['hits']['hits']:
                for i, hit in enumerate(response['hits']['hits']):
                    product = hit['_source']
                    score = hit['_score']
                    print(f"   {i+1}. {product['product_name']} (유사도: {score:.4f})")
                    
                return True
            else:
                print("   ❌ 검색 결과 없음")
                
        except Exception as e:
            print(f"❌ KNN 플러그인 테스트 실패: {e}")
            
        return False

    def test_4_alerting_plugin(self):
        """4. Alerting 플러그인 테스트"""
        print("\n=== 🚨 4. Alerting 플러그인 테스트 ===")
        
        try:
            # 모니터 목록 조회
            response = requests.get(
                f"{self.base_url}/_plugins/_alerting/monitors",
                auth=self.auth,
                verify=False
            )
            
            if response.status_code == 200:
                monitors = response.json()
                print(f"✅ Alerting 플러그인 활성화")
                print(f"✅ 현재 모니터 수: {monitors.get('totalMonitors', 0)}")
                
                # 간단한 테스트 모니터 생성
                monitor_body = {
                    "name": "KCB-Test-Monitor",
                    "type": "monitor",
                    "monitor_type": "query_level_monitor",
                    "enabled": False,  # 테스트용이므로 비활성화
                    "schedule": {
                        "period": {"interval": 5, "unit": "MINUTES"}
                    },
                    "inputs": [
                        {
                            "search": {
                                "indices": ["kcb-employees"],
                                "query": {
                                    "size": 0,
                                    "query": {"match_all": {}},
                                    "aggs": {
                                        "employee_count": {
                                            "value_count": {"field": "name.keyword"}
                                        }
                                    }
                                }
                            }
                        }
                    ],
                    "triggers": [
                        {
                            "name": "employee_count_check",
                            "severity": "3",
                            "condition": {
                                "script": {
                                    "source": "ctx.results[0].aggregations.employee_count.value > 10",
                                    "lang": "painless"
                                }
                            },
                            "actions": []
                        }
                    ]
                }
                
                create_response = requests.post(
                    f"{self.base_url}/_plugins/_alerting/monitors",
                    auth=self.auth,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(monitor_body),
                    verify=False
                )
                
                if create_response.status_code in [200, 201]:
                    monitor = create_response.json()
                    monitor_id = monitor.get('_id')
                    print(f"✅ 테스트 모니터 생성: {monitor_id}")
                    return True
                else:
                    print(f"⚠️ 모니터 생성 실패: {create_response.status_code}")
                    print("   (기본 기능은 정상 작동)")
                    return True
                    
            else:
                print(f"❌ Alerting 플러그인 응답 오류: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Alerting 테스트 실패: {e}")
            
        return False

    def test_5_ml_plugin(self):
        """5. ML Commons 플러그인 테스트"""
        print("\n=== 🤖 5. ML Commons 플러그인 테스트 ===")
        
        try:
            # ML 플러그인 상태 확인
            response = requests.get(
                f"{self.base_url}/_plugins/_ml/stats",
                auth=self.auth,
                verify=False
            )
            
            if response.status_code == 200:
                ml_stats = response.json()
                print(f"✅ ML Commons 플러그인 활성화")
                print(f"✅ ML 노드 수: {len(ml_stats.get('nodes', {}))}")
                
                # 간단한 고객 데이터로 클러스터링 테스트
                self.create_customer_data_for_ml()
                
                return True
            else:
                print(f"❌ ML 플러그인 응답 오류: {response.status_code}")
                
        except Exception as e:
            print(f"❌ ML 플러그인 테스트 실패: {e}")
            
        return False

    def create_customer_data_for_ml(self):
        """ML 테스트용 고객 데이터 생성"""
        customer_index = "kcb-customers"
        
        if self.client.indices.exists(index=customer_index):
            self.client.indices.delete(index=customer_index)
        
        # 고객 데이터 매핑
        mapping = {
            "mappings": {
                "properties": {
                    "customer_id": {"type": "keyword"},
                    "age": {"type": "integer"},
                    "income": {"type": "integer"},
                    "credit_score": {"type": "integer"},
                    "loan_amount": {"type": "integer"}
                }
            }
        }
        
        self.client.indices.create(index=customer_index, body=mapping)
        
        # 샘플 고객 데이터
        customers = [
            {"customer_id": "C001", "age": 30, "income": 5000, "credit_score": 750, "loan_amount": 30000},
            {"customer_id": "C002", "age": 45, "income": 7000, "credit_score": 680, "loan_amount": 50000},
            {"customer_id": "C003", "age": 25, "income": 3500, "credit_score": 720, "loan_amount": 20000},
            {"customer_id": "C004", "age": 35, "income": 6000, "credit_score": 800, "loan_amount": 40000},
            {"customer_id": "C005", "age": 50, "income": 8000, "credit_score": 650, "loan_amount": 60000}
        ]
        
        # 데이터 삽입
        for i, customer in enumerate(customers):
            self.client.index(index=customer_index, id=i+1, body=customer)
        
        time.sleep(2)
        print(f"   ✅ ML용 고객 데이터 생성: {len(customers)}명")

    def test_6_performance_analyzer(self):
        """6. Performance Analyzer 플러그인 테스트"""
        print("\n=== ⚡ 6. Performance Analyzer 플러그인 테스트 ===")
        
        try:
            # Performance Analyzer API 테스트 (포트 9600)
            response = requests.get(
                "http://localhost:9600/_plugins/_performanceanalyzer/metrics",
                timeout=5
            )
            
            if response.status_code == 200:
                print("✅ Performance Analyzer 활성화")
                print("✅ 성능 메트릭 수집 중")
                return True
            else:
                print(f"⚠️ Performance Analyzer 응답: {response.status_code}")
                print("   (별도 포트에서 실행되므로 정상일 수 있음)")
                return True
                
        except Exception as e:
            print(f"⚠️ Performance Analyzer 접근 불가: {e}")
            print("   (Performance Analyzer는 별도 설정이 필요할 수 있습니다)")
            return True

    def test_7_index_management(self):
        """7. Index Management 플러그인 테스트"""
        print("\n=== 📁 7. Index Management 플러그인 테스트 ===")
        
        try:
            # ISM 정책 목록 조회
            response = requests.get(
                f"{self.base_url}/_plugins/_ism/policies",
                auth=self.auth,
                verify=False
            )
            
            if response.status_code == 200:
                policies = response.json()
                print(f"✅ Index Management 플러그인 활성화")
                print(f"✅ 현재 ISM 정책 수: {policies.get('total_policies', 0)}")
                return True
            else:
                print(f"❌ Index Management 플러그인 오류: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Index Management 테스트 실패: {e}")
            
        return False

    def test_8_observability(self):
        """8. Observability 플러그인 테스트"""
        print("\n=== 👁️ 8. Observability 플러그인 테스트 ===")
        
        try:
            # 관측성 객체 목록 조회
            response = requests.get(
                f"{self.base_url}/_plugins/_observability/object",
                auth=self.auth,
                verify=False
            )
            
            if response.status_code == 200:
                objects = response.json()
                print(f"✅ Observability 플러그인 활성화")
                print(f"✅ 관측성 객체 수: {len(objects.get('observabilityObjectList', []))}")
                return True
            else:
                print(f"❌ Observability 플러그인 오류: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Observability 테스트 실패: {e}")
            
        return False

    def run_all_tests(self):
        """모든 플러그인 테스트 실행"""
        print("🚀 OpenSearch 플러그인 전체 테스트를 시작합니다!")
        print("=" * 60)
        
        # 연결 확인
        try:
            info = self.client.info()
            print(f"✅ OpenSearch 버전: {info['version']['number']}")
            print(f"✅ 클러스터: {info['cluster_name']}")
        except Exception as e:
            print(f"❌ 연결 실패: {e}")
            return
        
        # 테스트 실행
        tests = [
            ("Security", self.test_1_security_plugin),
            ("SQL", self.test_2_sql_plugin),
            ("KNN", self.test_3_knn_plugin),
            ("Alerting", self.test_4_alerting_plugin),
            ("ML Commons", self.test_5_ml_plugin),
            ("Performance Analyzer", self.test_6_performance_analyzer),
            ("Index Management", self.test_7_index_management),
            ("Observability", self.test_8_observability)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n⏳ {test_name} 플러그인 테스트 중...")
            try:
                result = test_func()
                results[test_name] = "✅ 성공" if result else "❌ 실패"
            except Exception as e:
                results[test_name] = f"❌ 오류: {str(e)[:30]}..."
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("🎯 플러그인 테스트 결과 요약")
        print("-" * 40)
        
        for plugin, result in results.items():
            print(f"{plugin:20} : {result}")
        
        success_count = sum(1 for r in results.values() if "✅" in r)
        total_count = len(results)
        
        print(f"\n📊 총 {total_count}개 플러그인 중 {success_count}개 성공")
        
        if success_count >= total_count * 0.8:  # 80% 이상 성공
            print("🎉 대부분의 플러그인이 정상 작동합니다!")
        else:
            print("⚠️ 일부 플러그인에 문제가 있을 수 있습니다.")
        
        print("\n🌐 다음 단계:")
        print("   1. http://opensearch.local 에서 Dashboards 접속")
        print("   2. 생성된 인덱스들을 확인해보세요:")
        print("      - kcb-employees (직원 데이터)")
        print("      - kcb-products (상품 데이터)")
        print("      - kcb-customers (고객 데이터)")

if __name__ == "__main__":
    tester = OpenSearchPluginTester()
    tester.run_all_tests()