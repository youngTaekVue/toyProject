# 🚀 Integrated Monitoring Dashboard - Backend API Server

이 프로젝트는 요양기관 청구 오류 모니터링 대시보드, 헬스케어(Google Fit) 데이터 연동, 가계부(Python 이관 트랜잭션), 구글 캘린더, 기상청 날씨 및 버스 도착 실시간 정보 등 대시보드 애플리케이션의 핵심 API를 서빙하는 Node.js / Express 백엔드 서버입니다.

---

## 🏗️ 아키텍처 및 폴더 구조 (Route-Controller-Service)

코드의 가독성, 결합성 및 테스트 용이성을 극대화하기 위해 **레이어드 아키텍처(Layered Architecture)** 구조를 채택하여 코드를 분리했습니다.

```
backend/
├── app.js                  (Express 앱 초기화, 미들웨어 및 통합 라우터 마운트)
├── bin/
│   └── www                 (서버 구동 진입 스크립트: require("../app") 로드)
├── public/                 (정적 파일 호스팅 및 업로드된 엑셀 파일 저장소)
└── src/                    (메인 소스 코드)
    ├── config/             (데이터베이스 및 환경설정 공유 인스턴스)
    │   └── db.js           (MySQL/MariaDB Connection Pool 생성)
    ├── utils/              (좌표 변환 등 순수 수학 연산 헬퍼 모듈)
    │   └── geoConverter.js
    ├── routes/             (오직 API 진입 경로 매핑만 담당)
    │   ├── index.js        (통합 게이트웨이 엔트리 라우터)
    │   ├── errorStatistics.js
    │   ├── weather.js
    │   ├── python.js
    │   └── ... (도메인별 라우터)
    ├── controllers/        (HTTP 요청 가공, 파라미터 유효성 검증 및 응답 제어)
    │   └── errorStatisticsController.js
    └── services/           (순수 비즈니스 로직 연산, 엑셀 파일 파싱 및 조작)
        └── errorStatisticsService.js
```

---

## 🛠️ 핵심 도메인별 기능 목록 (API Endpoints)

### 1. 청구 실패 에러 통계 (Billing Error Statistics)
* **`GET /api/files`**: 업로드된 청구 에러 엑셀 파일 리스트 조회
* **`GET /api/errorStatistics/data/:fileKey`**: 특정 엑셀 파일 내 모든 시트 데이터 로드 및 파싱
* **`PUT /api/errorStatistics/status`**: 특정 실패 청구 건들의 상태(미확인 ➡️ 회신대기 ➡️ 최종완료) 변경 및 H열 동적 저장

### 2. 헬스케어 (Google Fit Integration)
* **`GET /health/google-fit/auth`**: 구글 핏 API 권한 부여 화면 리다이렉트
* **`GET /health/google-fit/callback`**: OAuth 2.0 인증 토큰 수신 콜백
* **`GET /health/google-fit/data`**: 최근 7일간의 누적 걸음수(com.google.step_count.delta) 집계 데이터 조회
* **`GET /health/google-fit/clear-tokens`**: 구글 핏 로그인 세션(토큰) 해제

### 3. 기상청 및 지리 정보 (Weather & Geocoding)
* **`POST /weather/dataList`**: 전달받은 위경도를 기상청 격자 좌표(NX, NY)로 변환 후 초단기예보/단기예보 조회
* **`GET /mapkey/getGMapKey`**: 구글 맵 Javascript SDK용 API Key 반환 (서버단 캐시 방지)
* **`GET /mapkey/getKakaoKey`**: 카카오맵 Javascript SDK용 App Key 반환

### 4. 대중교통 버스 정보 (Gyeonggi Bus API)
* **`GET /bus/stationList`**: 경기도 버스 정류소 명칭/번호 검색
* **`GET /bus/arrivalList`**: 특정 정류소의 실시간 버스 도착 정보 조회
* **`GET /bus/locationList`**: 노선 ID에 따른 실시간 버스 위치 정보 수집
* **`GET /bus/aroundStationList`**: 위경도 주변의 정류소 탐색

### 5. 구글 캘린더 (Google Calendar API)
* **`GET /calendar/api/events/:id`**: 특정 캘린더 ID(기본/공휴일 등)의 범위별 일정 이벤트 로드
* **`POST /calendar/api/insert`**: 캘린더에 신규 일정 추가 및 FullCalendar 호환 객체 응답

### 6. 자산 관리 원장 (Financial ledger)
* **`GET /python/transactions`**: DB 연동 가계부 거래 원장 전체 조회
* **`POST /python/transactions`**: 엑셀 업로드 트랜잭션 중복 검사 후 적재
* **`GET /python/categories`**: 카테고리 매핑 규칙 로드
* **`GET /python/financial_status/compare`**: 최신 snapshot과 이전 snapshot 간 자산 증감(Delta) 비교 분석
* **`GET /python/financial_treemap_data`**: ApexCharts Treemap에 적합한 자산/부채 계층 데이터 가공 서빙

---

## 🚀 기동 및 시작 방법

### 1. 패키지 설치
```sh
npm install
```
### 3. 서버 실행
```sh
npm start
```
서버는 기본적으로 **3000번 포트**에서 대기하며, 기동 시 MySQL 데이터베이스 연결 상태를 자동으로 확인합니다.
