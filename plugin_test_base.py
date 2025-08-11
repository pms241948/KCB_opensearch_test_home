#!/usr/bin/env python3
"""
OpenSearch 플러그인 개별 테스트 - 기본 구조 + Security 플러그인
"""

import requests
import json
import time
from opensearchpy import OpenSearch, RequestsHttpConnection
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PluginTesterBase:
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
        
        print("🔍 OpenSearch 플러그인 개별 테스트")
        print("=" * 50)

    def test_connection(self):
        """연결 테스트"""
        try:
            info = self.client.info()
            print(f"✅ OpenSearch 버전: {info['version']['number']}")
            print(f"✅ 클러스터: {info['cluster_name']}")
            return True
        except Exception as e:
            print(f"❌ 연결 실패: {e}")
            return False

    def test_security_plugin(self):
        """Security 플러그인 상세 테스트"""
        print("\n=== 🔐 Security 플러그인 테스트 ===")
        
        results = {
            "플러그인명": "opensearch-security",
            "기능목록": [],
            "테스트결과": {},
            "활용방안": []
        }
        
        try:
            # 1. 현재 사용자 인증 정보 확인
            print("\n📋 1. 사용자 인증 정보")
            auth_response = requests.get(
                f"{self.base_url}/_plugins/_security/authinfo",
                auth=self.auth,
                verify=False
            )
            
            if auth_response.status_code == 200:
                auth_info = auth_response.json()
                print(f"   ✅ 현재 사용자: {auth_info.get('user_name')}")
                print(f"   ✅ 사용자 역할: {', '.join(auth_info.get('roles', []))}")
                print(f"   ✅ 백엔드 역할: {', '.join(auth_info.get('backend_roles', []))}")
                
                results["기능목록"].append("사용자 인증 및 세션 관리")
                results["테스트결과"]["사용자인증"] = "성공"
            else:
                print(f"   ❌ 인증 정보 조회 실패: {auth_response.status_code}")
                results["테스트결과"]["사용자인증"] = "실패"
            
            # 2. 사용자 목록 관리
            print("\n👥 2. 사용자 관리")
            users_response = requests.get(
                f"{self.base_url}/_plugins/_security/api/internalusers",
                auth=self.auth,
                verify=False
            )
            
            if users_response.status_code == 200:
                users = users_response.json()
                print(f"   ✅ 총 사용자 수: {len(users)}명")
                
                # 사용자 목록 표시 (최대 5명)
                print("   📝 등록된 사용자:")
                for i, (username, user_info) in enumerate(list(users.items())[:5]):
                    backend_roles = user_info.get('backend_roles', [])
                    roles_str = ', '.join(backend_roles) if backend_roles else '기본 역할'
                    print(f"      - {username}: {roles_str}")
                
                if len(users) > 5:
                    print(f"      ... 외 {len(users) - 5}명 더")
                
                results["기능목록"].append("내부 사용자 관리")
                results["테스트결과"]["사용자관리"] = f"{len(users)}명 관리 중"
            else:
                print(f"   ❌ 사용자 목록 조회 실패: {users_response.status_code}")
                results["테스트결과"]["사용자관리"] = "실패"
            
            # 3. 역할 기반 접근 제어 (RBAC)
            print("\n🎭 3. 역할 기반 접근 제어")
            roles_response = requests.get(
                f"{self.base_url}/_plugins/_security/api/roles",
                auth=self.auth,
                verify=False
            )
            
            if roles_response.status_code == 200:
                roles = roles_response.json()
                print(f"   ✅ 총 역할 수: {len(roles)}개")
                
                # 주요 역할 표시
                print("   📝 주요 역할:")
                role_count = 0
                for role_name, role_info in roles.items():
                    if role_count >= 5:
                        break
                    
                    cluster_perms = role_info.get('cluster_permissions', [])
                    index_perms = role_info.get('index_permissions', [])
                    
                    print(f"      - {role_name}:")
                    print(f"        클러스터 권한: {len(cluster_perms)}개")
                    print(f"        인덱스 권한: {len(index_perms)}개")
                    
                    role_count += 1
                
                results["기능목록"].append("역할 기반 접근 제어 (RBAC)")
                results["테스트결과"]["역할관리"] = f"{len(roles)}개 역할"
            else:
                print(f"   ❌ 역할 목록 조회 실패: {roles_response.status_code}")
                results["테스트결과"]["역할관리"] = "실패"
            
            # 4. 멀티테넌시 (Multi-tenancy)
            print("\n🏢 4. 멀티테넌시")
            tenants_response = requests.get(
                f"{self.base_url}/_plugins/_security/api/tenants",
                auth=self.auth,
                verify=False
            )
            
            if tenants_response.status_code == 200:
                tenants = tenants_response.json()
                print(f"   ✅ 총 테넌트 수: {len(tenants)}개")
                
                # 테넌트 목록 표시
                print("   📝 테넌트 목록:")
                for tenant_name, tenant_info in list(tenants.items())[:3]:
                    description = tenant_info.get('description', '설명 없음')
                    reserved = tenant_info.get('reserved', False)
                    status = "(시스템 예약)" if reserved else "(사용자 정의)"
                    print(f"      - {tenant_name}: {description} {status}")
                
                results["기능목록"].append("멀티테넌시 (조직별 데이터 분리)")
                results["테스트결과"]["멀티테넌시"] = f"{len(tenants)}개 테넌트"
            else:
                print(f"   ❌ 테넌트 목록 조회 실패: {tenants_response.status_code}")
                results["테스트결과"]["멀티테넌시"] = "실패"
            
            # 5. 역할 매핑 (Role Mapping)
            print("\n🔗 5. 역할 매핑")
            rolesmapping_response = requests.get(
                f"{self.base_url}/_plugins/_security/api/rolesmapping",
                auth=self.auth,
                verify=False
            )
            
            if rolesmapping_response.status_code == 200:
                role_mappings = rolesmapping_response.json()
                print(f"   ✅ 역할 매핑 수: {len(role_mappings)}개")
                
                # 주요 매핑 표시
                print("   📝 주요 역할 매핑:")
                for mapping_name, mapping_info in list(role_mappings.items())[:3]:
                    backend_roles = mapping_info.get('backend_roles', [])
                    users = mapping_info.get('users', [])
                    print(f"      - {mapping_name}:")
                    if backend_roles:
                        print(f"        백엔드 역할: {', '.join(backend_roles)}")
                    if users:
                        print(f"        사용자: {', '.join(users)}")
                
                results["기능목록"].append("역할 매핑 관리")
                results["테스트결과"]["역할매핑"] = f"{len(role_mappings)}개 매핑"
            else:
                print(f"   ❌ 역할 매핑 조회 실패: {rolesmapping_response.status_code}")
                results["테스트결과"]["역할매핑"] = "실패"
            
            # 6. 보안 설정 확인
            print("\n🔒 6. 보안 설정")
            try:
                # 보안 상태 확인
                health_response = requests.get(
                    f"{self.base_url}/_plugins/_security/health",
                    auth=self.auth,
                    verify=False
                )
                
                if health_response.status_code == 200:
                    health_info = health_response.json()
                    print(f"   ✅ 보안 플러그인 상태: {health_info.get('status', '정상')}")
                    results["테스트결과"]["보안상태"] = "정상"
                else:
                    print("   ⚠️ 보안 상태 확인 불가 (정상 동작)")
                    results["테스트결과"]["보안상태"] = "확인불가"
                
                # SSL/TLS 설정 확인
                print("   ✅ SSL/TLS 암호화: 활성화 (HTTPS 연결 성공)")
                results["기능목록"].append("SSL/TLS 전송 암호화")
                
            except Exception as e:
                print(f"   ⚠️ 보안 설정 확인 중 오류: {e}")
            
            # 7. 감사 로깅 (Audit Logging)
            print("\n📊 7. 감사 로깅")
            try:
                audit_response = requests.get(
                    f"{self.base_url}/_plugins/_security/api/audit",
                    auth=self.auth,
                    verify=False
                )
                
                if audit_response.status_code == 200:
                    print("   ✅ 감사 로깅 설정 조회 가능")
                    results["기능목록"].append("보안 이벤트 감사 로깅")
                    results["테스트결과"]["감사로깅"] = "지원됨"
                elif audit_response.status_code == 405:
                    print("   ⚠️ 감사 로깅은 별도 설정 필요")
                    results["테스트결과"]["감사로깅"] = "설정 필요"
                else:
                    print(f"   ❌ 감사 로깅 확인 실패: {audit_response.status_code}")
                    results["테스트결과"]["감사로깅"] = "실패"
                    
            except Exception as e:
                print(f"   ⚠️ 감사 로깅 확인 오류: {e}")
                results["테스트결과"]["감사로깅"] = "오류"
            
            # 활용 방안 정리
            results["활용방안"] = [
                "부서별 사용자 계정 및 권한 관리",
                "인덱스별 세분화된 접근 제어",
                "필드 레벨 보안으로 민감 정보 보호",
                "문서 레벨 보안으로 조건부 데이터 접근",
                "멀티테넌시로 조직간 데이터 완전 분리",
                "LDAP/Active Directory 연동",
                "SSO (Single Sign-On) 구현",
                "감사 로그를 통한 보안 모니터링",
                "API 키 기반 애플리케이션 인증",
                "IP 기반 접근 제한"
            ]
            
            return results
            
        except Exception as e:
            print(f"❌ Security 플러그인 전체 테스트 오류: {e}")
            results["테스트결과"]["전체오류"] = str(e)
            return results

    def print_security_summary(self, results):
        """Security 플러그인 결과 요약"""
        print("\n" + "="*60)
        print("📊 Security 플러그인 테스트 결과 요약")
        print("="*60)
        
        # 기능 목록
        features = results.get("기능목록", [])
        print(f"\n🔧 지원 기능 ({len(features)}개):")
        for i, feature in enumerate(features, 1):
            print(f"   {i:2d}. {feature}")
        
        # 테스트 결과
        test_results = results.get("테스트결과", {})
        print(f"\n🧪 테스트 결과:")
        success_count = 0
        total_count = 0
        
        for test_name, result in test_results.items():
            if test_name != "전체오류":
                total_count += 1
                if "성공" in str(result) or "정상" in str(result) or "개" in str(result):
                    success_count += 1
                    print(f"   ✅ {test_name}: {result}")
                elif "실패" in str(result):
                    print(f"   ❌ {test_name}: {result}")
                else:
                    print(f"   ⚠️ {test_name}: {result}")
        
        if total_count > 0:
            success_rate = (success_count / total_count) * 100
            print(f"\n📈 성공률: {success_rate:.1f}% ({success_count}/{total_count})")
        
        # 활용 방안
        use_cases = results.get("활용방안", [])
        print(f"\n💡 주요 활용 방안:")
        for i, use_case in enumerate(use_cases[:5], 1):
            print(f"   {i}. {use_case}")
        
        if len(use_cases) > 5:
            print(f"   ... 외 {len(use_cases)-5}개 더")

    def run_security_test(self):
        """Security 플러그인 테스트 실행"""
        if not self.test_connection():
            return
        
        print("\n🚀 Security 플러그인 상세 테스트를 시작합니다!")
        
        results = self.test_security_plugin()
        self.print_security_summary(results)
        
        print(f"\n🌐 다음 단계:")
        print("   1. OpenSearch Dashboards에서 보안 설정 확인")
        print("   2. 사용자 및 역할 추가 생성 테스트")
        print("   3. 인덱스별 접근 권한 설정")
        print("   4. 멀티테넌시 활용한 부서별 대시보드 구성")
        
        print(f"\n💻 OpenSearch Dashboards 접속:")
        print("   http://opensearch.local")
        print("   사용자: admin / 비밀번호: Kcb2025opSLabAi9")

if __name__ == "__main__":
    tester = PluginTesterBase()
    tester.run_security_test()