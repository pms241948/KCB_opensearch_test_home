#!/usr/bin/env python3
"""
OpenSearch SQL 플러그인 상세 테스트
"""

import requests
import json
import time
from opensearchpy import OpenSearch, RequestsHttpConnection
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SQLPluginTester:
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

    def create_test_data(self):
        """SQL 테스트용 샘플 데이터 생성"""
        print("\n📊 테스트 데이터 생성 중...")
        
        # 직원 데이터 인덱스
        employees_index = "sql-test-employees"
        
        if self.client.indices.exists(index=employees_index):
            self.client.indices.delete(index=employees_index)
        
        # 직원 데이터 매핑
        employee_mapping = {
            "mappings": {
                "properties": {
                    "employee_id": {"type": "keyword"},
                    "name": {"type": "text"},
                    "department": {"type": "keyword"},
                    "position": {"type": "keyword"},
                    "salary": {"type": "integer"},
                    "hire_date": {"type": "date"},
                    "age": {"type": "integer"},
                    "email": {"type": "keyword"},
                    "performance_score": {"type": "float"}
                }
            }
        }
        
        self.client.indices.create(index=employees_index, body=employee_mapping)
        
        # 샘플 직원 데이터
        employees = [
            {"employee_id": "EMP001", "name": "김철수", "department": "IT", "position": "개발팀장", "salary": 7000, "hire_date": "2020-01-15", "age": 35, "email": "kim@company.com", "performance_score": 4.5},
            {"employee_id": "EMP002", "name": "이영희", "department": "HR", "position": "인사과장", "salary": 6500, "hire_date": "2019-03-10", "age": 32, "email": "lee@company.com", "performance_score": 4.2},
            {"employee_id": "EMP003", "name": "박민수", "department": "IT", "position": "시니어개발자", "salary": 6000, "hire_date": "2021-06-01", "age": 29, "email": "park@company.com", "performance_score": 4.7},
            {"employee_id": "EMP004", "name": "최은지", "department": "Finance", "position": "재무분석가", "salary": 5500, "hire_date": "2022-09-20", "age": 28, "email": "choi@company.com", "performance_score": 4.0},
            {"employee_id": "EMP005", "name": "정호영", "department": "IT", "position": "주니어개발자", "salary": 4500, "hire_date": "2023-01-05", "age": 26, "email": "jung@company.com", "performance_score": 3.8},
            {"employee_id": "EMP006", "name": "강수정", "department": "Marketing", "position": "마케팅매니저", "salary": 5800, "hire_date": "2021-08-12", "age": 31, "email": "kang@company.com", "performance_score": 4.3},
            {"employee_id": "EMP007", "name": "윤태현", "department": "IT", "position": "데이터엔지니어", "salary": 6200, "hire_date": "2020-11-30", "age": 33, "email": "yoon@company.com", "performance_score": 4.6},
            {"employee_id": "EMP008", "name": "임소영", "department": "HR", "position": "채용담당자", "salary": 4800, "hire_date": "2022-03-15", "age": 27, "email": "lim@company.com", "performance_score": 4.1},
            {"employee_id": "EMP009", "name": "조성민", "department": "Finance", "position": "회계사", "salary": 5200, "hire_date": "2021-12-01", "age": 30, "email": "cho@company.com", "performance_score": 3.9},
            {"employee_id": "EMP010", "name": "한미래", "department": "Marketing", "position": "디지털마케터", "salary": 5000, "hire_date": "2023-05-20", "age": 25, "email": "han@company.com", "performance_score": 4.4}
        ]
        
        # 데이터 삽입
        for i, emp in enumerate(employees):
            self.client.index(index=employees_index, id=i+1, body=emp)
        
        time.sleep(2)  # 인덱싱 대기
        print(f"   ✅ 직원 데이터 생성: {len(employees)}명")
        
        return employees_index

    def execute_sql_query(self, query, test_name, show_results=True):
        """SQL 쿼리 실행 및 결과 표시"""
        try:
            print(f"\n🔍 {test_name}")
            print(f"   SQL: {query.strip()}")
            
            response = requests.post(
                f"{self.base_url}/_plugins/_sql",
                auth=self.auth,
                headers={"Content-Type": "application/json"},
                data=json.dumps({"query": query}),
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 실행 성공")
                
                if 'datarows' in result and result['datarows'] and show_results:
                    print(f"   📊 결과 ({len(result['datarows'])}행):")
                    
                    # 컬럼 헤더 표시
                    if 'schema' in result:
                        headers = [col['name'] for col in result['schema']]
                        print(f"      {' | '.join(headers)}")
                        print(f"      {'-' * (len(' | '.join(headers)))}")
                    
                    # 결과 행 표시 (최대 5행)
                    for i, row in enumerate(result['datarows'][:5]):
                        formatted_row = []
                        for item in row:
                            if isinstance(item, float):
                                formatted_row.append(f"{item:.1f}")
                            elif isinstance(item, int) and item > 1000:
                                formatted_row.append(f"{item:,}")
                            else:
                                formatted_row.append(str(item))
                        print(f"      {' | '.join(formatted_row)}")
                    
                    if len(result['datarows']) > 5:
                        print(f"      ... 외 {len(result['datarows'])-5}행 더")
                
                return True, result
            else:
                print(f"   ❌ 실행 실패: {response.status_code}")
                if response.text:
                    print(f"      오류: {response.text[:100]}")
                return False, None
                
        except Exception as e:
            print(f"   ❌ 쿼리 오류: {e}")
            return False, None

    def test_basic_sql_features(self, index_name):
        """기본 SQL 기능 테스트"""
        print("\n=== 📋 기본 SQL 기능 테스트 ===")
        
        results = {"기본기능": [], "테스트결과": {}}
        
        # 1. SELECT 문
        basic_queries = [
            {
                "name": "전체 데이터 조회",
                "query": f"SELECT * FROM `{index_name}` LIMIT 3",
                "feature": "SELECT * (전체 컬럼 조회)"
            },
            {
                "name": "특정 컬럼 선택",
                "query": f"SELECT name, department, salary FROM `{index_name}` LIMIT 5",
                "feature": "SELECT 특정 컬럼"
            },
            {
                "name": "WHERE 조건 검색",
                "query": f"SELECT name, position, salary FROM `{index_name}` WHERE department = 'IT'",
                "feature": "WHERE 절 필터링"
            },
            {
                "name": "ORDER BY 정렬",
                "query": f"SELECT name, salary FROM `{index_name}` ORDER BY salary DESC LIMIT 5",
                "feature": "ORDER BY 정렬"
            },
            {
                "name": "LIMIT 제한",
                "query": f"SELECT name, department FROM `{index_name}` LIMIT 3",
                "feature": "LIMIT 결과 제한"
            }
        ]
        
        for test in basic_queries:
            success, _ = self.execute_sql_query(test["query"], test["name"])
            if success:
                results["기본기능"].append(test["feature"])
                results["테스트결과"][test["name"]] = "성공"
            else:
                results["테스트결과"][test["name"]] = "실패"
        
        return results

    def test_aggregation_functions(self, index_name):
        """집계 함수 테스트"""
        print("\n=== 📊 집계 함수 테스트 ===")
        
        results = {"집계기능": [], "테스트결과": {}}
        
        aggregation_queries = [
            {
                "name": "COUNT 함수",
                "query": f"SELECT COUNT(*) as total_employees FROM `{index_name}`",
                "feature": "COUNT(*) 총 개수"
            },
            {
                "name": "AVG 함수",
                "query": f"SELECT AVG(salary) as average_salary FROM `{index_name}`",
                "feature": "AVG() 평균값"
            },
            {
                "name": "MAX/MIN 함수",
                "query": f"SELECT MAX(salary) as max_salary, MIN(salary) as min_salary FROM `{index_name}`",
                "feature": "MAX(), MIN() 최대/최소값"
            },
            {
                "name": "SUM 함수",
                "query": f"SELECT SUM(salary) as total_salary FROM `{index_name}`",
                "feature": "SUM() 합계"
            },
            {
                "name": "GROUP BY",
                "query": f"SELECT department, COUNT(*) as emp_count, AVG(salary) as avg_salary FROM `{index_name}` GROUP BY department",
                "feature": "GROUP BY 그룹화"
            },
            {
                "name": "HAVING 절",
                "query": f"SELECT department, COUNT(*) as count FROM `{index_name}` GROUP BY department HAVING COUNT(*) > 1",
                "feature": "HAVING 그룹 조건"
            }
        ]
        
        for test in aggregation_queries:
            success, _ = self.execute_sql_query(test["query"], test["name"])
            if success:
                results["집계기능"].append(test["feature"])
                results["테스트결과"][test["name"]] = "성공"
            else:
                results["테스트결과"][test["name"]] = "실패"
        
        return results

    def test_advanced_sql_features(self, index_name):
        """고급 SQL 기능 테스트"""
        print("\n=== 🔥 고급 SQL 기능 테스트 ===")
        
        results = {"고급기능": [], "테스트결과": {}}
        
        advanced_queries = [
            {
                "name": "CASE WHEN 조건문",
                "query": f"""
                SELECT name, salary,
                       CASE 
                           WHEN salary >= 6000 THEN '고급'
                           WHEN salary >= 5000 THEN '중급'
                           ELSE '초급'
                       END as salary_grade
                FROM `{index_name}`
                ORDER BY salary DESC
                """,
                "feature": "CASE WHEN 조건부 분류"
            },
            {
                "name": "서브쿼리",
                "query": f"""
                SELECT name, salary, department
                FROM `{index_name}`
                WHERE salary > (SELECT AVG(salary) FROM `{index_name}`)
                ORDER BY salary DESC
                """,
                "feature": "서브쿼리 (Subquery)"
            },
            {
                "name": "다중 조건 WHERE",
                "query": f"""
                SELECT name, department, salary, age
                FROM `{index_name}`
                WHERE salary >= 5000 AND age < 35 AND department IN ('IT', 'Finance')
                """,
                "feature": "복합 WHERE 조건 (AND, IN)"
            },
            {
                "name": "LIKE 패턴 검색",
                "query": f"""
                SELECT name, email
                FROM `{index_name}`
                WHERE email LIKE '%company.com'
                """,
                "feature": "LIKE 패턴 매칭"
            },
            {
                "name": "날짜 함수",
                "query": f"""
                SELECT name, hire_date,
                       DATE_FORMAT(hire_date, 'yyyy') as hire_year,
                       DATE_FORMAT(hire_date, 'MM') as hire_month
                FROM `{index_name}`
                ORDER BY hire_date DESC
                """,
                "feature": "DATE_FORMAT 날짜 포맷"
            },
            {
                "name": "ROUND 함수",
                "query": f"""
                SELECT department,
                       COUNT(*) as employee_count,
                       ROUND(AVG(salary), 0) as avg_salary,
                       ROUND(AVG(performance_score), 2) as avg_performance
                FROM `{index_name}`
                GROUP BY department
                """,
                "feature": "ROUND 반올림 함수"
            }
        ]
        
        for test in advanced_queries:
            success, _ = self.execute_sql_query(test["query"], test["name"])
            if success:
                results["고급기능"].append(test["feature"])
                results["테스트결과"][test["name"]] = "성공"
            else:
                results["테스트결과"][test["name"]] = "실패"
        
        return results

    def test_business_analysis_queries(self, index_name):
        """비즈니스 분석용 쿼리 테스트"""
        print("\n=== 💼 비즈니스 분석 쿼리 테스트 ===")
        
        results = {"분석기능": [], "테스트결과": {}}
        
        business_queries = [
            {
                "name": "부서별 인력 현황",
                "query": f"""
                SELECT department,
                       COUNT(*) as headcount,
                       ROUND(AVG(age), 1) as avg_age,
                       ROUND(AVG(salary), 0) as avg_salary,
                       ROUND(AVG(performance_score), 2) as avg_performance
                FROM `{index_name}`
                GROUP BY department
                ORDER BY headcount DESC
                """,
                "feature": "부서별 종합 분석"
            },
            {
                "name": "연봉 구간별 분포",
                "query": f"""
                SELECT 
                    CASE 
                        WHEN salary >= 6000 THEN '6000만원 이상'
                        WHEN salary >= 5000 THEN '5000-6000만원'
                        WHEN salary >= 4000 THEN '4000-5000만원'
                        ELSE '4000만원 미만'
                    END as salary_range,
                    COUNT(*) as employee_count,
                    ROUND(AVG(performance_score), 2) as avg_performance
                FROM `{index_name}`
                GROUP BY salary_range
                ORDER BY MIN(salary) DESC
                """,
                "feature": "연봉 구간별 성과 분석"
            },
            {
                "name": "입사년도별 트렌드",
                "query": f"""
                SELECT 
                    DATE_FORMAT(hire_date, 'yyyy') as hire_year,
                    COUNT(*) as new_hires,
                    ROUND(AVG(salary), 0) as avg_starting_salary
                FROM `{index_name}`
                GROUP BY DATE_FORMAT(hire_date, 'yyyy')
                ORDER BY hire_year DESC
                """,
                "feature": "입사 트렌드 분석"
            },
            {
                "name": "고성과자 식별",
                "query": f"""
                SELECT name, department, position, salary, performance_score
                FROM `{index_name}`
                WHERE performance_score >= 4.5
                ORDER BY performance_score DESC, salary DESC
                """,
                "feature": "고성과자 조회"
            },
            {
                "name": "부서별 성과 순위",
                "query": f"""
                SELECT department,
                       ROUND(AVG(performance_score), 2) as avg_performance,
                       COUNT(*) as team_size,
                       ROUND(AVG(salary), 0) as avg_salary
                FROM `{index_name}`
                GROUP BY department
                ORDER BY avg_performance DESC
                """,
                "feature": "부서 성과 랭킹"
            }
        ]
        
        for test in business_queries:
            success, _ = self.execute_sql_query(test["query"], test["name"])
            if success:
                results["분석기능"].append(test["feature"])
                results["테스트결과"][test["name"]] = "성공"
            else:
                results["테스트결과"][test["name"]] = "실패"
        
        return results

    def test_ppl_queries(self, index_name):
        """PPL (Piped Processing Language) 테스트"""
        print("\n=== 🔄 PPL (Piped Processing Language) 테스트 ===")
        
        results = {"PPL기능": [], "테스트결과": {}}
        
        try:
            # PPL 쿼리 예시
            ppl_queries = [
                {
                    "name": "기본 PPL 검색",
                    "query": "search source=sql-test-employees | fields name, department, salary | head 5"
                },
                {
                    "name": "PPL 필터링", 
                    "query": "search source=sql-test-employees | where department='IT' | fields name, position, salary"
                }
            ]
            
            for test in ppl_queries:
                try:
                    print(f"\n🔍 {test['name']}")
                    print(f"   PPL: {test['query'].strip()}")
                    
                    response = requests.post(
                        f"{self.base_url}/_plugins/_sql",
                        auth=self.auth,
                        headers={"Content-Type": "application/json"},
                        data=json.dumps({"query": test["query"]}),
                        verify=False
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ PPL 실행 성공")
                        
                        if 'datarows' in result and result['datarows']:
                            print(f"   📊 결과: {len(result['datarows'])}행")
                            # 첫 번째 결과만 표시
                            if result['datarows']:
                                print(f"      샘플: {result['datarows'][0]}")
                        
                        results["PPL기능"].append(test["feature"])
                        results["테스트결과"][test["name"]] = "성공"
                    else:
                        print(f"   ❌ PPL 실행 실패: {response.status_code}")
                        results["테스트결과"][test["name"]] = "실패"
                        
                except Exception as e:
                    print(f"   ❌ PPL 오류: {e}")
                    results["테스트결과"][test["name"]] = f"오류: {e}"
            
        except Exception as e:
            print(f"❌ PPL 전체 테스트 오류: {e}")
            results["테스트결과"]["PPL전체"] = f"오류: {e}"
        
        return results

    def run_sql_plugin_test(self):
        """SQL 플러그인 전체 테스트 실행"""
        print("🔍 OpenSearch SQL 플러그인 상세 테스트")
        print("=" * 60)
        
        if not self.test_connection():
            return
        
        # 테스트 데이터 생성
        index_name = self.create_test_data()
        
        # 각 기능별 테스트 실행
        all_results = {}
        
        # 기본 SQL 기능
        basic_results = self.test_basic_sql_features(index_name)
        all_results.update(basic_results)
        
        # 집계 함수
        agg_results = self.test_aggregation_functions(index_name)
        all_results.update(agg_results)
        
        # 고급 SQL 기능
        advanced_results = self.test_advanced_sql_features(index_name)
        all_results.update(advanced_results)
        
        # 비즈니스 분석
        business_results = self.test_business_analysis_queries(index_name)
        all_results.update(business_results)
        
        # PPL 테스트
        ppl_results = self.test_ppl_queries(index_name)
        all_results.update(ppl_results)
        
        # 결과 요약
        self.print_sql_summary(all_results)

    def print_sql_summary(self, results):
        """SQL 플러그인 테스트 결과 요약"""
        print("\n" + "="*70)
        print("📊 SQL 플러그인 테스트 결과 요약")
        print("="*70)
        
        # 모든 기능 수집
        all_features = []
        for key in ["기본기능", "집계기능", "고급기능", "분석기능", "PPL기능"]:
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
            elif "실패" in str(result):
                print(f"   ❌ {test_name}: {result}")
            else:
                print(f"   ⚠️ {test_name}: {result}")
        
        if total_count > 0:
            success_rate = (success_count / total_count) * 100
            print(f"\n📈 성공률: {success_rate:.1f}% ({success_count}/{total_count})")
        
        # 활용 방안
        print(f"\n💡 SQL 플러그인 활용 방안:")
        use_cases = [
            "기존 SQL 지식으로 OpenSearch 데이터 분석",
            "BI 도구 (Tableau, Power BI) 연동",
            "복잡한 집계 및 통계 분석",
            "실시간 대시보드용 쿼리 작성",
            "PPL로 로그 분석 파이프라인 구축",
            "데이터 과학자/분석가 친화적 인터페이스",
            "기존 SQL 스킬 재활용",
            "비개발자도 쉽게 데이터 조회",
            "복잡한 비즈니스 로직 구현",
            "OLAP 스타일 분석 쿼리"
        ]
        
        for i, use_case in enumerate(use_cases, 1):
            print(f"   {i:2d}. {use_case}")
        
        print(f"\n🌐 다음 단계:")
        print("   1. BI 도구와 JDBC 연결 테스트")
        print("   2. 복잡한 비즈니스 분석 쿼리 작성")
        print("   3. 실시간 대시보드용 쿼리 최적화")
        print("   4. PPL을 활용한 로그 분석 파이프라인 구축")
        
        print(f"\n💻 생성된 테스트 인덱스:")
        print("   • sql-test-employees: 직원 데이터 (10명)")

if __name__ == "__main__":
    tester = SQLPluginTester()
    tester.run_sql_plugin_test()