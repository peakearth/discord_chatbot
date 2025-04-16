-- 기본 메뉴 테이블
CREATE TABLE IF NOT EXISTS lunch_menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_name TEXT NOT NULL,
    category TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 음식점 정보 테이블
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    location TEXT,
    operating_hours TEXT,
    contact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 선호도 테이블
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    menu_id INTEGER,
    restaurant_id INTEGER,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (menu_id) REFERENCES lunch_menu(id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

-- 학식 메뉴 테이블
CREATE TABLE IF NOT EXISTS cafeteria_menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT NOT NULL,
    menu_type TEXT NOT NULL,
    menu_name TEXT NOT NULL,
    price INTEGER,
    menu_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 기존 메뉴 삭제 후 새로운 메뉴 구성
DELETE FROM lunch_menu;

-- 한식 메뉴
INSERT INTO lunch_menu (menu_name, category) VALUES
    ('김치볶음밥', '한식'),
    ('라면', '한식'),
    ('제육덮밥', '한식'),
    ('김밥', '한식'),
    ('떡볶이', '한식'),
    ('부대찌개', '한식'),
    ('참치마요덮밥', '한식'),
    ('치킨마요덮밥', '한식'),
    ('냉면', '한식'),
    ('비빔밥', '한식'),
    ('순두부찌개', '한식'),
    ('된장찌개', '한식'),
    ('김치찌개', '한식'),
    ('된장비빔밥', '한식'),
    ('김치볶음밥', '한식'),
    ('제육볶음', '한식'),
    ('불고기', '한식'),
    ('갈비탕', '한식'),
    ('돼지국밥', '한식'),
    ('순대', '한식'),
    ('컵밥', '한식');

-- 분식 메뉴
INSERT INTO lunch_menu (menu_name, category) VALUES
    ('라볶이', '분식'),
    ('떡볶이와 튀김', '분식'),
    ('김밥과 라면', '분식'),
    ('떡볶이와 순대', '분식'),
    ('김밥과 떡볶이', '분식'),
    ('라면과 만두', '분식');

-- 편의점 메뉴
INSERT INTO lunch_menu (menu_name, category) VALUES
    ('삼각김밥', '편의점'),
    ('도시락', '편의점'),
    ('샌드위치', '편의점'),
    ('컵라면', '편의점'),
    ('김밥도시락', '편의점'),
    ('샐러드', '편의점'),
    ('파스타', '편의점');

-- 패스트푸드
INSERT INTO lunch_menu (menu_name, category) VALUES
    ('햄버거', '패스트푸드'),
    ('치킨버거', '패스트푸드'),
    ('감자튀김', '패스트푸드'),
    ('치킨너겟', '패스트푸드'),
    ('피자', '패스트푸드'),
    ('서브웨이', '패스트푸드');

-- 간편식
INSERT INTO lunch_menu (menu_name, category) VALUES
    ('편의점 김밥', '간편식'),
    ('도시락', '간편식'),
    ('냉동식품', '간편식'),
    ('레토르트', '간편식');

-- 동아대 학식
INSERT INTO lunch_menu (menu_name, category) VALUES
    ('교수회관 학생식당', '학식'),
    ('중앙도서관 식당', '학식'),
    ('공대 1호관 먹방라운지', '학식');

-- 음식점 샘플 데이터 추가
INSERT INTO restaurants (name, category, location, operating_hours, contact) VALUES
    ('영진돼지국밥','한식','부산광역시 사하구 하신번영로157번길 37'),
    ('청송집', '한식', '부산광역시 사하구 하신번영로 432'),
    ('해주냉면', '한식 ', '부산광역시 사하구 낙동대로 324번길 5');