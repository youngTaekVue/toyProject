# 요양기관 청구 오류 모니터링 대시보드 (Frontend)

요양기관의 청구 오류 내역과 실시간 에러 로그를 관제하고 조치 상태를 관리하는 모니터링 대시보드 화면입니다.

## 🛠 기술 스택
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **Language**: TypeScript
- **UI Library**: Vuetify 3 (커스텀 스타일 적용)

---

## 🎨 주요 디자인 및 레이아웃 특징

1. **화면 레이아웃 & 패딩 일관성**
   - 대시보드 메인 화면과 상세 화면의 패딩(`pt-3 px-4 pb-8`) 및 여백 구조를 일치시켜 화면 전환 시 이질감이 없도록 개선했습니다.
   - 브라우저 해상도를 100% 활용하는 Fluid 레이아웃을 채택하여 대형 모니터에서도 시각적으로 쾌적하게 정보를 전달합니다.

2. **그리드 대칭 정렬**
   - **차트 영역**: 트렌드 혼합 차트(`TrendMixedChart`)와 에러 TOP 5 차트(`TopErrorsChart`)의 카드 높이를 `350px`로 동일하게 맞춰 좌우 균형을 이루도록 설계했습니다.
   - **테이블 영역**: 요양기관 테이블(`HospitalFailureTable`)과 EMR사 테이블(`EmrVendorFailureTable`)을 `650px` 고정 높이로 설정하여 수평 수직 정렬을 맞췄습니다.
   - **파일 테이블 독립**: 첨부 파일별 통계 테이블(`AttachedFileFailureTable`)을 하단에 단독 배치하여 좌우 균형이 흐트러지지 않도록 조정했습니다.

3. **커스텀 UI 컴포넌트**
   - Vuetify의 기본 스타일 대신 가볍고 모던한 느낌의 `custom-badge`와 `sleek-btn` 스타일을 적용했습니다.
   - 검색창은 통일된 `sleek-search-input`을 사용하여 심플한 룩을 제공합니다.


## 🚀 실행 방법

### 1. 의존성 패키지 설치
```bash
npm install
```

### 2. 환경 변수 설정
`dashboard` 폴더 루트에 `.env` 파일을 생성하고 API 서버 주소를 입력합니다.
```env
VITE_API_BASE_URL=http://localhost:3000
```

### 3. 로컬 개발 서버 실행
```bash
npm run dev
```

### 4. 프로덕션 빌드
```bash
npm run build
```
빌드 성공 시 `dist/` 폴더에 정적 배포용 번들이 생성됩니다.