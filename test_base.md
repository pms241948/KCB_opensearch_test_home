PS C:\Users\user\Desktop\opensearch-lab> python plugin_test_base.py
🔍 OpenSearch 플러그인 개별 테스트
==================================================
✅ OpenSearch 버전: 2.13.0
✅ 클러스터: opensearch-local

🚀 Security 플러그인 상세 테스트를 시작합니다!

=== 🔐 Security 플러그인 테스트 ===

📋 1. 사용자 인증 정보
   ✅ 현재 사용자: admin
   ✅ 사용자 역할: own_index, all_access
   ✅ 백엔드 역할: admin

👥 2. 사용자 관리
   ✅ 총 사용자 수: 7명
   📝 등록된 사용자:
      - logstash: logstash
      - snapshotrestore: snapshotrestore
      - admin: admin
      - kibanaserver: 기본 역할
      - kibanaro: kibanauser, readall
      ... 외 2명 더

🎭 3. 역할 기반 접근 제어
   ✅ 총 역할 수: 48개
   📝 주요 역할:
      - security_analytics_ack_alerts:
        클러스터 권한: 1개
        인덱스 권한: 0개
      - observability_read_access:
        클러스터 권한: 1개
        인덱스 권한: 0개
      - kibana_user:
        클러스터 권한: 1개
        인덱스 권한: 2개
      - own_index:
        클러스터 권한: 1개
        인덱스 권한: 1개
      - alerting_full_access:
        클러스터 권한: 4개
        인덱스 권한: 1개

🏢 4. 멀티테넌시
   ✅ 총 테넌트 수: 2개
   📝 테넌트 목록:
      - global_tenant: Global tenant (시스템 예약)
      - admin_tenant: Demo tenant for admin user (사용자 정의)

🔗 5. 역할 매핑
   ✅ 역할 매핑 수: 7개
   📝 주요 역할 매핑:
      - manage_snapshots:
        백엔드 역할: snapshotrestore
      - logstash:
        백엔드 역할: logstash
      - own_index:
        사용자: *

🔒 6. 보안 설정
   ✅ 보안 플러그인 상태: UP
   ✅ SSL/TLS 암호화: 활성화 (HTTPS 연결 성공)

📊 7. 감사 로깅
   ✅ 감사 로깅 설정 조회 가능

============================================================
📊 Security 플러그인 테스트 결과 요약
============================================================

🔧 지원 기능 (7개):
    1. 사용자 인증 및 세션 관리
    2. 내부 사용자 관리
    3. 역할 기반 접근 제어 (RBAC)
    4. 멀티테넌시 (조직별 데이터 분리)
    5. 역할 매핑 관리
    6. SSL/TLS 전송 암호화
    7. 보안 이벤트 감사 로깅

🧪 테스트 결과:
   ✅ 사용자인증: 성공
   ⚠️ 사용자관리: 7명 관리 중
   ✅ 역할관리: 48개 역할
   ✅ 멀티테넌시: 2개 테넌트
   ✅ 역할매핑: 7개 매핑
   ✅ 보안상태: 정상
   ⚠️ 감사로깅: 지원됨

📈 성공률: 71.4% (5/7)

💡 주요 활용 방안:
   1. 부서별 사용자 계정 및 권한 관리
   2. 인덱스별 세분화된 접근 제어
   3. 필드 레벨 보안으로 민감 정보 보호
   4. 문서 레벨 보안으로 조건부 데이터 접근
   5. 멀티테넌시로 조직간 데이터 완전 분리
   ... 외 5개 더

🌐 다음 단계:
   1. OpenSearch Dashboards에서 보안 설정 확인
   2. 사용자 및 역할 추가 생성 테스트
   3. 인덱스별 접근 권한 설정
   4. 멀티테넌시 활용한 부서별 대시보드 구성

💻 OpenSearch Dashboards 접속:
   http://opensearch.local
   사용자: admin / 비밀번호: Kcb2025opSLabAi9