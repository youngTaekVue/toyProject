# vuetify-project

Scaffolded with Vuetify CLI.

## ❗️ Documentation

- Primary docs: https://vuetifyjs.com/
- Getting started guide: https://vuetifyjs.com/en/getting-started/installation/
- Community support: https://community.vuetifyjs.com/
- Issue tracker: https://issues.vuetifyjs.com/

## 🧱 Stack

- Framework: Vue 3 + Vite
- UI Library: Vuetify
- Language: TypeScript
- Package manager: npm

## 🧭 Start Here

- Main entry: `src/main.ts`
- Main app component: `src/App.vue`
- Main styles: `src/styles/`
- Plugin setup: `src/plugins/`

## 📁 Project Structure

- `src/main.ts` — application entry point
- `src/App.vue` — root component
- `src/components/` — reusable Vue components
- `src/plugins/` — plugin registration and setup
- `src/styles/` — global styles and theme settings
- `public/` — static public files

## ✨ Enabled Features

- Base setup

## 💿 Install

Use your selected package manager (npm) to install dependencies:

```bash
npm install
```

## 🚀 Quick Start

```bash
npm install
npm run dev
```

## 🏗️ Build

```bash
npm run build
```

## 🧪 Available Scripts

- `npm run dev`
- `npm run build`
- `npm run preview`
- `npm run build-only`
- `npm run type-check`

## 💪 Support Vuetify Development

This project uses Vuetify - an MIT licensed Open Source project. We are glad to welcome contributors and any support for ongoing development:

- Contribute to Vuetify and ecosystem projects: https://github.com/vuetifyjs
- Request enterprise support: https://support.vuetifyjs.com/
- Sponsor on GitHub: https://github.com/sponsors/vuetifyjs
- Support on Open Collective: https://opencollective.com/vuetify

## 📱 Responsive Design Guidelines

### 1. 반응형 브레이크포인트 (Responsive Breakpoints)
화면 크기에 따라 스타일을 전환하는 기준점(해상도)입니다. (Tailwind CSS 등에서 표준으로 사용되는 기준)

- **sm (640px 이상)**: 모바일 가로 모드 및 소형 화면
- **md (768px 이상)**: 태블릿 (세로 모드)
- **lg (1024px 이상)**: 노트북 및 태블릿 (가로 모드)
- **xl (1280px 이상)**: 기본 데스크탑 모니터
- **2xl (1536px 이상)**: 대형 모니터 및 고해상도 디스플레이

### 2. 유연한 레이아웃 (Flexible Layouts)
다양한 화면 크기에 유연하게 배치되는 최신 CSS 레이아웃 방식입니다.

- **Flexbox**: 1차원 레이아웃 배치 구조 (`display: flex; flex-wrap: wrap; gap: 1rem;`)
- **Grid**: 2차원 격자 구조로, 컨테이너 너비에 따라 열의 개수가 자동으로 조절되도록 구성 (`grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));`)
- **Wrapping**: 내용이 넘칠 때 자연스럽게 다음 줄로 넘어가도록 설정 (`flex-wrap: wrap;`)

### 3. 반응형 타이포그래피 (Responsive Typography)
`text-sm`, `text-base`, `text-xl`처럼 고정 단위를 사용하는 방법도 있지만, 최근에는 `clamp()` 함수를 이용한 유동적 타이포그래피(Fluid Typography)를 권장합니다.

**예시**: `font-size: clamp(1rem, 2.5vw, 1.5rem);`

최소 크기(1rem), 화면 너비에 비례하는 크기(2.5vw), 최대 크기(1.5rem)를 지정하여 폰트 크기가 화면에 맞춰 부드럽게 변하도록 합니다.

### 4. 반응형 이미지 (Responsive Images)
- `max-width: 100%`: 이미지가 부모 컨테이너 너비를 초과하지 않고 비율에 맞춰 축소됩니다.
- `object-fit: cover`: 이미지 비율을 왜곡하지 않고, 지정된 영역을 꽉 채우도록 자동으로 크롭(잘라내기)합니다.
- `aspect-ratio: 16 / 9`: 화면 크기가 변해도 항상 일정한 종횡비(예: 16대 9)를 유지합니다.

### 5. 미디어 쿼리 (Media Queries)
특정 화면 조건에 맞는 CSS를 적용하는 문법입니다.

예시에서는 모바일 퍼스트 기준, `max-width: 768px` 미디어 쿼리를 사용하여 화면 너비가 768px 이하(모바일 환경)일 때 패딩을 줄이고 그리드를 1열(1fr)로 단일화하는 스타일을 보여줍니다.

### 6. 모바일 퍼스트 디자인 (Mobile-First Design)
가장 작은 모바일 화면의 스타일을 기본(Base)으로 먼저 설계한 후, 화면이 커짐에 따라 확장해 나가는 진보적 향상(Progressive Enhancement) 설계 방식입니다.

Base (모바일) ➔ md: (태블릿) ➔ lg: (노트북) ➔ xl: (데스크탑) 순서로 점진적으로 요소를 추가합니다.