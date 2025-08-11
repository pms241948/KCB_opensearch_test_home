PS C:\Users\user\Desktop\opensearch-lab> python .\simple_test.py
🔍 OpenSearch 연결 테스트 시작...
✅ OpenSearch 연결 성공!
   버전: 2.13.0
   클러스터: opensearch-local

📦 설치된 플러그인:
   name         component                            version
   opensearch-1 opensearch-alerting                  2.13.0.0
   opensearch-1 opensearch-anomaly-detection         2.13.0.0
   opensearch-1 opensearch-asynchronous-search       2.13.0.0
   opensearch-1 opensearch-cross-cluster-replication 2.13.0.0
   opensearch-1 opensearch-custom-codecs             2.13.0.0
   opensearch-1 opensearch-flow-framework            2.13.0.0
   opensearch-1 opensearch-geospatial                2.13.0.0
   opensearch-1 opensearch-index-management          2.13.0.0
   opensearch-1 opensearch-job-scheduler             2.13.0.0
   opensearch-1 opensearch-knn                       2.13.0.0
   opensearch-1 opensearch-ml                        2.13.0.0
   opensearch-1 opensearch-neural-search             2.13.0.0
   opensearch-1 opensearch-notifications             2.13.0.0
   opensearch-1 opensearch-notifications-core        2.13.0.0
   opensearch-1 opensearch-observability             2.13.0.0
   opensearch-1 opensearch-performance-analyzer      2.13.0.0
   opensearch-1 opensearch-reports-scheduler         2.13.0.0
   opensearch-1 opensearch-security                  2.13.0.0
   opensearch-1 opensearch-security-analytics        2.13.0.0
   opensearch-1 opensearch-skills                    2.13.0.0
   opensearch-1 opensearch-sql                       2.13.0.0

🔍 검색 테스트:
   찾은 문서 수: 0

🎉 모든 테스트가 성공했습니다!
PS C:\Users\user\Desktop\opensearch-lab> python .\full_plugin_test.py
🔧 OpenSearch 플러그인 테스터 시작
--------------------------------------------------
🚀 OpenSearch 플러그인 전체 테스트를 시작합니다!
============================================================
✅ OpenSearch 버전: 2.13.0
✅ 클러스터: opensearch-local

⏳ Security 플러그인 테스트 중...

=== 🔐 1. Security 플러그인 테스트 ===
✅ 현재 사용자: admin
✅ 사용자 역할: own_index, all_access
✅ 총 사용자 수: 7명

⏳ SQL 플러그인 테스트 중...

=== 🔍 2. SQL 플러그인 테스트 ===
✅ 직원 데이터 생성: 5명

📊 전체 직원 조회:
   결과:
     ['김철수', 'IT', 7000]
     ['이영희', 'HR', 6500]
     ['박민수', 'IT', 6000]

📊 IT 부서 직원:
   결과:
     ['김철수', '개발팀장', 7000]
     ['박민수', '시니어개발자', 6000]
     ['정호영', '주니어개발자', 4500]

📊 부서별 평균 연봉:
   결과:
     ['Finance', 5500.0]
     ['HR', 6500.0]
     ['IT', 5833.333333333333]

⏳ KNN 플러그인 테스트 중...

=== 🎯 3. KNN 벡터 검색 플러그인 테스트 ===
✅ KNN 인덱스 생성 완료
✅ 상품 데이터 생성: 6개

🔍 벡터 검색 (스마트폰과 유사한 상품):
   1. 스마트폰 (유사도: 1.0000)
   2. 태블릿 (유사도: 0.9709)
   3. 노트북 (유사도: 0.8929)

⏳ Alerting 플러그인 테스트 중...

=== 🚨 4. Alerting 플러그인 테스트 ===
❌ Alerting 플러그인 응답 오류: 405

⏳ ML Commons 플러그인 테스트 중...

=== 🤖 5. ML Commons 플러그인 테스트 ===
✅ ML Commons 플러그인 활성화
✅ ML 노드 수: 1
   ✅ ML용 고객 데이터 생성: 5명

⏳ Performance Analyzer 플러그인 테스트 중...

=== ⚡ 6. Performance Analyzer 플러그인 테스트 ===
⚠️ Performance Analyzer 접근 불가: HTTPConnectionPool(host='localhost', port=9600): Read timed out. (read timeout=5)
   (Performance Analyzer는 별도 설정이 필요할 수 있습니다)

⏳ Index Management 플러그인 테스트 중...

=== 📁 7. Index Management 플러그인 테스트 ===
✅ Index Management 플러그인 활성화
✅ 현재 ISM 정책 수: 0

⏳ Observability 플러그인 테스트 중...

=== 👁️ 8. Observability 플러그인 테스트 ===
✅ Observability 플러그인 활성화
✅ 관측성 객체 수: 0

============================================================
🎯 플러그인 테스트 결과 요약
----------------------------------------
Security             : ✅ 성공
SQL                  : ✅ 성공
KNN                  : ✅ 성공
Alerting             : ❌ 실패
ML Commons           : ✅ 성공
Performance Analyzer : ✅ 성공
Index Management     : ✅ 성공
Observability        : ✅ 성공

📊 총 8개 플러그인 중 7개 성공
🎉 대부분의 플러그인이 정상 작동합니다!

🌐 다음 단계:
   1. http://opensearch.local 에서 Dashboards 접속
   2. 생성된 인덱스들을 확인해보세요:
      - kcb-employees (직원 데이터)
      - kcb-products (상품 데이터)
      - kcb-customers (고객 데이터)