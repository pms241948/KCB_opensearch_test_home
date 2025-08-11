#!/usr/bin/env python3
"""
OpenSearch 간단한 연결 테스트
"""

import requests
from opensearchpy import OpenSearch, RequestsHttpConnection
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_opensearch_connection():
    """OpenSearch 연결 테스트"""
    print("🔍 OpenSearch 연결 테스트 시작...")
    
    # OpenSearch 클라이언트 생성
    client = OpenSearch(
        hosts=[{'host': 'localhost', 'port': 9200}],
        http_auth=('admin', 'Kcb2025opSLabAi9'),
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        connection_class=RequestsHttpConnection
    )
    
    try:
        # 클러스터 정보 조회
        info = client.info()
        print(f"✅ OpenSearch 연결 성공!")
        print(f"   버전: {info['version']['number']}")
        print(f"   클러스터: {info['cluster_name']}")
        
        # 플러그인 목록 조회
        response = requests.get(
            "https://localhost:9200/_cat/plugins?v",
            auth=('admin', 'Kcb2025opSLabAi9'),
            verify=False
        )
        
        if response.status_code == 200:
            print(f"\n📦 설치된 플러그인:")
            plugins = response.text.strip().split('\n')
            for plugin in plugins:
                print(f"   {plugin}")
        
        # 간단한 인덱스 생성 테스트
        test_index = "test-connection"
        
        # 기존 인덱스가 있다면 삭제
        if client.indices.exists(index=test_index):
            client.indices.delete(index=test_index)
        
        # 새 인덱스 생성
        client.indices.create(
            index=test_index,
            body={
                "mappings": {
                    "properties": {
                        "message": {"type": "text"},
                        "timestamp": {"type": "date"}
                    }
                }
            }
        )
        
        # 테스트 문서 추가
        client.index(
            index=test_index,
            id=1,
            body={
                "message": "OpenSearch 연결 테스트 성공!",
                "timestamp": "2024-01-15T10:30:00"
            }
        )
        
        # 문서 검색
        result = client.search(
            index=test_index,
            body={"query": {"match_all": {}}}
        )
        
        print(f"\n🔍 검색 테스트:")
        print(f"   찾은 문서 수: {result['hits']['total']['value']}")
        if result['hits']['hits']:
            doc = result['hits']['hits'][0]['_source']
            print(f"   메시지: {doc['message']}")
        
        print(f"\n🎉 모든 테스트가 성공했습니다!")
        return True
        
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False

if __name__ == "__main__":
    test_opensearch_connection()