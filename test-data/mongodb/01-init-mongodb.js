// OpenSearch 플러그인 테스트용 MongoDB 초기 데이터
// 금융 거래, 고객 정보, 시스템 로그 데이터

// 데이터베이스 생성 및 사용
db = db.getSiblingDB('opensearch_test');

// 1. 고객 정보 컬렉션
db.createCollection('customers');
db.customers.insertMany([
  {
    customer_id: "CUST001",
    name: "김철수",
    age: 35,
    income: 65000000,
    credit_score: 720,
    risk_level: "LOW",
    registration_date: new Date("2020-03-15"),
    last_transaction: new Date("2025-08-10"),
    total_transactions: 156,
    avg_transaction_amount: 125000,
    preferred_categories: ["온라인쇼핑", "음식점", "교통"],
    location: {
      city: "서울",
      district: "강남구",
      coordinates: [127.0276, 37.4979]
    }
  },
  {
    customer_id: "CUST002", 
    name: "이영희",
    age: 28,
    income: 45000000,
    credit_score: 680,
    risk_level: "MEDIUM",
    registration_date: new Date("2021-07-22"),
    last_transaction: new Date("2025-08-11"),
    total_transactions: 89,
    avg_transaction_amount: 85000,
    preferred_categories: ["온라인쇼핑", "뷰티", "카페"],
    location: {
      city: "서울",
      district: "서초구", 
      coordinates: [127.0324, 37.4837]
    }
  },
  {
    customer_id: "CUST003",
    name: "박민수",
    age: 42,
    income: 85000000,
    credit_score: 780,
    risk_level: "LOW",
    registration_date: new Date("2019-11-08"),
    last_transaction: new Date("2025-08-12"),
    total_transactions: 234,
    avg_transaction_amount: 180000,
    preferred_categories: ["주유소", "음식점", "온라인쇼핑"],
    location: {
      city: "서울",
      district: "송파구",
      coordinates: [127.1059, 37.5145]
    }
  },
  {
    customer_id: "CUST004",
    name: "정호영",
    age: 31,
    income: 38000000,
    credit_score: 620,
    risk_level: "HIGH",
    registration_date: new Date("2022-01-30"),
    last_transaction: new Date("2025-08-09"),
    total_transactions: 67,
    avg_transaction_amount: 95000,
    preferred_categories: ["온라인쇼핑", "게임", "음식점"],
    location: {
      city: "서울",
      district: "마포구",
      coordinates: [126.9087, 37.5636]
    }
  },
  {
    customer_id: "CUST005",
    name: "최수진",
    age: 39,
    income: 72000000,
    credit_score: 750,
    risk_level: "LOW",
    registration_date: new Date("2020-09-12"),
    last_transaction: new Date("2025-08-12"),
    total_transactions: 198,
    avg_transaction_amount: 145000,
    preferred_categories: ["뷰티", "음식점", "온라인쇼핑"],
    location: {
      city: "서울",
      district: "종로구",
      coordinates: [126.9780, 37.5735]
    }
  }
]);

