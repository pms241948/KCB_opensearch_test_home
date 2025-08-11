PS C:\Users\user\Desktop\opensearch-lab> python plugin_test_sql.py
🔍 OpenSearch SQL 플러그인 상세 테스트
============================================================
✅ OpenSearch 버전: 2.13.0

📊 테스트 데이터 생성 중...
   ✅ 직원 데이터 생성: 10명

=== 📋 기본 SQL 기능 테스트 ===

🔍 전체 데이터 조회
   SQL: SELECT * FROM `sql-test-employees` LIMIT 3
   ✅ 실행 성공
   📊 결과 (3행):
      performance_score | employee_id | name | hire_date | position | department | salary | age | email
      -------------------------------------------------------------------------------------------------
      4.5 | EMP001 | 김철수 | 2020-01-15 00:00:00 | 개발팀장 | IT | 7,000 | 35 | kim@company.com
      4.2 | EMP002 | 이영희 | 2019-03-10 00:00:00 | 인사과장 | HR | 6,500 | 32 | lee@company.com
      4.7 | EMP003 | 박민수 | 2021-06-01 00:00:00 | 시니어개발자 | IT | 6,000 | 29 | park@company.com

🔍 특정 컬럼 선택
   SQL: SELECT name, department, salary FROM `sql-test-employees` LIMIT 5
   ✅ 실행 성공
   📊 결과 (5행):
      name | department | salary
      --------------------------
      김철수 | IT | 7,000
      이영희 | HR | 6,500
      박민수 | IT | 6,000
      최은지 | Finance | 5,500
      정호영 | IT | 4,500

🔍 WHERE 조건 검색
   SQL: SELECT name, position, salary FROM `sql-test-employees` WHERE department = 'IT'
   ✅ 실행 성공
   📊 결과 (4행):
      name | position | salary
      ------------------------
      김철수 | 개발팀장 | 7,000
      박민수 | 시니어개발자 | 6,000
      정호영 | 주니어개발자 | 4,500
      윤태현 | 데이터엔지니어 | 6,200

🔍 ORDER BY 정렬
   SQL: SELECT name, salary FROM `sql-test-employees` ORDER BY salary DESC LIMIT 5
   ✅ 실행 성공
   📊 결과 (5행):
      name | salary
      -------------
      김철수 | 7,000
      이영희 | 6,500
      윤태현 | 6,200
      박민수 | 6,000
      강수정 | 5,800

🔍 LIMIT 제한
   SQL: SELECT name, department FROM `sql-test-employees` LIMIT 3
   ✅ 실행 성공
   📊 결과 (3행):
      name | department
      -----------------
      김철수 | IT
      이영희 | HR
      박민수 | IT

=== 📊 집계 함수 테스트 ===

🔍 COUNT 함수
   SQL: SELECT COUNT(*) as total_employees FROM `sql-test-employees`
   ✅ 실행 성공
   📊 결과 (1행):
      COUNT(*)
      --------
      10

🔍 AVG 함수
   SQL: SELECT AVG(salary) as average_salary FROM `sql-test-employees`
   ✅ 실행 성공
   📊 결과 (1행):
      AVG(salary)
      -----------
      5650.0

🔍 MAX/MIN 함수
   SQL: SELECT MAX(salary) as max_salary, MIN(salary) as min_salary FROM `sql-test-employees`
   ✅ 실행 성공
   📊 결과 (1행):
      MAX(salary) | MIN(salary)
      -------------------------
      7,000 | 4,500

🔍 SUM 함수
   SQL: SELECT SUM(salary) as total_salary FROM `sql-test-employees`
   ✅ 실행 성공
   📊 결과 (1행):
      SUM(salary)
      -----------
      56,500

🔍 GROUP BY
   SQL: SELECT department, COUNT(*) as emp_count, AVG(salary) as avg_salary FROM `sql-test-employees` GROUP BY department
   ✅ 실행 성공
   📊 결과 (4행):
      department | COUNT(*) | AVG(salary)
      -----------------------------------
      Finance | 2 | 5350.0
      HR | 2 | 5650.0
      IT | 4 | 5925.0
      Marketing | 2 | 5400.0

🔍 HAVING 절
   SQL: SELECT department, COUNT(*) as count FROM `sql-test-employees` GROUP BY department HAVING COUNT(*) > 1
   ✅ 실행 성공
   📊 결과 (4행):
      department | COUNT(*)
      ---------------------
      Finance | 2
      HR | 2
      IT | 4
      Marketing | 2

=== 🔥 고급 SQL 기능 테스트 ===

🔍 CASE WHEN 조건문
   SQL: SELECT name, salary,
                       CASE
                           WHEN salary >= 6000 THEN '고급'
                           WHEN salary >= 5000 THEN '중급'
                           ELSE '초급'
                       END as salary_grade
                FROM `sql-test-employees`
                ORDER BY salary DESC
   ✅ 실행 성공
   📊 결과 (10행):
      name | salary | CASE
                           WHEN salary >= 6000 THEN '고급'
                           WHEN salary >= 5000 THEN '중급'
                           ELSE '초급'
                       END
      -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      김철수 | 7,000 | 고급
      이영희 | 6,500 | 고급
      윤태현 | 6,200 | 고급
      박민수 | 6,000 | 고급
      강수정 | 5,800 | 중급
      ... 외 5행 더

