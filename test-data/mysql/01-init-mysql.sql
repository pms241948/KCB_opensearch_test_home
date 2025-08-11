-- MySQL 테스트 데이터 초기화
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(50),
    stock_quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 샘플 데이터 삽입
INSERT INTO products (name, price, category, stock_quantity) VALUES
('갤럭시 S24', 1200000.00, '전자제품', 50),
('아이폰 15', 1500000.00, '전자제품', 30),
('맥북 프로', 2500000.00, '전자제품', 20),
('나이키 운동화', 150000.00, '의류', 100),
('아디다스 후디', 80000.00, '의류', 75);

-- 인덱스 생성
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_price ON products(price);