// 2. 거래 내역 컬렉션
db.createCollection('transactions');
db.transactions.insertMany([
  {
    transaction_id: "TXN001",
    customer_id: "CUST001",
    amount: 150000,
    category: "온라인쇼핑",
    merchant: "쿠팡",
    timestamp: new Date("2025-08-12T10:30:00Z"),
    location: {
      city: "서울",
      district: "강남구",
      coordinates: [127.0276, 37.4979]
    },
    risk_score: 0.15,
    is_suspicious: false,
    payment_method: "신용카드",
    card_type: "VISA"
  },
  {
    transaction_id: "TXN002",
    customer_id: "CUST002", 
    amount: 85000,
    category: "음식점",
    merchant: "스타벅스 강남점",
    timestamp: new Date("2025-08-12T12:15:00Z"),
    location: {
      city: "서울",
      district: "강남구",
      coordinates: [127.0280, 37.4980]
    },
    risk_score: 0.08,
    is_suspicious: false,
    payment_method: "신용카드",
    card_type: "MASTER"
  },
  {
    transaction_id: "TXN003",
    customer_id: "CUST003",
    amount: 250000,
    category: "주유소",
    merchant: "SK에너지",
    timestamp: new Date("2025-08-12T14:45:00Z"),
    location: {
      city: "서울",
      district: "송파구",
      coordinates: [127.1060, 37.5146]
    },
    risk_score: 0.12,
    is_suspicious: false,
    payment_method: "신용카드",
    card_type: "VISA"
  },
  {
    transaction_id: "TXN004",
    customer_id: "CUST004",
    amount: 500000,
    category: "온라인쇼핑",
    merchant: "알 수 없는 판매자",
    timestamp: new Date("2025-08-12T02:30:00Z"),
    location: {
      city: "해외",
      district: "알 수 없음",
      coordinates: [0, 0]
    },
    risk_score: 0.85,
    is_suspicious: true,
    payment_method: "신용카드",
    card_type: "MASTER"
  },
  {
    transaction_id: "TXN005",
    customer_id: "CUST005",
    amount: 120000,
    category: "뷰티",
    merchant: "올리브영",
    timestamp: new Date("2025-08-12T16:20:00Z"),
    location: {
      city: "서울",
      district: "종로구",
      coordinates: [126.9781, 37.5736]
    },
    risk_score: 0.10,
    is_suspicious: false,
    payment_method: "신용카드",
    card_type: "VISA"
  }
]);

// 3. 시스템 로그 컬렉션
db.createCollection('system_logs');
db.system_logs.insertMany([
  {
    log_id: "LOG001",
    timestamp: new Date("2025-08-12T10:00:00Z"),
    level: "INFO",
    service: "transaction_service",
    message: "거래 처리 시작",
    details: {
      cpu_usage: 45.2,
      memory_usage: 67.8,
      response_time: 120,
      active_connections: 150
    }
  },
  {
    log_id: "LOG002",
    timestamp: new Date("2025-08-12T10:05:00Z"),
    level: "WARN",
    service: "fraud_detection",
    message: "의심스러운 거래 감지",
    details: {
      cpu_usage: 78.5,
      memory_usage: 82.3,
      response_time: 450,
      active_connections: 180
    }
  },
  {
    log_id: "LOG003",
    timestamp: new Date("2025-08-12T10:10:00Z"),
    level: "ERROR",
    service: "payment_gateway",
    message: "결제 게이트웨이 연결 실패",
    details: {
      cpu_usage: 95.1,
      memory_usage: 89.7,
      response_time: 1200,
      active_connections: 200
    }
  },
  {
    log_id: "LOG004",
    timestamp: new Date("2025-08-12T10:15:00Z"),
    level: "INFO",
    service: "user_authentication",
    message: "사용자 인증 성공",
    details: {
      cpu_usage: 52.3,
      memory_usage: 71.2,
      response_time: 180,
      active_connections: 165
    }
  },
  {
    log_id: "LOG005",
    timestamp: new Date("2025-08-12T10:20:00Z"),
    level: "INFO",
    service: "database_service",
    message: "데이터베이스 연결 정상",
    details: {
      cpu_usage: 48.7,
      memory_usage: 69.5,
      response_time: 95,
      active_connections: 140
    }
  }
]);

// 4. 인덱스 생성
db.customers.createIndex({ "customer_id": 1 });
db.customers.createIndex({ "risk_level": 1 });
db.customers.createIndex({ "location.coordinates": "2dsphere" });

db.transactions.createIndex({ "transaction_id": 1 });
db.transactions.createIndex({ "customer_id": 1 });
db.transactions.createIndex({ "timestamp": 1 });
db.transactions.createIndex({ "is_suspicious": 1 });
db.transactions.createIndex({ "location.coordinates": "2dsphere" });

db.system_logs.createIndex({ "timestamp": 1 });
db.system_logs.createIndex({ "level": 1 });
db.system_logs.createIndex({ "service": 1 });

print("MongoDB 초기 데이터 생성 완료!");
print("생성된 컬렉션:");
print("- customers: " + db.customers.countDocuments() + "개 문서");
print("- transactions: " + db.transactions.countDocuments() + "개 문서");
print("- system_logs: " + db.system_logs.countDocuments() + "개 문서");