🔍 서브쿼리
   SQL: SELECT name, salary, department
                FROM `sql-test-employees`
                WHERE salary > (SELECT AVG(salary) FROM `sql-test-employees`)
                ORDER BY salary DESC
   ❌ 실행 실패: 500
      오류: {
  "error": {
    "reason": "There was internal problem at backend",
    "details": "unsupported ex

🔍 다중 조건 WHERE
   SQL: SELECT name, department, salary, age
                FROM `sql-test-employees`
                WHERE salary >= 5000 AND age < 35 AND department IN ('IT', 'Finance')
   ✅ 실행 성공
   📊 결과 (4행):
      name | department | salary | age
      --------------------------------
      박민수 | IT | 6,000 | 29
      최은지 | Finance | 5,500 | 28
      윤태현 | IT | 6,200 | 33
      조성민 | Finance | 5,200 | 30

🔍 LIKE 패턴 검색
   SQL: SELECT name, email
                FROM `sql-test-employees`
                WHERE email LIKE '%company.com'
   ✅ 실행 성공
   📊 결과 (10행):
      name | email
      ------------
      김철수 | kim@company.com
      이영희 | lee@company.com
      박민수 | park@company.com
      최은지 | choi@company.com
      정호영 | jung@company.com
      ... 외 5행 더

🔍 날짜 함수
   SQL: SELECT name, hire_date,
                       DATE_FORMAT(hire_date, 'yyyy') as hire_year,
                       DATE_FORMAT(hire_date, 'MM') as hire_month
                FROM `sql-test-employees`
                ORDER BY hire_date DESC
   ✅ 실행 성공
   📊 결과 (10행):
      name | hire_date | DATE_FORMAT(hire_date, 'yyyy') | DATE_FORMAT(hire_date, 'MM')
      --------------------------------------------------------------------------------
      한미래 | 2023-05-20 00:00:00 | 2023 | 05
      정호영 | 2023-01-05 00:00:00 | 2023 | 01
      최은지 | 2022-09-20 00:00:00 | 2022 | 09
      임소영 | 2022-03-15 00:00:00 | 2022 | 03
      조성민 | 2021-12-01 00:00:00 | 2021 | 12
      ... 외 5행 더

🔍 ROUND 함수
   SQL: SELECT department,
                       COUNT(*) as employee_count,
                       ROUND(AVG(salary), 0) as avg_salary,
                       ROUND(AVG(performance_score), 2) as avg_performance
                FROM `sql-test-employees`
                GROUP BY department
   ✅ 실행 성공
   📊 결과 (4행):
      department | COUNT(*) | ROUND(AVG(salary), 0) | ROUND(AVG(performance_score), 2)
      --------------------------------------------------------------------------------
      Finance | 2 | 5350.0 | 4.0
      HR | 2 | 5650.0 | 4.2
      IT | 4 | 5925.0 | 4.4
      Marketing | 2 | 5400.0 | 4.3

=== 💼 비즈니스 분석 쿼리 테스트 ===

🔍 부서별 인력 현황
   SQL: SELECT department,
                       COUNT(*) as headcount,
                       ROUND(AVG(age), 1) as avg_age,
                       ROUND(AVG(salary), 0) as avg_salary,
                       ROUND(AVG(performance_score), 2) as avg_performance
                FROM `sql-test-employees`
                GROUP BY department
                ORDER BY headcount DESC
   ✅ 실행 성공
   📊 결과 (4행):
      department | COUNT(*) | ROUND(AVG(age), 1) | ROUND(AVG(salary), 0) | ROUND(AVG(performance_score), 2)
      -----------------------------------------------------------------------------------------------------
      IT | 4 | 30.8 | 5925.0 | 4.4
      Marketing | 2 | 28.0 | 5400.0 | 4.3
      Finance | 2 | 29.0 | 5350.0 | 4.0
      HR | 2 | 29.5 | 5650.0 | 4.2

🔍 연봉 구간별 분포
   SQL: SELECT
                    CASE
                        WHEN salary >= 6000 THEN '6000만원 이상'
                        WHEN salary >= 5000 THEN '5000-6000만원'
                        WHEN salary >= 4000 THEN '4000-5000만원'
                        ELSE '4000만원 미만'
                    END as salary_range,
                    COUNT(*) as employee_count,
                    ROUND(AVG(performance_score), 2) as avg_performance
                FROM `sql-test-employees`
                GROUP BY salary_range
                ORDER BY MIN(salary) DESC
   ✅ 실행 성공
   📊 결과 (3행):
      CASE
                        WHEN salary >= 6000 THEN '6000만원 이상'
                        WHEN salary >= 5000 THEN '5000-6000만원'
                        WHEN salary >= 4000 THEN '4000-5000만원'
                        ELSE '4000만원 미만'
                    END | COUNT(*) | ROUND(AVG(performance_score), 2)
      ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      6000만원 이상 | 4 | 4.5
      5000-6000만원 | 4 | 4.2
      4000-5000만원 | 2 | 4.0

🔍 입사년도별 트렌드
   SQL: SELECT
                    DATE_FORMAT(hire_date, 'yyyy') as hire_year,
                    COUNT(*) as new_hires,
                    ROUND(AVG(salary), 0) as avg_starting_salary
                FROM `sql-test-employees`
                GROUP BY DATE_FORMAT(hire_date, 'yyyy')
                ORDER BY hire_year DESC
   ✅ 실행 성공
   📊 결과 (5행):
      DATE_FORMAT(hire_date, 'yyyy') | COUNT(*) | ROUND(AVG(salary), 0)
      -----------------------------------------------------------------
      2023 | 2 | 4750.0
      2022 | 2 | 5150.0
      2021 | 3 | 5667.0
      2020 | 2 | 6600.0
      2019 | 1 | 6500.0

🔍 고성과자 식별
   SQL: SELECT name, department, position, salary, performance_score
                FROM `sql-test-employees`
                WHERE performance_score >= 4.5
                ORDER BY performance_score DESC, salary DESC
   ✅ 실행 성공
   📊 결과 (3행):
      name | department | position | salary | performance_score
      ---------------------------------------------------------
      박민수 | IT | 시니어개발자 | 6,000 | 4.7
      윤태현 | IT | 데이터엔지니어 | 6,200 | 4.6
      김철수 | IT | 개발팀장 | 7,000 | 4.5

🔍 부서별 성과 순위
   SQL: SELECT department,
                       ROUND(AVG(performance_score), 2) as avg_performance,
                       COUNT(*) as team_size,
                       ROUND(AVG(salary), 0) as avg_salary
                FROM `sql-test-employees`
                GROUP BY department
                ORDER BY avg_performance DESC
   ✅ 실행 성공
   📊 결과 (4행):
      department | ROUND(AVG(performance_score), 2) | COUNT(*) | ROUND(AVG(salary), 0)
      --------------------------------------------------------------------------------
      IT | 4.4 | 4 | 5925.0
      Marketing | 4.3 | 2 | 5400.0
      HR | 4.2 | 2 | 5650.0
      Finance | 4.0 | 2 | 5350.0

=== 🔄 PPL (Piped Processing Language) 테스트 ===

🔍 기본 PPL 검색
   PPL: search source=sql-test-employees | fields name, department, salary | head 5
   ❌ PPL 실행 실패: 400

🔍 PPL 필터링
   PPL: search source=sql-test-employees | where department='IT' | fields name, position, salary
   ❌ PPL 실행 실패: 400

======================================================================
📊 SQL 플러그인 테스트 결과 요약
======================================================================

🔧 지원 기능 (21개):
    1. SELECT * (전체 컬럼 조회)
    2. SELECT 특정 컬럼
    3. WHERE 절 필터링
    4. ORDER BY 정렬
    5. LIMIT 결과 제한
    6. COUNT(*) 총 개수
    7. AVG() 평균값
    8. MAX(), MIN() 최대/최소값
    9. SUM() 합계
   10. GROUP BY 그룹화
   11. HAVING 그룹 조건
   12. CASE WHEN 조건부 분류
   13. 복합 WHERE 조건 (AND, IN)
   14. LIKE 패턴 매칭
   15. DATE_FORMAT 날짜 포맷
   16. ROUND 반올림 함수
   17. 부서별 종합 분석
   18. 연봉 구간별 성과 분석
   19. 입사 트렌드 분석
   20. 고성과자 조회
   21. 부서 성과 랭킹

🧪 테스트 결과:
   ❌ 기본 PPL 검색: 실패
   ❌ PPL 필터링: 실패

📈 성공률: 0.0% (0/2)

💡 SQL 플러그인 활용 방안:
    1. 기존 SQL 지식으로 OpenSearch 데이터 분석
    2. BI 도구 (Tableau, Power BI) 연동
    3. 복잡한 집계 및 통계 분석
    4. 실시간 대시보드용 쿼리 작성
    5. PPL로 로그 분석 파이프라인 구축
    6. 데이터 과학자/분석가 친화적 인터페이스
    7. 기존 SQL 스킬 재활용
    8. 비개발자도 쉽게 데이터 조회
    9. 복잡한 비즈니스 로직 구현
   10. OLAP 스타일 분석 쿼리

🌐 다음 단계:
   1. BI 도구와 JDBC 연결 테스트
   2. 복잡한 비즈니스 분석 쿼리 작성
   3. 실시간 대시보드용 쿼리 최적화
   4. PPL을 활용한 로그 분석 파이프라인 구축

💻 생성된 테스트 인덱스:
   • sql-test-employees: 직원 데이터 (10명)