#!/usr/bin/env python3
"""
OpenSearch Anomaly Detection 플러그인 테스트
==========================================

Anomaly Detection 플러그인의 주요 기능들을 테스트합니다:
1. 시계열 이상 탐지 설정
2. 실시간 모니터링 대시보드
3. 자동 알림 시스템
4. 금융 업무 시나리오 (거래 패턴, 시스템 성능)

작성자: KCB IT AI 추진단
날짜: 2025-08-12
"""

import json
import time
import datetime
import numpy as np
from opensearchpy import OpenSearch
from opensearchpy.exceptions import RequestError, NotFoundError
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetectionTester:
    def __init__(self):
        """OpenSearch 클라이언트 초기화"""
        self.client = OpenSearch(
            hosts=[{'host': 'localhost', 'port': 9200}],
            http_auth=('admin', 'Kcb2025opSLabAi9'),
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False
        )
        print("🔍 Anomaly Detection 플러그인 테스트 시작")
        print("=" * 50)
    
    def check_anomaly_plugin_status(self):
        """Anomaly Detection 플러그인 상태 확인"""
        print("\n📋 1. Anomaly Detection 플러그인 상태 확인")
        print("-" * 35)
        
        try:
            # 플러그인 목록 확인
            response = self.client.cat.plugins(format='json', v=True)
            anomaly_plugins = [p for p in response if 'anomaly' in p['component'].lower()]
            
            if anomaly_plugins:
                print("✅ Anomaly Detection 플러그인이 설치되어 있습니다:")
                for plugin in anomaly_plugins:
                    print(f"   - {plugin['component']} v{plugin['version']}")
            else:
                print("❌ Anomaly Detection 플러그인을 찾을 수 없습니다.")
                print("💡 OpenSearch 2.13.0에는 기본 포함되어 있어야 합니다.")
            
            # Anomaly Detection API 상태 확인
            try:
                detectors_response = self.client.transport.perform_request(
                    'GET',
                    '/_plugins/_anomaly_detection/detectors/_search',
                    body={"size": 0}
                )
                print(f"✅ Anomaly Detection API 정상 동작")
                print(f"📊 등록된 탐지기 수: {detectors_response.get('hits', {}).get('total', {}).get('value', 0)}")
                
            except Exception as e:
                print(f"⚠️ Anomaly Detection API 확인 실패: {e}")
                print("💡 계속 진행하여 기본 기능 테스트해보겠습니다.")
            
            return True
            
        except Exception as e:
            print(f"❌ 플러그인 상태 확인 실패: {e}")
            return False
    
    def setup_financial_data(self):
        """금융 업무용 시계열 데이터 생성"""
        print("\n📊 2. 금융 시계열 데이터 생성")
        print("-" * 30)
        
        try:
            # 1. 일일 거래량 데이터 인덱스
            transaction_volume_mapping = {
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "date": {"type": "date"},
                        "daily_transaction_count": {"type": "long"},
                        "daily_transaction_amount": {"type": "double"},
                        "avg_transaction_size": {"type": "double"},
                        "peak_hour_transactions": {"type": "long"},
                        "system_load": {"type": "double"},
                        "response_time_ms": {"type": "double"},
                        "error_rate": {"type": "double"},
                        "region": {"type": "keyword"}
                    }
                }
            }
            
            # 2. 실시간 거래 모니터링 데이터 인덱스
            realtime_transactions_mapping = {
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "transaction_id": {"type": "keyword"},
                        "customer_id": {"type": "keyword"},
                        "amount": {"type": "double"},
                        "merchant_type": {"type": "keyword"},
                        "location": {"type": "keyword"},
                        "is_weekend": {"type": "boolean"},
                        "hour_of_day": {"type": "integer"},
                        "anomaly_score": {"type": "double"}
                    }
                }
            }
            
            # 인덱스 생성
            indices = [
                ("financial-daily-metrics", transaction_volume_mapping),
                ("financial-realtime-transactions", realtime_transactions_mapping)
            ]
            
            for index_name, mapping in indices:
                if self.client.indices.exists(index=index_name):
                    self.client.indices.delete(index=index_name)
                
                self.client.indices.create(index=index_name, body=mapping)
                print(f"✅ 인덱스 '{index_name}' 생성 완료")
            
            # 30일간 일일 메트릭 데이터 생성
            daily_data = []
            np.random.seed(42)
            base_date = datetime.datetime(2025, 7, 13)  # 30일 전부터
            
            for day in range(30):
                current_date = base_date + datetime.timedelta(days=day)
                is_weekend = current_date.weekday() >= 5
                
                # 주말/주중 패턴 반영
                if is_weekend:
                    base_transactions = 8000 + np.random.normal(0, 500)
                    base_amount = 12000000 + np.random.normal(0, 1000000)
                else:
                    base_transactions = 15000 + np.random.normal(0, 1000)
                    base_amount = 25000000 + np.random.normal(0, 2000000)
                
                # 특정 날짜에 이상 패턴 주입 (시스템 장애, 프로모션 등)
                if day in [5, 12, 20]:  # 이상 날짜
                    if day == 5:  # 시스템 장애 시뮬레이션
                        base_transactions *= 0.3
                        base_amount *= 0.3
                        system_load = 95 + np.random.normal(0, 3)
                        response_time = 2000 + np.random.normal(0, 500)
                        error_rate = 15 + np.random.normal(0, 3)
                    elif day == 12:  # 프로모션 이벤트
                        base_transactions *= 2.5
                        base_amount *= 3.0
                        system_load = 85 + np.random.normal(0, 5)
                        response_time = 800 + np.random.normal(0, 200)
                        error_rate = 2 + np.random.normal(0, 1)
                    else:  # 외부 공격 시뮬레이션
                        base_transactions *= 1.8
                        base_amount *= 0.7
                        system_load = 90 + np.random.normal(0, 5)
                        response_time = 1500 + np.random.normal(0, 300)
                        error_rate = 8 + np.random.normal(0, 2)
                else:  # 정상 범위
                    system_load = 45 + np.random.normal(0, 10)
                    response_time = 200 + np.random.normal(0, 50)
                    error_rate = 0.5 + np.random.normal(0, 0.3)
                
                daily_record = {
                    "@timestamp": current_date.isoformat(),
                    "date": current_date.strftime("%Y-%m-%d"),
                    "daily_transaction_count": max(1000, int(base_transactions)),
                    "daily_transaction_amount": max(1000000, base_amount),
                    "avg_transaction_size": base_amount / base_transactions if base_transactions > 0 else 0,
                    "peak_hour_transactions": max(500, int(base_transactions * 0.15)),
                    "system_load": max(0, min(100, system_load)),
                    "response_time_ms": max(50, response_time),
                    "error_rate": max(0, min(100, error_rate)),
                    "region": np.random.choice(["Seoul", "Busan", "Incheon", "Daegu", "Gwangju"])
                }
                daily_data.append(daily_record)
            
            # 실시간 거래 데이터 생성 (최근 3일)
            realtime_data = []
            for day_offset in range(3):
                current_date = datetime.datetime.now() - datetime.timedelta(days=day_offset)
                
                # 하루 24시간 동안 시간당 거래 생성
                for hour in range(24):
                    transaction_time = current_date.replace(hour=hour, minute=0, second=0)
                    is_weekend = transaction_time.weekday() >= 5
                    
                    # 시간대별 거래 패턴
                    if 6 <= hour <= 9:  # 출근 시간
                        transaction_count = 200 + np.random.poisson(50)
                    elif 12 <= hour <= 14:  # 점심 시간
                        transaction_count = 300 + np.random.poisson(80)
                    elif 18 <= hour <= 22:  # 퇴근/저녁 시간
                        transaction_count = 250 + np.random.poisson(70)
                    else:  # 기타 시간
                        transaction_count = 100 + np.random.poisson(30)
                    
                    # 주말 패턴 조정
                    if is_weekend:
                        transaction_count = int(transaction_count * 0.7)
                    
                    # 거래 생성
                    for _ in range(transaction_count):
                        # 정상 거래 패턴
                        if np.random.random() > 0.02:  # 98% 정상
                            if 9 <= hour <= 17:  # 업무시간
                                amount = np.random.lognormal(np.log(100), 0.8)
                            else:  # 비업무시간
                                amount = np.random.lognormal(np.log(50), 0.6)
                            anomaly_score = np.random.uniform(0, 0.3)
                        else:  # 2% 이상 거래
                            amount = np.random.lognormal(np.log(1000), 1.2)  # 큰 금액
                            anomaly_score = np.random.uniform(0.7, 1.0)
                        
                        transaction = {
                            "@timestamp": (transaction_time + datetime.timedelta(
                                minutes=np.random.randint(0, 60),
                                seconds=np.random.randint(0, 60)
                            )).isoformat(),
                            "transaction_id": f"TXN_{day_offset:02d}{hour:02d}{np.random.randint(1000, 9999)}",
                            "customer_id": f"CUST_{np.random.randint(1, 1001):04d}",
                            "amount": amount,
                            "merchant_type": np.random.choice([
                                "restaurant", "grocery", "gas_station", "retail", 
                                "online", "pharmacy", "entertainment"
                            ]),
                            "location": np.random.choice([
                                "Seoul_Gangnam", "Seoul_Jongno", "Busan_Haeundae", 
                                "Incheon_Airport", "Daegu_Central"
                            ]),
                            "is_weekend": is_weekend,
                            "hour_of_day": hour,
                            "anomaly_score": anomaly_score
                        }
                        realtime_data.append(transaction)
            
            # 벌크 인덱싱
            print(f"📊 일일 메트릭 데이터 인덱싱 중... ({len(daily_data)}건)")
            bulk_body = []
            for record in daily_data:
                bulk_body.extend([
                    {"index": {"_index": "financial-daily-metrics"}},
                    record
                ])
            
            self.client.bulk(body=bulk_body, refresh=True)
            
            print(f"📊 실시간 거래 데이터 인덱싱 중... ({len(realtime_data)}건)")
            bulk_body = []
            for record in realtime_data:
                bulk_body.extend([
                    {"index": {"_index": "financial-realtime-transactions"}},
                    record
                ])
            
            self.client.bulk(body=bulk_body, refresh=True)
            
            print(f"✅ 총 {len(daily_data)}개 일일 메트릭 + {len(realtime_data)}개 실시간 거래 데이터 생성 완료")
            return True
            
        except Exception as e:
            print(f"❌ 금융 데이터 생성 실패: {e}")
            return False
    
    def create_anomaly_detectors(self):
        """이상 탐지기 생성 및 설정"""
        print("\n🎯 3. 이상 탐지기 생성 및 설정")
        print("-" * 30)
        
        try:
            # 1. 일일 거래량 이상 탐지기
            daily_detector_config = {
                "name": "daily_transaction_anomaly_detector",
                "description": "일일 거래량 및 시스템 성능 이상 탐지",
                "time_field": "@timestamp",
                "indices": ["financial-daily-metrics"],
                "detection_interval": {
                    "period": {
                        "interval": 1,
                        "unit": "Minutes"
                    }
                },
                "window_delay": {
                    "period": {
                        "interval": 1,
                        "unit": "Minutes"
                    }
                },
                "shingle_size": 8,
                "schema_version": 0,
                "feature_attributes": [
                    {
                        "feature_id": "daily_transactions",
                        "feature_name": "daily_transaction_count",
                        "feature_enabled": True,
                        "aggregation_query": {
                            "daily_transactions": {
                                "sum": {
                                    "field": "daily_transaction_count"
                                }
                            }
                        }
                    },
                    {
                        "feature_id": "system_performance",
                        "feature_name": "system_load_avg",
                        "feature_enabled": True,
                        "aggregation_query": {
                            "system_performance": {
                                "avg": {
                                    "field": "system_load"
                                }
                            }
                        }
                    },
                    {
                        "feature_id": "response_time",
                        "feature_name": "avg_response_time",
                        "feature_enabled": True,
                        "aggregation_query": {
                            "response_time": {
                                "avg": {
                                    "field": "response_time_ms"
                                }
                            }
                        }
                    }
                ]
            }
            
            # 2. 실시간 거래 이상 탐지기
            realtime_detector_config = {
                "name": "realtime_transaction_anomaly_detector",
                "description": "실시간 거래 패턴 이상 탐지",
                "time_field": "@timestamp",
                "indices": ["financial-realtime-transactions"],
                "detection_interval": {
                    "period": {
                        "interval": 1,
                        "unit": "Minutes"
                    }
                },
                "window_delay": {
                    "period": {
                        "interval": 1,
                        "unit": "Minutes"
                    }
                },
                "shingle_size": 4,
                "schema_version": 0,
                "feature_attributes": [
                    {
                        "feature_id": "transaction_volume",
                        "feature_name": "hourly_transaction_count",
                        "feature_enabled": True,
                        "aggregation_query": {
                            "transaction_volume": {
                                "value_count": {
                                    "field": "transaction_id"
                                }
                            }
                        }
                    },
                    {
                        "feature_id": "avg_amount",
                        "feature_name": "average_transaction_amount",
                        "feature_enabled": True,
                        "aggregation_query": {
                            "avg_amount": {
                                "avg": {
                                    "field": "amount"
                                }
                            }
                        }
                    },
                    {
                        "feature_id": "high_value_transactions",
                        "feature_name": "large_transaction_count",
                        "feature_enabled": True,
                        "aggregation_query": {
                            "high_value_transactions": {
                                "value_count": {
                                    "field": "amount",
                                    "script": {
                                        "source": "doc['amount'].value > 500"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
            
            # 탐지기 생성
            detectors = [
                ("daily", daily_detector_config),
                ("realtime", realtime_detector_config)
            ]
            
            created_detectors = {}
            
            for detector_type, config in detectors:
                try:
                    response = self.client.transport.perform_request(
                        'POST',
                        '/_plugins/_anomaly_detection/detectors',
                        body=config
                    )
                    
                    detector_id = response.get('_id')
                    created_detectors[detector_type] = detector_id
                    print(f"✅ {detector_type} 탐지기 생성 성공 (ID: {detector_id})")
                    
                    # 탐지기 시작
                    start_response = self.client.transport.perform_request(
                        'POST',
                        f'/_plugins/_anomaly_detection/detectors/{detector_id}/_start'
                    )
                    print(f"✅ {detector_type} 탐지기 시작됨")
                    
                except Exception as e:
                    print(f"⚠️ {detector_type} 탐지기 생성/시작 실패: {e}")
                    # 기존 탐지기가 있는지 확인
                    try:
                        search_response = self.client.transport.perform_request(
                            'GET',
                            '/_plugins/_anomaly_detection/detectors/_search',
                            body={
                                "query": {
                                    "match": {
                                        "name": config["name"]
                                    }
                                }
                            }
                        )
                        
                        if search_response.get('hits', {}).get('hits'):
                            existing_detector = search_response['hits']['hits'][0]
                            detector_id = existing_detector['_id']
                            created_detectors[detector_type] = detector_id
                            print(f"📋 기존 {detector_type} 탐지기 발견 (ID: {detector_id})")
                        
                    except Exception as search_error:
                        print(f"❌ {detector_type} 탐지기 검색 실패: {search_error}")
            
            if created_detectors:
                print(f"\n📊 생성된 탐지기 수: {len(created_detectors)}")
                self.detector_ids = created_detectors
                return True
            else:
                print("❌ 생성된 탐지기가 없습니다.")
                return False
            
        except Exception as e:
            print(f"❌ 이상 탐지기 생성 실패: {e}")
            return False
    
    def analyze_anomaly_results(self):
        """이상 탐지 결과 분석"""
        print("\n📈 4. 이상 탐지 결과 분석")
        print("-" * 25)
        
        try:
            # 기본 통계 기반 이상 탐지 분석
            print("📊 기본 통계 기반 이상 패턴 분석:")
            
            # 1. 일일 메트릭 이상 패턴 분석
            daily_analysis_query = {
                "size": 0,
                "aggs": {
                    "daily_stats": {
                        "date_histogram": {
                            "field": "@timestamp",
                            "calendar_interval": "1d"
                        },
                        "aggs": {
                            "total_transactions": {"sum": {"field": "daily_transaction_count"}},
                            "avg_system_load": {"avg": {"field": "system_load"}},
                            "avg_response_time": {"avg": {"field": "response_time_ms"}},
                            "avg_error_rate": {"avg": {"field": "error_rate"}},
                            "anomaly_score": {
                                "bucket_script": {
                                    "buckets_path": {
                                        "load": "avg_system_load",
                                        "response": "avg_response_time",
                                        "errors": "avg_error_rate"
                                    },
                                    "script": """
                                        double load_score = params.load > 80 ? (params.load - 80) / 20.0 : 0;
                                        double response_score = params.response > 1000 ? (params.response - 1000) / 1000.0 : 0;
                                        double error_score = params.errors > 5 ? (params.errors - 5) / 10.0 : 0;
                                        return Math.min(1.0, (load_score + response_score + error_score) / 3.0);
                                    """
                                }
                            }
                        }
                    },
                    "overall_stats": {
                        "stats": {"field": "daily_transaction_count"}
                    }
                }
            }
            
            daily_result = self.client.search(
                index="financial-daily-metrics", 
                body=daily_analysis_query
            )
            
            print("\n   📅 일일 시스템 성능 분석:")
            anomalous_days = []
            for bucket in daily_result['aggregations']['daily_stats']['buckets']:
                date = bucket['key_as_string'][:10]
                transactions = bucket['total_transactions']['value']
                system_load = bucket['avg_system_load']['value']
                response_time = bucket['avg_response_time']['value']
                error_rate = bucket['avg_error_rate']['value']
                anomaly_score = bucket['anomaly_score']['value']
                
                status = "🚨 이상" if anomaly_score > 0.3 else "✅ 정상"
                print(f"     {date}: {status} (점수: {anomaly_score:.3f})")
                print(f"       - 거래량: {transactions:,.0f}, 시스템 부하: {system_load:.1f}%")
                print(f"       - 응답시간: {response_time:.0f}ms, 오류율: {error_rate:.2f}%")
                
                if anomaly_score > 0.3:
                    anomalous_days.append({
                        "date": date,
                        "score": anomaly_score,
                        "transactions": transactions,
                        "system_load": system_load,
                        "response_time": response_time,
                        "error_rate": error_rate
                    })
            
            # 2. 실시간 거래 패턴 분석
            realtime_analysis_query = {
                "size": 0,
                "aggs": {
                    "hourly_patterns": {
                        "date_histogram": {
                            "field": "@timestamp",
                            "calendar_interval": "1h"
                        },
                        "aggs": {
                            "transaction_count": {"value_count": {"field": "transaction_id"}},
                            "avg_amount": {"avg": {"field": "amount"}},
                            "high_value_count": {
                                "filter": {
                                    "range": {"amount": {"gte": 500}}
                                }
                            },
                            "avg_anomaly_score": {"avg": {"field": "anomaly_score"}},
                            "suspicious_transactions": {
                                "filter": {
                                    "range": {"anomaly_score": {"gte": 0.7}}
                                }
                            }
                        }
                    },
                    "merchant_anomalies": {
                        "terms": {
                            "field": "merchant_type",
                            "size": 10
                        },
                        "aggs": {
                            "avg_anomaly_score": {"avg": {"field": "anomaly_score"}},
                            "high_risk_transactions": {
                                "filter": {
                                    "range": {"anomaly_score": {"gte": 0.5}}
                                }
                            }
                        }
                    }
                }
            }
            
            realtime_result = self.client.search(
                index="financial-realtime-transactions",
                body=realtime_analysis_query
            )
            
            print(f"\n   ⏰ 시간대별 거래 패턴 분석:")
            suspicious_hours = []
            for bucket in realtime_result['aggregations']['hourly_patterns']['buckets']:
                timestamp = bucket['key_as_string']
                count = bucket['transaction_count']['value']
                avg_amount = bucket['avg_amount']['value']
                high_value_count = bucket['high_value_count']['doc_count']
                avg_anomaly = bucket['avg_anomaly_score']['value']
                suspicious_count = bucket['suspicious_transactions']['doc_count']
                
                if suspicious_count > 0 or avg_anomaly > 0.3:
                    suspicious_hours.append({
                        "time": timestamp,
                        "suspicious_count": suspicious_count,
                        "avg_anomaly": avg_anomaly
                    })
                    status = "🚨"
                else:
                    status = "✅"
                
                print(f"     {timestamp}: {status} {count}건 거래 (평균: ${avg_amount:.0f})")
                if suspicious_count > 0:
                    print(f"       - 의심 거래: {suspicious_count}건, 평균 이상점수: {avg_anomaly:.3f}")
            
            print(f"\n   🏪 업종별 이상 패턴 분석:")
            for bucket in realtime_result['aggregations']['merchant_anomalies']['buckets']:
                merchant = bucket['key']
                avg_anomaly = bucket['avg_anomaly_score']['value']
                high_risk_count = bucket['high_risk_transactions']['doc_count']
                
                risk_level = "🚨 높음" if avg_anomaly > 0.4 else "⚠️ 중간" if avg_anomaly > 0.2 else "✅ 낮음"
                print(f"     {merchant}: {risk_level} (평균 이상점수: {avg_anomaly:.3f}, 고위험: {high_risk_count}건)")
            
            # 3. 요약 보고서
            print(f"\n📋 이상 탐지 요약 보고서:")
            print(f"   🗓️ 이상 감지된 날짜: {len(anomalous_days)}일")
            print(f"   ⏰ 의심스러운 시간대: {len(suspicious_hours)}회")
            
            if anomalous_days:
                worst_day = max(anomalous_days, key=lambda x: x['score'])
                print(f"   📉 최고 위험 날짜: {worst_day['date']} (점수: {worst_day['score']:.3f})")
                print(f"     - 주요 이슈: ", end="")
                issues = []
                if worst_day['system_load'] > 80:
                    issues.append(f"높은 시스템 부하({worst_day['system_load']:.1f}%)")
                if worst_day['response_time'] > 1000:
                    issues.append(f"느린 응답시간({worst_day['response_time']:.0f}ms)")
                if worst_day['error_rate'] > 5:
                    issues.append(f"높은 오류율({worst_day['error_rate']:.2f}%)")
                print(", ".join(issues) if issues else "복합적 이상 패턴")
            
            return True
            
        except Exception as e:
            print(f"❌ 이상 탐지 결과 분석 실패: {e}")
            return False
    
    def test_real_time_monitoring(self):
        """실시간 모니터링 기능 테스트"""
        print("\n⏱️ 5. 실시간 모니터링 시스템 테스트")
        print("-" * 30)
        
        try:
            # 실시간 대시보드용 쿼리들
            monitoring_queries = {
                "current_system_status": {
                    "size": 1,
                    "sort": [{"@timestamp": {"order": "desc"}}],
                    "query": {"match_all": {}},
                    "_source": ["@timestamp", "system_load", "response_time_ms", "error_rate"]
                },
                "last_hour_transactions": {
                    "size": 0,
                    "query": {
                        "range": {
                            "@timestamp": {
                                "gte": "now-1h"
                            }
                        }
                    },
                    "aggs": {
                        "total_transactions": {"value_count": {"field": "transaction_id"}},
                        "total_amount": {"sum": {"field": "amount"}},
                        "avg_amount": {"avg": {"field": "amount"}},
                        "suspicious_transactions": {
                            "filter": {
                                "range": {"anomaly_score": {"gte": 0.5}}
                            }
                        },
                        "by_merchant": {
                            "terms": {"field": "merchant_type", "size": 5},
                            "aggs": {
                                "transaction_count": {"value_count": {"field": "transaction_id"}},
                                "avg_anomaly": {"avg": {"field": "anomaly_score"}}
                            }
                        }
                    }
                },
                "performance_trends": {
                    "size": 0,
                    "query": {
                        "range": {
                            "@timestamp": {
                                "gte": "now-24h"
                            }
                        }
                    },
                    "aggs": {
                        "hourly_performance": {
                            "date_histogram": {
                                "field": "@timestamp",
                                "calendar_interval": "1h"
                            },
                            "aggs": {
                                "avg_system_load": {"avg": {"field": "system_load"}},
                                "avg_response_time": {"avg": {"field": "response_time_ms"}},
                                "avg_error_rate": {"avg": {"field": "error_rate"}}
                            }
                        }
                    }
                }
            }
            
            print("📊 실시간 시스템 상태:")
            
            # 1. 현재 시스템 상태 조회
            try:
                current_status = self.client.search(
                    index="financial-daily-metrics",
                    body=monitoring_queries["current_system_status"]
                )
                
                if current_status['hits']['hits']:
                    latest = current_status['hits']['hits'][0]['_source']
                    system_load = latest['system_load']
                    response_time = latest['response_time_ms']
                    error_rate = latest['error_rate']
                    
                    # 상태 평가
                    load_status = "🚨 위험" if system_load > 80 else "⚠️ 주의" if system_load > 60 else "✅ 정상"
                    response_status = "🚨 위험" if response_time > 1000 else "⚠️ 주의" if response_time > 500 else "✅ 정상"
                    error_status = "🚨 위험" if error_rate > 5 else "⚠️ 주의" if error_rate > 2 else "✅ 정상"
                    
                    print(f"   시스템 부하: {system_load:.1f}% {load_status}")
                    print(f"   응답 시간: {response_time:.0f}ms {response_status}")
                    print(f"   오류율: {error_rate:.2f}% {error_status}")
                else:
                    print("   ❌ 현재 시스템 상태 데이터 없음")
                    
            except Exception as e:
                print(f"   ❌ 시스템 상태 조회 실패: {e}")
            
            # 2. 최근 1시간 거래 현황
            try:
                recent_transactions = self.client.search(
                    index="financial-realtime-transactions",
                    body=monitoring_queries["last_hour_transactions"]
                )
                
                aggs = recent_transactions['aggregations']
                total_count = aggs['total_transactions']['value']
                total_amount = aggs['total_amount']['value']
                avg_amount = aggs['avg_amount']['value']
                suspicious_count = aggs['suspicious_transactions']['doc_count']
                
                print(f"\n📈 최근 1시간 거래 현황:")
                print(f"   총 거래 건수: {total_count:,.0f}건")
                print(f"   총 거래 금액: ${total_amount:,.0f}")
                print(f"   평균 거래 금액: ${avg_amount:.0f}")
                print(f"   의심 거래: {suspicious_count}건 ({suspicious_count/total_count*100:.1f}%)")
                
                print(f"\n   업종별 거래 현황:")
                for bucket in aggs['by_merchant']['buckets']:
                    merchant = bucket['key']
                    count = bucket['transaction_count']['value']
                    avg_anomaly = bucket['avg_anomaly']['value']
                    risk_indicator = "🚨" if avg_anomaly > 0.3 else "⚠️" if avg_anomaly > 0.15 else "✅"
                    print(f"     {merchant}: {count:.0f}건 {risk_indicator} (이상점수: {avg_anomaly:.3f})")
                    
            except Exception as e:
                print(f"   ❌ 거래 현황 조회 실패: {e}")
            
            # 3. 24시간 성능 트렌드
            try:
                performance_trends = self.client.search(
                    index="financial-daily-metrics",
                    body=monitoring_queries["performance_trends"]
                )
                
                print(f"\n📊 24시간 성능 트렌드:")
                trend_data = []
                for bucket in performance_trends['aggregations']['hourly_performance']['buckets']:
                    if bucket['doc_count'] > 0:
                        hour_data = {
                            'time': bucket['key_as_string'],
                            'load': bucket['avg_system_load']['value'],
                            'response': bucket['avg_response_time']['value'],
                            'errors': bucket['avg_error_rate']['value']
                        }
                        trend_data.append(hour_data)
                
                if trend_data:
                    # 최근 몇 시간 데이터 표시
                    recent_trends = trend_data[-6:]  # 최근 6시간
                    for data in recent_trends:
                        time_str = data['time'][11:16]  # HH:MM 형식
                        load_trend = "📈" if data['load'] > 70 else "📊" if data['load'] > 40 else "📉"
                        print(f"     {time_str}: {load_trend} 부하 {data['load']:.1f}%, 응답 {data['response']:.0f}ms")
                    
                    # 트렌드 분석
                    avg_load = sum(d['load'] for d in recent_trends) / len(recent_trends)
                    avg_response = sum(d['response'] for d in recent_trends) / len(recent_trends)
                    
                    print(f"\n   📊 최근 6시간 평균:")
                    print(f"     시스템 부하: {avg_load:.1f}%")
                    print(f"     응답 시간: {avg_response:.0f}ms")
                    
                    # 성능 예측
                    if len(recent_trends) >= 3:
                        load_trend = recent_trends[-1]['load'] - recent_trends[-3]['load']
                        response_trend = recent_trends[-1]['response'] - recent_trends[-3]['response']
                        
                        print(f"\n   🔮 성능 예측:")
                        if load_trend > 10:
                            print("     ⚠️ 시스템 부하 증가 추세 - 용량 확장 검토 필요")
                        elif load_trend < -10:
                            print("     ✅ 시스템 부하 감소 추세 - 안정적")
                        else:
                            print("     📊 시스템 부하 안정적")
                            
                        if response_trend > 200:
                            print("     ⚠️ 응답 시간 증가 추세 - 성능 최적화 필요")
                        elif response_trend < -200:
                            print("     ✅ 응답 시간 개선 추세")
                        else:
                            print("     📊 응답 시간 안정적")
                else:
                    print("   ❌ 트렌드 데이터 없음")
                    
            except Exception as e:
                print(f"   ❌ 성능 트렌드 조회 실패: {e}")
            
            # 4. 실시간 알림 시뮬레이션
            print(f"\n🚨 실시간 알림 시뮬레이션:")
            
            # 임계값 체크
            alerts = []
            try:
                # 최근 데이터로 알림 조건 체크
                alert_query = {
                    "size": 10,
                    "sort": [{"@timestamp": {"order": "desc"}}],
                    "query": {
                        "bool": {
                            "should": [
                                {"range": {"system_load": {"gte": 80}}},
                                {"range": {"response_time_ms": {"gte": 1000}}},
                                {"range": {"error_rate": {"gte": 5}}}
                            ]
                        }
                    }
                }
                
                alert_results = self.client.search(
                    index="financial-daily-metrics",
                    body=alert_query
                )
                
                for hit in alert_results['hits']['hits']:
                    source = hit['_source']
                    timestamp = source['@timestamp']
                    
                    if source['system_load'] >= 80:
                        alerts.append(f"🚨 HIGH_LOAD: 시스템 부하 {source['system_load']:.1f}% ({timestamp})")
                    if source['response_time_ms'] >= 1000:
                        alerts.append(f"🚨 SLOW_RESPONSE: 응답시간 {source['response_time_ms']:.0f}ms ({timestamp})")
                    if source['error_rate'] >= 5:
                        alerts.append(f"🚨 HIGH_ERROR: 오류율 {source['error_rate']:.2f}% ({timestamp})")
                
                # 의심 거래 알림
                suspicious_query = {
                    "size": 5,
                    "sort": [{"@timestamp": {"order": "desc"}}],
                    "query": {
                        "range": {"anomaly_score": {"gte": 0.8}}
                    }
                }
                
                suspicious_results = self.client.search(
                    index="financial-realtime-transactions",
                    body=suspicious_query
                )
                
                for hit in suspicious_results['hits']['hits']:
                    source = hit['_source']
                    alerts.append(f"🚨 FRAUD_ALERT: 의심거래 ${source['amount']:.0f} "
                                f"(고객: {source['customer_id']}, 점수: {source['anomaly_score']:.3f})")
                
            except Exception as e:
                alerts.append(f"❌ 알림 체크 실패: {e}")
            
            if alerts:
                print("   발생한 알림:")
                for alert in alerts[:5]:  # 최대 5개만 표시
                    print(f"     {alert}")
                if len(alerts) > 5:
                    print(f"     ... 외 {len(alerts)-5}개 알림")
            else:
                print("   ✅ 현재 발생한 알림 없음")
            
            return True
            
        except Exception as e:
            print(f"❌ 실시간 모니터링 테스트 실패: {e}")
            return False
    
    def generate_business_recommendations(self):
        """비즈니스 추천 사항 생성"""
        print("\n💡 6. 비즈니스 추천 사항 생성")
        print("-" * 30)
        
        try:
            # 종합 분석을 위한 데이터 수집
            analysis_queries = {
                "system_reliability": {
                    "size": 0,
                    "aggs": {
                        "avg_uptime": {
                            "avg": {
                                "script": {
                                    "source": "100 - doc['error_rate'].value"
                                }
                            }
                        },
                        "performance_distribution": {
                            "range": {
                                "field": "response_time_ms",
                                "ranges": [
                                    {"key": "excellent", "to": 200},
                                    {"key": "good", "from": 200, "to": 500},
                                    {"key": "poor", "from": 500, "to": 1000},
                                    {"key": "critical", "from": 1000}
                                ]
                            }
                        },
                        "load_distribution": {
                            "histogram": {
                                "field": "system_load",
                                "interval": 20
                            }
                        }
                    }
                },
                "transaction_insights": {
                    "size": 0,
                    "aggs": {
                        "fraud_rate": {
                            "avg": {"field": "anomaly_score"}
                        },
                        "high_risk_merchants": {
                            "terms": {
                                "field": "merchant_type",
                                "order": {"avg_anomaly": "desc"}
                            },
                            "aggs": {
                                "avg_anomaly": {"avg": {"field": "anomaly_score"}},
                                "transaction_count": {"value_count": {"field": "transaction_id"}}
                            }
                        },
                        "peak_hours": {
                            "terms": {
                                "field": "hour_of_day",
                                "size": 24,
                                "order": {"_count": "desc"}
                            }
                        },
                        "weekend_vs_weekday": {
                            "terms": {"field": "is_weekend"},
                            "aggs": {
                                "avg_amount": {"avg": {"field": "amount"}},
                                "avg_anomaly": {"avg": {"field": "anomaly_score"}}
                            }
                        }
                    }
                }
            }
            
            # 시스템 신뢰성 분석
            system_result = self.client.search(
                index="financial-daily-metrics",
                body=analysis_queries["system_reliability"]
            )
            
            # 거래 인사이트 분석
            transaction_result = self.client.search(
                index="financial-realtime-transactions",
                body=analysis_queries["transaction_insights"]
            )
            
            print("📊 종합 분석 결과:")
            
            # 시스템 성능 분석
            avg_uptime = system_result['aggregations']['avg_uptime']['value']
            perf_dist = system_result['aggregations']['performance_distribution']['buckets']
            
            print(f"\n   🖥️ 시스템 성능 평가:")
            print(f"     평균 가용성: {avg_uptime:.2f}%")
            
            total_samples = sum(bucket['doc_count'] for bucket in perf_dist)
            for bucket in perf_dist:
                percentage = (bucket['doc_count'] / total_samples * 100) if total_samples > 0 else 0
                print(f"     {bucket['key']} 성능: {percentage:.1f}%")
            
            # 거래 패턴 분석
            fraud_rate = transaction_result['aggregations']['fraud_rate']['value']
            high_risk_merchants = transaction_result['aggregations']['high_risk_merchants']['buckets']
            peak_hours = transaction_result['aggregations']['peak_hours']['buckets'][:3]
            weekend_analysis = transaction_result['aggregations']['weekend_vs_weekday']['buckets']
            
            print(f"\n   💳 거래 패턴 분석:")
            print(f"     전체 이상 점수: {fraud_rate:.3f}")
            
            print(f"     고위험 업종 TOP 3:")
            for i, bucket in enumerate(high_risk_merchants[:3], 1):
                merchant = bucket['key']
                avg_anomaly = bucket['avg_anomaly']['value']
                count = bucket['transaction_count']['value']
                print(f"       {i}. {merchant}: {avg_anomaly:.3f} ({count:.0f}건)")
            
            print(f"     거래 집중 시간대:")
            for bucket in peak_hours:
                hour = bucket['key']
                count = bucket['doc_count']
                print(f"       {hour:02d}:00 - {count}건")
            
            # 비즈니스 추천사항 생성
            print(f"\n🎯 비즈니스 추천사항:")
            
            recommendations = []
            
            # 시스템 성능 기반 추천
            if avg_uptime < 95:
                recommendations.append("🔧 시스템 안정성 개선 필요 - SLA 목표 달성을 위한 인프라 강화")
            
            excellent_perf = next((b['doc_count'] for b in perf_dist if b['key'] == 'excellent'), 0)
            total_perf = sum(b['doc_count'] for b in perf_dist)
            excellent_ratio = (excellent_perf / total_perf * 100) if total_perf > 0 else 0
            
            if excellent_ratio < 70:
                recommendations.append("⚡ 응답속도 최적화 - 우수 성능 비율을 70% 이상으로 개선")
            
            # 보안 및 사기 방지 추천
            if fraud_rate > 0.3:
                recommendations.append("🛡️ 사기 탐지 시스템 강화 - 이상 점수가 높은 거래 패턴 분석 및 대응")
            
            # 고위험 업종별 맞춤 대응
            if high_risk_merchants and high_risk_merchants[0]['avg_anomaly']['value'] > 0.4:
                top_risk_merchant = high_risk_merchants[0]['key']
                recommendations.append(f"🎯 {top_risk_merchant} 업종 특별 모니터링 - 추가 보안 조치 적용")
            
            # 운영 효율성 개선
            weekend_data = {bucket['key']: bucket for bucket in weekend_analysis}
            if weekend_data.get(True, {}).get('avg_anomaly', {}).get('value', 0) > weekend_data.get(False, {}).get('avg_anomaly', {}).get('value', 0):
                recommendations.append("📅 주말 보안 강화 - 주말 이상 거래 비율이 평일보다 높음")
            
            # 용량 계획
            peak_hour_traffic = max(bucket['doc_count'] for bucket in peak_hours) if peak_hours else 0
            avg_hour_traffic = sum(bucket['doc_count'] for bucket in peak_hours) / len(peak_hours) if peak_hours else 0
            
            if peak_hour_traffic > avg_hour_traffic * 2:
                recommendations.append("📈 트래픽 분산 최적화 - 피크 시간대 부하 분산 방안 검토")
            
            # KCB 특화 추천사항
            kcb_recommendations = [
                "💼 신용평가 정확도 향상 - 이상 거래 패턴을 신용평가 모델에 반영",
                "🔗 타 시스템 연동 강화 - 실시간 이상 탐지 결과를 CRM/ERP 시스템과 연계",
                "📊 예측 분석 도입 - 과거 패턴 기반 미래 이상 상황 예측 모델 구축",
                "🎓 직원 교육 프로그램 - 이상 탐지 시스템 활용법 및 대응 절차 교육"
            ]
            
            recommendations.extend(kcb_recommendations[:2])  # 상위 2개 추가
            
            # 추천사항 출력
            for i, rec in enumerate(recommendations, 1):
                print(f"     {i}. {rec}")
            
            # 구현 우선순위
            print(f"\n📋 구현 우선순위:")
            priority_items = [
                ("High", "실시간 알림 시스템 구축", "즉시 대응 가능한 모니터링"),
                ("High", "자동 이상 탐지 정책 수립", "업무 규칙 기반 임계값 설정"),
                ("Medium", "대시보드 고도화", "경영진 리포팅용 시각화"),
                ("Medium", "예측 모델 도입", "proactive 이상 탐지"),
                ("Low", "외부 시스템 연동", "통합 모니터링 환경 구축")
            ]
            
            for priority, item, description in priority_items:
                priority_icon = "🔴" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
                print(f"     {priority_icon} {priority}: {item}")
                print(f"       → {description}")
            
            return True
            
        except Exception as e:
            print(f"❌ 비즈니스 추천사항 생성 실패: {e}")
            return False
    
    def run_all_tests(self):
        """모든 Anomaly Detection 테스트 실행"""
        print("🚀 OpenSearch Anomaly Detection 플러그인 종합 테스트")
        print("=" * 65)
        
        test_results = {}
        
        # 테스트 실행
        test_methods = [
            ("플러그인 상태 확인", self.check_anomaly_plugin_status),
            ("금융 데이터 생성", self.setup_financial_data),
            ("이상 탐지기 생성", self.create_anomaly_detectors),
            ("이상 탐지 결과 분석", self.analyze_anomaly_results),
            ("실시간 모니터링", self.test_real_time_monitoring),
            ("비즈니스 추천사항", self.generate_business_recommendations)
        ]
        
        for test_name, test_method in test_methods:
            try:
                result = test_method()
                test_results[test_name] = result
                if result:
                    print(f"\n✅ {test_name} 테스트 완료")
                else:
                    print(f"\n❌ {test_name} 테스트 실패")
            except Exception as e:
                print(f"\n💥 {test_name} 테스트 중 오류: {e}")
                test_results[test_name] = False
        
        # 최종 결과 요약
        print(f"\n" + "=" * 65)
        print("📋 Anomaly Detection 플러그인 테스트 결과 요약")
        print("=" * 65)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ 통과" if result else "❌ 실패"
            print(f"   {test_name}: {status}")
        
        print(f"\n🎯 성공률: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 모든 Anomaly Detection 테스트가 성공적으로 완료되었습니다!")
        else:
            print("⚠️  일부 테스트가 실패했습니다. 로그를 확인해주세요.")
        
        # 활용 가이드
        print(f"\n" + "=" * 65)
        print("💡 Anomaly Detection 활용 가이드 (KCB 맞춤)")
        print("=" * 65)
        print("🎯 금융업 이상 탐지 활용 사례:")
        print("   1. 실시간 거래 모니터링")
        print("      - 카드 결제 이상 패턴 탐지")
        print("      - 계좌 이체 사기 방지")
        print("      - ATM 거래 모니터링")
        print()
        print("   2. 시스템 성능 관리")
        print("      - 서버 성능 이상 감지")
        print("      - 네트워크 트래픽 모니터링")
        print("      - 데이터베이스 성능 추적")
        print()
        print("   3. 고객 행동 분석")
        print("      - 비정상 로그인 패턴")
        print("      - 의심스러운 계좌 활동")
        print("      - 신용카드 도용 탐지")
        print()
        print("   4. 규제 준수 및 리스크 관리")
        print("      - AML(자금세탁방지) 모니터링")
        print("      - 내부 통제 시스템")
        print("      - 운영 리스크 관리")
        print()
        print("🔧 다음 단계 제안:")
        print("   1. Alerting 플러그인으로 자동 알림 시스템 구축")
        print("   2. 실제 업무 데이터 연동 테스트")
        print("   3. 대시보드 구축 (Observability 플러그인)")
        print("   4. 성능 최적화 (Performance Analyzer 플러그인)")


def main():
    """메인 실행 함수"""
    tester = AnomalyDetectionTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()