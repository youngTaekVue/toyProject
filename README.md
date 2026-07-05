# Toy Project 모음

다양한 프론트엔드 기능 및 UI/UX 요소를 실험하고 구현한 토이 프로젝트 저장소입니다.

## 📁 프로젝트 구조 및 설명

| 디렉토리 | 분류 | 설명 |
| :--- | :--- | :--- |
| **dashboard** | 📊 대시보드 | 요양기관 청구 오류 및 에러 모니터링 시스템 (Vue 3 + Vite) |
| **backend** | 🖥️ 서버/API | 대시보드 및 각 토이 프로젝트용 Express API 백엔드 서버 |
| **001.swapSample** | ⚙️ UI/UX | 두 요소의 상태나 내용을 Swap/Toggle 하는 기능 예제 |
| **002.customElement** | 🌐 웹 표준 | Web Components를 활용한 사용자 정의 HTML 엘리먼트 구현 |
| **003.lazy-load-list** | ⚡ 성능 | 데이터 비동기 로드를 위한 무한 스크롤(Lazy Loading) 구현 |
| **004.thermometer** | 📊 시각화 | 아날로그 형태의 온도계 UI/UX 컴포넌트 |
| **005.calendar** | 📅 UI/UX | 날짜 선택 및 캘린더 기능 구현 |
| **006.weather** | 📡 API 연동 | 날씨 API 데이터를 활용한 날씨 위젯 데모 |
| **svgAnimation** | 🎨 애니메이션 | SVG를 활용한 동적 인터랙티브 애니메이션 예제 |

---

## 🚀 실행 및 시작 방법

### 1. 저장소 복제 및 이동
```bash
git clone <repository-url>
cd toyProject
```

### 2. 백엔드 API 서버 구동
```bash
cd backend
npm install
npm run dev # 또는 node server.js
```

### 3. 모니터링 대시보드 구동
```bash
cd ../dashboard
npm install
npm run dev
```