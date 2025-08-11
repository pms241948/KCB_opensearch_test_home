-- PostgreSQL 테스트 데이터 초기화
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    age INTEGER,
    city VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 샘플 데이터 삽입
INSERT INTO users (username, email, full_name, age, city) VALUES
('kim_chulsu', 'kim@kcb.co.kr', '김철수', 30, '서울'),
('lee_younghee', 'lee@kcb.co.kr', '이영희', 28, '부산'),
('park_minsu', 'park@kcb.co.kr', '박민수', 35, '대구'),
('choi_eunji', 'choi@kcb.co.kr', '최은지', 32, '인천'),
('jung_hoyoung', 'jung@kcb.co.kr', '정호영', 29, '광주');

-- 인덱스 생성
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);