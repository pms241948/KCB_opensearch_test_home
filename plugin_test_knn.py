#!/usr/bin/env python3
"""
OpenSearch KNN 플러그인 상세 테스트
벡터 검색 및 유사도 분석 기능 테스트
"""

import requests
import json
import time
import random
import math
from opensearchpy import OpenSearch, RequestsHttpConnection
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class KNNPluginTester:
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

    def test_connection(self):
        """연결 테스트"""
        try:
            info = self.client.info()
            print(f"✅ OpenSearch 버전: {info['version']['number']}")
            return True
        except Exception as e:
            print(f"❌ 연결 실패: {e}")
            return False

    def test_knn_index_creation(self):
        """KNN 인덱스 생성 테스트"""
        print("\n=== 📋 KNN 인덱스 생성 테스트 ===")
        
        results = {"인덱스기능": [], "테스트결과": {}}
        
        # 다양한 차원과 거리 메트릭 테스트
        test_indices = [
            {
                "name": "knn-test-small",
                "dimension": 5,
                "space_type": "l2",
                "description": "5차원 L2 거리"
            },
            {
                "name": "knn-test-medium",
                "dimension": 50,
                "space_type": "cosinesimil",
                "description": "50차원 코사인 유사도"
            },
            {
                "name": "knn-test-large",
                "dimension": 128,
                "space_type": "l1",
                "description": "128차원 L1 거리"
            }
        ]
        
        for test_config in test_indices:
            try:
                index_name = test_config["name"]
                
                # 기존 인덱스 삭제
                if self.client.indices.exists(index=index_name):
                    self.client.indices.delete(index=index_name)
                
                # KNN 인덱스 매핑 생성
                mapping = {
                    "settings": {
                        "index": {
                            "knn": True,
                            "knn.algo_param.ef_search": 100
                        }
                    },
                    "mappings": {
                        "properties": {
                            "title": {"type": "text"},
                            "category": {"type": "keyword"},
                            "vector": {
                                "type": "knn_vector",
                                "dimension": test_config["dimension"],
                                "method": {
                                    "name": "hnsw",
                                    "space_type": test_config["space_type"],
                                    "engine": "lucene",
                                    "parameters": {
                                        "ef_construction": 128,
                                        "m": 24
                                    }
                                }
                            }
                        }
                    }
                }
                
                self.client.indices.create(index=index_name, body=mapping)
                
                print(f"   ✅ {test_config['description']} 인덱스 생성 성공")
                results["인덱스기능"].append(f"{test_config['dimension']}차원 {test_config['space_type']} 거리")
                results["테스트결과"][test_config["name"]] = "성공"
                
                # 인덱스 설정 확인
                index_info = self.client.indices.get(index=index_name)
                knn_enabled = index_info[index_name]['settings']['index'].get('knn', 'false')
                print(f"      KNN 활성화: {knn_enabled}")
                
            except Exception as e:
                print(f"   ❌ {test_config['description']} 인덱스 생성 실패: {e}")
                results["테스트결과"][test_config["name"]] = f"실패: {e}"
        
        return results

    def create_vector_test_data(self):
        """벡터 테스트 데이터 생성"""
        print("\n📊 벡터 테스트 데이터 생성")
        
        # 문서 유사도 검색용 데이터
        doc_index = "knn-documents"
        
        if self.client.indices.exists(index=doc_index):
            self.client.indices.delete(index=doc_index)
        
        # 문서 인덱스 매핑
        doc_mapping = {
            "settings": {"index": {"knn": True}},
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "category": {"type": "keyword"},
                    "author": {"type": "keyword"},
                    "publish_date": {"type": "date"},
                    "content_vector": {
                        "type": "knn_vector",
                        "dimension": 10,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "lucene"
                        }
                    }
                }
            }
        }
        
        self.client.indices.create(index=doc_index, body=doc_mapping)
        
        # 문서 데이터 (카테고리별로 유사한 벡터)
        documents = [
            # 기술 문서들 (비슷한 벡터)
            {"title": "Python 프로그래밍 기초", "content": "파이썬 기본 문법과 데이터 타입", "category": "기술", "author": "김개발", "publish_date": "2024-01-15", 
             "content_vector": [0.9, 0.8, 0.1, 0.2, 0.1, 0.0, 0.1, 0.0, 0.2, 0.1]},
            {"title": "Java 객체지향 프로그래밍", "content": "자바의 클래스와 객체 개념", "category": "기술", "author": "이코딩", "publish_date": "2024-01-20",
             "content_vector": [0.8, 0.9, 0.2, 0.1, 0.2, 0.0, 0.0, 0.1, 0.1, 0.2]},
            {"title": "웹 개발 프레임워크", "content": "React와 Vue.js 비교", "category": "기술", "author": "박웹", "publish_date": "2024-02-01",
             "content_vector": [0.7, 0.8, 0.3, 0.2, 0.1, 0.1, 0.0, 0.0, 0.3, 0.1]},
            
            # 비즈니스 문서들
            {"title": "마케팅 전략 수립", "content": "디지털 마케팅 트렌드 분석", "category": "비즈니스", "author": "최마케팅", "publish_date": "2024-01-25",
             "content_vector": [0.1, 0.2, 0.8, 0.9, 0.1, 0.0, 0.2, 0.0, 0.1, 0.0]},
            {"title": "재무 관리 기법", "content": "현금 흐름과 투자 분석", "category": "비즈니스", "author": "정재무", "publish_date": "2024-02-10",
             "content_vector": [0.2, 0.1, 0.9, 0.8, 0.0, 0.1, 0.1, 0.0, 0.0, 0.2]},
            {"title": "인사 관리 시스템", "content": "성과 평가와 보상 체계", "category": "비즈니스", "author": "한인사", "publish_date": "2024-02-15",
             "content_vector": [0.0, 0.1, 0.7, 0.8, 0.2, 0.1, 0.3, 0.0, 0.1, 0.1]},
            
            # 연구 논문들
            {"title": "AI 알고리즘 연구", "content": "머신러닝과 딥러닝 비교", "category": "연구", "author": "김연구", "publish_date": "2024-01-30",
             "content_vector": [0.1, 0.0, 0.2, 0.1, 0.8, 0.9, 0.1, 0.0, 0.2, 0.3]},
            {"title": "데이터 과학 방법론", "content": "빅데이터 분석 기법", "category": "연구", "author": "이데이터", "publish_date": "2024-02-05",
             "content_vector": [0.0, 0.1, 0.1, 0.2, 0.9, 0.8, 0.0, 0.1, 0.3, 0.2]},
            {"title": "통계학 응용", "content": "확률과 통계 모델링", "category": "연구", "author": "박통계", "publish_date": "2024-02-20",
             "content_vector": [0.1, 0.0, 0.0, 0.1, 0.7, 0.8, 0.2, 0.1, 0.4, 0.3]},
            
            # 기타 문서들
            {"title": "요리 레시피 모음", "content": "한식과 양식 요리법", "category": "생활", "author": "조요리", "publish_date": "2024-01-10",
             "content_vector": [0.0, 0.1, 0.0, 0.0, 0.1, 0.2, 0.8, 0.9, 0.1, 0.0]},
            {"title": "여행 가이드", "content": "국내외 여행지 추천", "category": "생활", "author": "강여행", "publish_date": "2024-02-25",
             "content_vector": [0.1, 0.0, 0.1, 0.0, 0.0, 0.1, 0.9, 0.8, 0.0, 0.2]}
        ]
        
        # 데이터 삽입
        for i, doc in enumerate(documents):
            self.client.index(index=doc_index, id=i+1, body=doc)
        
        time.sleep(3)  # 인덱싱 대기
        print(f"   ✅ 문서 데이터 생성: {len(documents)}개")
        
        return doc_index

    def test_basic_knn_search(self, index_name):
        """기본 KNN 검색 테스트"""
        print("\n=== 🔍 기본 KNN 검색 테스트 ===")
        
        results = {"검색기능": [], "테스트결과": {}}
        
        # 1. 기본 KNN 검색
        print("\n📋 1. 기본 벡터 유사도 검색")
        
        # 기술 문서와 유사한 벡터로 검색
        tech_query_vector = [0.8, 0.9, 0.1, 0.1, 0.1, 0.0, 0.0, 0.0, 0.2, 0.1]
        
        basic_knn_query = {
            "size": 5,
            "query": {
                "knn": {
                    "content_vector": {
                        "vector": tech_query_vector,
                        "k": 5
                    }
                }
            }
        }
        
        try:
            response = self.client.search(index=index_name, body=basic_knn_query)
            
            if response['hits']['hits']:
                print("   ✅ 기본 KNN 검색 성공")
                print("   📊 검색 결과 (기술 문서 유사도):")
                
                for i, hit in enumerate(response['hits']['hits']):
                    doc = hit['_source']
                    score = hit['_score']
                    print(f"      {i+1}. {doc['title']} ({doc['category']})")
                    print(f"         유사도: {score:.4f}, 저자: {doc['author']}")
                
                results["검색기능"].append("K-최근접 이웃 벡터 검색")
                results["테스트결과"]["기본KNN검색"] = "성공"
            else:
                print("   ❌ 기본 KNN 검색 결과 없음")
                results["테스트결과"]["기본KNN검색"] = "결과없음"
                
        except Exception as e:
            print(f"   ❌ 기본 KNN 검색 오류: {e}")
            results["테스트결과"]["기본KNN검색"] = f"오류: {e}"
        
        # 2. 다른 카테고리로 검색
        print("\n📋 2. 비즈니스 문서 유사도 검색")
        
        business_query_vector = [0.1, 0.1, 0.9, 0.8, 0.0, 0.0, 0.1, 0.0, 0.0, 0.1]
        
        business_knn_query = {
            "size": 3,
            "query": {
                "knn": {
                    "content_vector": {
                        "vector": business_query_vector,
                        "k": 3
                    }
                }
            }
        }
        
        try:
            business_response = self.client.search(index=index_name, body=business_knn_query)
            
            if business_response['hits']['hits']:
                print("   ✅ 비즈니스 카테고리 KNN 검색 성공")
                print("   📊 검색 결과:")
                
                for i, hit in enumerate(business_response['hits']['hits']):
                    doc = hit['_source']
                    score = hit['_score']
                    print(f"      {i+1}. {doc['title']} ({doc['category']})")
                    print(f"         유사도: {score:.4f}")
                
                results["검색기능"].append("카테고리별 유사도 검색")
                results["테스트결과"]["카테고리KNN검색"] = "성공"
                
        except Exception as e:
            print(f"   ❌ 비즈니스 KNN 검색 오류: {e}")
            results["테스트결과"]["카테고리KNN검색"] = f"오류: {e}"
        
        return results

    def test_filtered_knn_search(self, index_name):
        """필터링된 KNN 검색 테스트"""
        print("\n=== 🔥 필터링된 KNN 검색 테스트 ===")
        
        results = {"필터기능": [], "테스트결과": {}}
        
        # 1. 카테고리 필터 + KNN
        print("\n📋 1. 카테고리 필터 + 벡터 검색")
        
        query_vector = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        
        filtered_query = {
            "size": 5,
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "content_vector": {
                                    "vector": query_vector,
                                    "k": 10
                                }
                            }
                        }
                    ],
                    "filter": [
                        {"term": {"category": "기술"}}
                    ]
                }
            }
        }
        
        try:
            filtered_response = self.client.search(index=index_name, body=filtered_query)
            
            if filtered_response['hits']['hits']:
                print("   ✅ 카테고리 필터링된 KNN 검색 성공")
                print("   📊 '기술' 카테고리 내에서만 검색:")
                
                for hit in filtered_response['hits']['hits']:
                    doc = hit['_source']
                    score = hit['_score']
                    print(f"      - {doc['title']} (유사도: {score:.4f})")
                
                results["필터기능"].append("카테고리 필터 + KNN")
                results["테스트결과"]["카테고리필터KNN"] = "성공"
                
        except Exception as e:
            print(f"   ❌ 카테고리 필터 KNN 오류: {e}")
            results["테스트결과"]["카테고리필터KNN"] = f"오류: {e}"
        
        # 2. 날짜 범위 필터 + KNN
        print("\n📋 2. 날짜 범위 필터 + 벡터 검색")
        
        date_filtered_query = {
            "size": 5,
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "content_vector": {
                                    "vector": query_vector,
                                    "k": 10
                                }
                            }
                        }
                    ],
                    "filter": [
                        {
                            "range": {
                                "publish_date": {
                                    "gte": "2024-02-01",
                                    "lte": "2024-02-28"
                                }
                            }
                        }
                    ]
                }
            }
        }
        
        try:
            date_response = self.client.search(index=index_name, body=date_filtered_query)
            
            if date_response['hits']['hits']:
                print("   ✅ 날짜 범위 필터링된 KNN 검색 성공")
                print("   📊 2024년 2월 문서만 검색:")
                
                for hit in date_response['hits']['hits']:
                    doc = hit['_source']
                    score = hit['_score']
                    publish_date = doc['publish_date']
                    print(f"      - {doc['title']} ({publish_date})")
                    print(f"        유사도: {score:.4f}")
                
                results["필터기능"].append("날짜 범위 필터 + KNN")
                results["테스트결과"]["날짜필터KNN"] = "성공"
                
        except Exception as e:
            print(f"   ❌ 날짜 필터 KNN 오류: {e}")
            results["테스트결과"]["날짜필터KNN"] = f"오류: {e}"
        
        # 3. 복합 필터 + KNN
        print("\n📋 3. 복합 조건 필터 + 벡터 검색")
        
        complex_filtered_query = {
            "size": 3,
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "content_vector": {
                                    "vector": query_vector,
                                    "k": 10
                                }
                            }
                        }
                    ],
                    "filter": [
                        {"terms": {"category": ["기술", "연구"]}},
                        {"range": {"publish_date": {"gte": "2024-01-15"}}}
                    ]
                }
            }
        }
        
        try:
            complex_response = self.client.search(index=index_name, body=complex_filtered_query)
            
            if complex_response['hits']['hits']:
                print("   ✅ 복합 필터링된 KNN 검색 성공")
                print("   📊 기술/연구 카테고리 + 1월15일 이후:")
                
                for hit in complex_response['hits']['hits']:
                    doc = hit['_source']
                    score = hit['_score']
                    print(f"      - {doc['title']} ({doc['category']})")
                    print(f"        유사도: {score:.4f}")
                
                results["필터기능"].append("복합 조건 필터 + KNN")
                results["테스트결과"]["복합필터KNN"] = "성공"
                
        except Exception as e:
            print(f"   ❌ 복합 필터 KNN 오류: {e}")
            results["테스트결과"]["복합필터KNN"] = f"오류: {e}"
        
        return results

    def test_distance_metrics(self):
        """거리 메트릭별 성능 테스트"""
        print("\n=== 📐 거리 메트릭별 테스트 ===")
        
        results = {"거리메트릭": [], "테스트결과": {}}
        
        distance_types = [
            {"type": "l2", "name": "유클리드 거리 (L2)"},
            {"type": "cosinesimil", "name": "코사인 유사도"},
            {"type": "l1", "name": "맨해튼 거리 (L1)"}
        ]
        
        for dist_config in distance_types:
            try:
                index_name = f"knn-test-{dist_config['type']}"
                
                # 거리별 테스트 인덱스 생성
                if self.client.indices.exists(index=index_name):
                    self.client.indices.delete(index=index_name)
                
                mapping = {
                    "settings": {"index": {"knn": True}},
                    "mappings": {
                        "properties": {
                            "name": {"type": "keyword"},
                            "vector": {
                                "type": "knn_vector",
                                "dimension": 5,
                                "method": {
                                    "name": "hnsw",
                                    "space_type": dist_config["type"],
                                    "engine": "lucene"
                                }
                            }
                        }
                    }
                }
                
                self.client.indices.create(index=index_name, body=mapping)
                
                # 테스트 벡터 데이터 삽입
                test_vectors = [
                    {"name": "벡터1", "vector": [1.0, 0.0, 0.0, 0.0, 0.0]},
                    {"name": "벡터2", "vector": [0.8, 0.2, 0.0, 0.0, 0.0]},
                    {"name": "벡터3", "vector": [0.0, 1.0, 0.0, 0.0, 0.0]},
                    {"name": "벡터4", "vector": [0.0, 0.0, 1.0, 0.0, 0.0]},
                    {"name": "벡터5", "vector": [0.0, 0.0, 0.0, 1.0, 0.0]}
                ]
                
                for i, vec_data in enumerate(test_vectors):
                    self.client.index(index=index_name, id=i+1, body=vec_data)
                
                time.sleep(2)
                
                # 검색 테스트
                search_vector = [1.0, 0.0, 0.0, 0.0, 0.0]
                
                start_time = time.time()
                
                search_query = {
                    "size": 3,
                    "query": {
                        "knn": {
                            "vector": {
                                "vector": search_vector,
                                "k": 3
                            }
                        }
                    }
                }
                
                search_response = self.client.search(index=index_name, body=search_query)
                search_time = (time.time() - start_time) * 1000  # milliseconds
                
                if search_response['hits']['hits']:
                    print(f"\n   ✅ {dist_config['name']} 테스트 성공")
                    print(f"      검색 시간: {search_time:.2f}ms")
                    print("      검색 결과:")
                    
                    for hit in search_response['hits']['hits']:
                        doc = hit['_source']
                        score = hit['_score']
                        print(f"        - {doc['name']}: 점수 {score:.4f}")
                    
                    results["거리메트릭"].append(dist_config['name'])
                    results["테스트결과"][dist_config['type']] = f"성공 ({search_time:.2f}ms)"
                else:
                    print(f"   ❌ {dist_config['name']} 검색 결과 없음")
                    results["테스트결과"][dist_config['type']] = "결과없음"
                
            except Exception as e:
                print(f"   ❌ {dist_config['name']} 테스트 오류: {e}")
                results["테스트결과"][dist_config['type']] = f"오류: {e}"
        
        return results

    def test_high_dimensional_vectors(self):
        """고차원 벡터 성능 테스트"""
        print("\n=== ⚡ 고차원 벡터 성능 테스트 ===")
        
        results = {"고차원기능": [], "테스트결과": {}}
        
        dimension_tests = [
            {"dim": 50, "name": "50차원"},
            {"dim": 128, "name": "128차원"},
            {"dim": 256, "name": "256차원"}
        ]
        
        for dim_config in dimension_tests:
            try:
                index_name = f"knn-high-dim-{dim_config['dim']}"
                dimension = dim_config['dim']
                
                if self.client.indices.exists(index=index_name):
                    self.client.indices.delete(index=index_name)
                
                # 고차원 벡터 인덱스
                mapping = {
                    "settings": {
                        "index": {
                            "knn": True,
                            "knn.algo_param.ef_search": 100
                        }
                    },
                    "mappings": {
                        "properties": {
                            "id": {"type": "keyword"},
                            "high_dim_vector": {
                                "type": "knn_vector",
                                "dimension": dimension,
                                "method": {
                                    "name": "hnsw",
                                    "space_type": "cosinesimil",
                                    "engine": "lucene",
                                    "parameters": {
                                        "ef_construction": 256,
                                        "m": 48
                                    }
                                }
                            }
                        }
                    }
                }
                
                self.client.indices.create(index=index_name, body=mapping)
                
                # 고차원 테스트 데이터 생성
                print(f"\n   📊 {dim_config['name']} 벡터 데이터 생성 중...")
                
                test_docs = []
                for i in range(20):  # 20개 문서
                    vector = [random.random() for _ in range(dimension)]
                    # 벡터 정규화 (코사인 유사도를 위해)
                    magnitude = math.sqrt(sum(x*x for x in vector))
                    if magnitude > 0:
                        vector = [x/magnitude for x in vector]
                    
                    doc = {
                        "id": f"doc_{i:03d}",
                        "high_dim_vector": vector
                    }
                    test_docs.append(doc)
                
                # 배치 삽입
                for i, doc in enumerate(test_docs):
                    self.client.index(index=index_name, id=i+1, body=doc)
                
                time.sleep(3)  # 인덱싱 대기
                
                # 검색 성능 테스트
                query_vector = [random.random() for _ in range(dimension)]
                magnitude = math.sqrt(sum(x*x for x in query_vector))
                if magnitude > 0:
                    query_vector = [x/magnitude for x in query_vector]
                
                start_time = time.time()
                
                search_query = {
                    "size": 5,
                    "query": {
                        "knn": {
                            "high_dim_vector": {
                                "vector": query_vector,
                                "k": 5
                            }
                        }
                    }
                }
                
                search_response = self.client.search(index=index_name, body=search_query)
                search_time = (time.time() - start_time) * 1000
                
                if search_response['hits']['hits']:
                    print(f"   ✅ {dim_config['name']} 벡터 검색 성공")
                    print(f"      검색 시간: {search_time:.2f}ms")
                    print(f"      검색된 문서: {len(search_response['hits']['hits'])}개")
                    
                    # 상위 결과 표시
                    top_hit = search_response['hits']['hits'][0]
                    print(f"      최고 유사도: {top_hit['_score']:.4f} ({top_hit['_source']['id']})")
                    
                    results["고차원기능"].append(f"{dim_config['name']} 벡터 검색")
                    results["테스트결과"][dim_config['name']] = f"성공 ({search_time:.2f}ms)"
                else:
                    print(f"   ❌ {dim_config['name']} 검색 결과 없음")
                    results["테스트결과"][dim_config['name']] = "결과없음"
                
            except Exception as e:
                print(f"   ❌ {dim_config['name']} 테스트 오류: {e}")
                results["테스트결과"][dim_config['name']] = f"오류: {e}"
        
        return results

    def run_knn_plugin_test(self):
        """KNN 플러그인 전체 테스트 실행"""
        print("🎯 OpenSearch KNN 플러그인 상세 테스트")
        print("=" * 60)
        
        if not self.test_connection():
            return
        
        all_results = {}
        
        # 1. KNN 인덱스 생성 테스트
        index_results = self.test_knn_index_creation()
        all_results.update(index_results)
        
        # 2. 벡터 테스트 데이터 생성
        doc_index = self.create_vector_test_data()
        
        # 3. 기본 KNN 검색 테스트
        search_results = self.test_basic_knn_search(doc_index)
        all_results.update(search_results)
        
        # 4. 필터링된 KNN 검색 테스트
        filter_results = self.test_filtered_knn_search(doc_index)
        all_results.update(filter_results)
        
        # 5. 거리 메트릭 테스트
        distance_results = self.test_distance_metrics()
        all_results.update(distance_results)
        
        # 6. 고차원 벡터 테스트
        high_dim_results = self.test_high_dimensional_vectors()
        all_results.update(high_dim_results)
        
        # 결과 요약
        self.print_knn_summary(all_results)

    def print_knn_summary(self, results):
        """KNN 플러그인 테스트 결과 요약"""
        print("\n" + "="*70)
        print("📊 KNN 플러그인 테스트 결과 요약")
        print("="*70)
        
        # 모든 기능 수집
        all_features = []
        for key in ["인덱스기능", "검색기능", "필터기능", "거리메트릭", "고차원기능"]:
            if key in results:
                all_features.extend(results[key])
        
        print(f"\n🔧 지원 기능 ({len(all_features)}개):")
        for i, feature in enumerate(all_features, 1):
            print(f"   {i:2d}. {feature}")
        
        # 테스트 결과 통계
        test_results = results.get("테스트결과", {})
        print(f"\n🧪 테스트 결과:")
        
        success_count = 0
        total_count = 0
        
        for test_name, result in test_results.items():
            total_count += 1
            if "성공" in str(result):
                success_count += 1
                print(f"   ✅ {test_name}: {result}")
            elif "실패" in str(result) or "오류" in str(result):
                print(f"   ❌ {test_name}: {result}")
            else:
                print(f"   ⚠️ {test_name}: {result}")
        
        if total_count > 0:
            success_rate = (success_count / total_count) * 100
            print(f"\n📈 성공률: {success_rate:.1f}% ({success_count}/{total_count})")
        
        # 활용 방안
        print(f"\n💡 KNN 플러그인 활용 방안:")
        use_cases = [
            "문서 유사도 검색 (텍스트 임베딩 기반)",
            "상품 추천 시스템 (고객/상품 특성 벡터)",
            "이미지 검색 (이미지 특성 벡터)",
            "고객 세분화 (고객 행동 패턴 벡터)",
            "이상 탐지 (정상 패턴과의 거리 측정)",
            "의미론적 검색 (자연어 의미 유사성)",
            "추천 엔진 구축 (협업 필터링)",
            "클러스터링 및 분류 작업",
            "얼굴 인식 및 생체 인증",
            "음성 인식 및 오디오 검색"
        ]
        
        for i, use_case in enumerate(use_cases, 1):
            print(f"   {i:2d}. {use_case}")
        
        print(f"\n🌐 다음 단계:")
        print("   1. 실제 텍스트 임베딩 모델과 연동")
        print("   2. 대용량 벡터 데이터 성능 최적화")
        print("   3. 하이브리드 검색 (키워드 + 벡터) 구현")
        print("   4. 실시간 추천 시스템 구축")
        
        print(f"\n💻 생성된 테스트 인덱스:")
        indices = [
            "knn-test-small: 5차원 L2 거리",
            "knn-test-medium: 50차원 코사인 유사도", 
            "knn-test-large: 128차원 L1 거리",
            "knn-documents: 문서 유사도 검색용 (11개 문서)"
        ]
        for idx in indices:
            print(f"   • {idx}")

if __name__ == "__main__":
    tester = KNNPluginTester()
    tester.run_knn_plugin_test()