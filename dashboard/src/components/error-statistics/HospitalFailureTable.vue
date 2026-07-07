<template>
  <v-card class="table-card hospital-card-fixed" elevation="0">
    <v-card-title class="d-flex justify-space-between align-center py-3 px-5 table-card-header flex-wrap gap-y-3">
      <div>
        <span class="table-card-title">요양기관별 실패 내역</span>
      </div>
      <div class="d-flex align-center flex-wrap" style="gap: 10px;">
        <!-- Custom Tab Group -->
        <div class="custom-tab-group">
          <button class="custom-tab-btn" :class="{ active: selectedStatusFilter === 'all' }" @click="selectedStatusFilterModel = 'all'">전체</button>
          <button class="custom-tab-btn" :class="{ active: selectedStatusFilter === 'active' }" @click="selectedStatusFilterModel = 'active'">미완료 건</button>
          <button class="custom-tab-btn" :class="{ active: selectedStatusFilter === 'resolved' }" @click="selectedStatusFilterModel = 'resolved'">최종 완료 건</button>
        </div>
        <!-- Search Input Box -->
        <div class="search-box">
          <div class="search-input-wrapper">
            <v-icon class="search-input-icon">mdi-magnify</v-icon>
            <input type="text" v-model="hospitalSearchModel" placeholder="요양기관명 검색..." class="sleek-search-input" />
          </div>
        </div>
        <!-- Settings button -->
        <button class="sleek-btn sleek-btn-info-outline" style="padding: 5px 10px;" @click.prevent="settingsDialog = true">
          ⚙️ 복사 설정
        </button>
      </div>
    </v-card-title>

    <div class="desktop-table-view">
      <v-table class="dashboard-table" style="table-layout: fixed;">
        <thead>
        <tr>
          <th class="text-center" style="width: 50px;">No</th>
          <th class="text-left cursor-pointer user-select-none" @click="$emit('sort', 'hospital')">
            요양기관명
            <v-icon size="x-small" :color="sortKey === 'hospital' ? 'blue-darken-2' : 'grey-lighten-1'">
              {{ sortKey === 'hospital' ? (sortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
            </v-icon>
          </th>
          <th class="text-right cursor-pointer user-select-none" @click="$emit('sort', 'count')" style="width: 90px;">
            실패 건수
            <v-icon size="x-small" :color="sortKey === 'count' ? 'blue-darken-2' : 'grey-lighten-1'">
              {{ sortKey === 'count' ? (sortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
            </v-icon>
          </th>
          <th class="text-right cursor-pointer user-select-none" @click="$emit('sort', 'resolutionRate')" style="width: 135px;">
            해결률
            <v-icon size="x-small" :color="sortKey === 'resolutionRate' ? 'blue-darken-2' : 'grey-lighten-1'">
              {{ sortKey === 'resolutionRate' ? (sortOrder === 'asc' ? 'mdi-arrow-up' : 'mdi-arrow-down') : 'mdi-swap-vertical' }}
            </v-icon>
          </th>
          <th class="text-center" style="width: 90px;">상태</th>
          <th class="text-center" style="width: 300px;">액션</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(item, idx) in paginatedHospitals" :key="item.hospital">
          <td class="text-center text-slate-400 font-weight-medium">{{ (hospitalPage - 1) * itemsPerPage + idx + 1 }}</td>
          <td class="text-left font-weight-medium text-slate-800 text-truncate" :title="item.hospital">{{ item.hospital }}</td>
          <td class="text-right font-weight-bold text-slate-700">
            {{ formatNumber(item.count) }}건 <span class="text-caption text-grey font-weight-medium">({{ formatNumber(item.casesCount) }}건)</span>
          </td>
          <td class="text-right">
            <div class="d-flex align-center justify-end">
              <span class="font-weight-bold mr-2.5 text-caption" :class="item.resolutionRate === 100 ? 'text-green' : 'text-orange'">{{ item.resolutionRate.toFixed(1) }}%</span>
              <div class="custom-progress-track">
                <div class="custom-progress-bar" :class="{ 'resolved': item.resolutionRate === 100 }" :style="{ width: item.resolutionRate + '%' }"></div>
              </div>
            </div>
          </td>
          <td class="text-center">
            <span class="custom-badge" :class="getHospitalStatusBadgeClass(item)">
              {{ getHospitalOverallState(item) }}
            </span>
          </td>
          <td class="text-center">
            <div class="d-flex align-center justify-center flex-wrap" style="gap: 6px;">
              <!-- 1. 상세보기 -->
              <button class="sleek-btn sleek-btn-primary-outline" @click.prevent="$emit('open-detail', item)">상세보기</button>

              <!-- 2. 내역 복사 -->
              <button class="sleek-btn sleek-btn-info-outline" @click.prevent="copyHospitalErrors(item)">
                📋 복사
              </button>

              <!-- 4. 상태 처리 -->
              <button class="sleek-btn" :class="getHospitalButtonClass(item)" @click.prevent="$emit('toggle-state', item)">
                {{ getHospitalButtonLabelFromItem(item) }}
              </button>
            </div>
          </td>
        </tr>
        <tr v-if="filteredHospitals.length === 0"><td colspan="6" class="text-center py-10 text-slate-400">데이터가 없습니다.</td></tr>
        </tbody>
      </v-table>
    </div>

    <!-- Mobile Card List View (Visible only on Mobile) -->
    <div class="mobile-card-list">
      <div v-for="(item, idx) in paginatedHospitals" :key="item.hospital" class="hospital-mobile-card mb-4 pa-4">
        <!-- No 영역 -->
        <div class="mb-3 d-flex align-center justify-space-between">
          <span class="mobile-card-no">#{{ (hospitalPage - 1) * itemsPerPage + idx + 1 }}</span>
        </div>

        <!-- 요양기관명 -->
        <div class="mb-3">
          <div class="mobile-field-label">요양기관명</div>
          <div class="mobile-field-value font-weight-bold text-slate-800">{{ item.hospital }}</div>
        </div>

        <!-- 실패 건수 -->
        <div class="mb-3">
          <div class="mobile-field-label">실패 건수</div>
          <div class="mobile-field-value font-weight-bold text-slate-700">
            {{ formatNumber(item.count) }}건 <span class="text-caption text-grey">({{ formatNumber(item.casesCount) }}건)</span>
          </div>
        </div>

        <!-- 해결률 -->
        <div class="mb-3">
          <div class="mobile-field-label">해결률</div>
          <div class="mobile-field-value d-flex align-center mt-1" style="gap: 8px;">
            <span class="font-weight-bold text-caption mr-1" :class="item.resolutionRate === 100 ? 'text-green' : 'text-orange'">
              {{ item.resolutionRate.toFixed(1) }}%
            </span>
            <div class="custom-progress-track" style="width: 100px;">
              <div class="custom-progress-bar" :class="{ 'resolved': item.resolutionRate === 100 }" :style="{ width: item.resolutionRate + '%' }"></div>
            </div>
          </div>
        </div>

        <!-- 상태 -->
        <div class="mb-3">
          <div class="mobile-field-label">상태</div>
          <div class="mobile-field-value mt-1">
            <span class="custom-badge" :class="getHospitalStatusBadgeClass(item)">
              {{ getHospitalOverallState(item) }}
            </span>
          </div>
        </div>

        <!-- 액션 -->
        <div class="mt-4 pt-3 border-t">
          <div class="mobile-field-label mb-2">액션</div>
          <div class="d-flex flex-wrap" style="gap: 8px;">
            <button class="sleek-btn sleek-btn-primary-outline flex-grow-1" style="flex: 1 1 45%;" @click.prevent="$emit('open-detail', item)">상세보기</button>

            <button class="sleek-btn sleek-btn-info-outline flex-grow-1" style="flex: 1 1 45%;" @click.prevent="copyHospitalErrors(item)">
              📋 복사
            </button>

            <button class="sleek-btn flex-grow-1" style="flex: 1 1 45%;" :class="getHospitalButtonClass(item)" @click.prevent="$emit('toggle-state', item)">
              {{ getHospitalButtonLabelFromItem(item) }}
            </button>
          </div>
        </div>
      </div>
      <div v-if="filteredHospitals.length === 0" class="text-center py-10 text-slate-400">데이터가 없습니다.</div>
    </div>

    <!-- Pagination -->
    <div class="custom-pagination border-t py-3" v-if="hospitalTotalPages > 1">
      <button class="pag-btn" :disabled="hospitalPage === 1" @click="hospitalPageModel = hospitalPage - 1">이전</button>
      <span class="pag-info">{{ hospitalPage }} / {{ hospitalTotalPages }}</span>
      <button class="pag-btn" :disabled="hospitalPage === hospitalTotalPages" @click="hospitalPageModel = hospitalPage + 1">다음</button>
    </div>

    <!-- 복사 문구 설정 모달 (UX/UI 프리미엄 보완) -->
    <v-dialog v-model="settingsDialog" max-width="600px" transition="dialog-bottom-transition">
      <v-card class="settings-dialog-card elevation-24">
        <!-- 모달 헤더 -->
        <v-card-title class="settings-dialog-header d-flex justify-space-between align-center">
          <div class="d-flex align-center gap-2">
            <v-icon color="primary" class="mr-2">mdi-cog-outline</v-icon>
            <span class="font-weight-bold text-slate-800 text-h6">복사 템플릿 & 지침 설정</span>
          </div>
          <v-btn icon="mdi-close" variant="text" size="small" color="slate-500" @click="settingsDialog = false"></v-btn>
        </v-card-title>

        <!-- 모달 안내 배너 -->
        <div class="settings-banner-info">
          <div class="banner-content d-flex align-start gap-2 text-caption">
            <v-icon color="blue" size="18" class="mr-1.5 mt-0.5">mdi-information-outline</v-icon>
            <div>
              각 요양기관의 <strong>[📋 복사]</strong> 버튼을 누를 때 생성되는 인사말과 지침을 커스텀합니다.<br>
              수정된 내용은 브라우저에 안전하게 보존되어 매번 재설정할 필요가 없습니다.
            </div>
          </div>
        </div>

        <!-- 모달 바디 -->
        <v-card-text class="settings-dialog-body" style="max-height: 480px; overflow-y: auto;">
          <!-- 0. 이메일 제목 템플릿 설정 -->
          <div class="settings-section">
            <div class="section-label-wrapper d-flex align-center justify-space-between" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <div class="d-flex align-center">
                <v-icon size="16" class="mr-1 text-slate-500">mdi-format-title</v-icon>
                <span class="section-label font-weight-bold">이메일 제목 템플릿</span>
              </div>
              <span class="text-caption text-slate-400">
                치환 키: <code>{요양기관명}</code>, <code>{차수}</code>
              </span>
            </div>
            <v-text-field
              v-model="emailTitleTemplate"
              variant="outlined"
              density="comfortable"
              hide-details
              placeholder="예: [청구실패오류] {요양기관명} 청구 보정 요청 건 ({차수})"
              class="sleek-text-field mb-2"
            ></v-text-field>
          </div>

          <!-- 1. 기본 고정 소개 문구 -->
          <div class="settings-section">
            <div class="section-label-wrapper d-flex align-center justify-space-between" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <div class="d-flex align-center">
                <v-icon size="16" class="mr-1 text-slate-500">mdi-card-text-outline</v-icon>
                <span class="section-label font-weight-bold">공통 소개글 (인사말)</span>
              </div>
              <!-- 간이 툴바 (굵게, 글자크기 연동) -->
              <div class="formatting-toolbar d-flex align-center" style="display: inline-flex; background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px; padding: 2px; gap: 2px;">
                <button type="button" class="toolbar-btn" title="굵게" @click="applyFormatToIntro('**', '**')">
                  <v-icon size="14">mdi-format-bold</v-icon>
                </button>
                <v-menu location="bottom end" transition="scale-transition">
                  <template v-slot:activator="{ props }">
                    <button type="button" class="toolbar-btn" title="글자 크기" v-bind="props">
                      <v-icon size="14">mdi-format-size</v-icon>
                    </button>
                  </template>
                  <v-list density="compact" class="toolbar-menu-list">
                    <v-list-item title="기본 (13px)" @click="applyFormatToIntro('[size=13]', '[/size]')" />
                    <v-list-item title="크게 (15px)" @click="applyFormatToIntro('[size=15]', '[/size]')" />
                    <v-list-item title="아주 크게 (18px)" @click="applyFormatToIntro('[size=18]', '[/size]')" />
                  </v-list>
                </v-menu>
              </div>
            </div>
            <v-textarea
              id="intro-textarea"
              v-model="introText"
              rows="2"
              variant="outlined"
              density="comfortable"
              hide-details
              placeholder="예: 아래 오류 내역을 원무 청구팀에 전달해 드립니다. 조치 지침에 따라 보정 부탁드립니다."
              class="sleek-textarea"
            ></v-textarea>
          </div>

          <!-- 2. 오류별 지침 개별 설정 -->
          <div class="settings-section mb-0">
            <div class="section-label-wrapper d-flex align-center">
              <v-icon size="16" class="mr-1 text-slate-500">mdi-clipboard-list-outline</v-icon>
              <span class="section-label font-weight-bold">오류 사유별 개별 지침</span>
            </div>
            <p class="text-caption text-slate-500 mb-3" style="line-height: 1.4;">
              💡 <strong>[해당사항없음]</strong>으로 입력된 카테고리는 복사 텍스트 내 조치 지침 가이드에서 아예 제외되어 깔끔하게 복사됩니다.
            </p>

            <div class="category-inputs-list">
              <div v-for="cat in uniqueCategories" :key="cat" class="category-setting-item">
                <div class="category-setting-header d-flex justify-space-between align-center">
                  <span class="category-name-tag text-slate-800 font-weight-bold">{{ cat }}</span>
                  <span
                    v-if="customInstructions[cat] === '해당사항없음'"
                    class="guide-badge badge-excluded"
                  >
                    가이드 제외됨
                  </span>
                  <span
                    v-else
                    class="guide-badge badge-included"
                  >
                    가이드 포함됨
                  </span>
                </div>
                <v-textarea
                  v-model="customInstructions[cat]"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  rows="1"
                  auto-grow
                  placeholder="예: '해당사항없음' 혹은 개별 조치 지침을 작성하세요."
                  class="sleek-textarea bg-white"
                  clearable
                ></v-textarea>
              </div>
            </div>
          </div>
        </v-card-text>

        <!-- 모달 푸터 -->
        <v-card-actions class="settings-dialog-footer">
          <v-btn class="modal-btn-cancel" @click="settingsDialog = false">취소</v-btn>
          <v-btn class="modal-btn-save" @click="saveSettings">
            <v-icon start class="mr-1">mdi-check</v-icon>
            설정 저장
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';

type RowState = '미확인' | '회신대기' | '최종완료';

const props = defineProps<{
  paginatedHospitals: any[];
  filteredHospitals: any[];
  hospitalPage: number;
  hospitalTotalPages: number;
  itemsPerPage: number;
  selectedStatusFilter: 'all' | 'active' | 'resolved';
  hospitalSearch: string;
  sortKey: string;
  sortOrder: 'asc' | 'desc';
  persistedStates: Record<string, RowState>;
  isLoading: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:hospitalPage', page: number): void;
  (e: 'update:selectedStatusFilter', filter: 'all' | 'active' | 'resolved'): void;
  (e: 'update:hospitalSearch', search: string): void;
  (e: 'sort', key: string): void;
  (e: 'open-detail', item: any): void;
  (e: 'toggle-state', item: any): void;
}>();

// Two-way bindings via computed getters/setters
const hospitalPageModel = computed({
  get: () => props.hospitalPage,
  set: (val) => emit('update:hospitalPage', val)
});

const selectedStatusFilterModel = computed({
  get: () => props.selectedStatusFilter,
  set: (val) => emit('update:selectedStatusFilter', val)
});

const hospitalSearchModel = computed({
  get: () => props.hospitalSearch,
  set: (val) => emit('update:hospitalSearch', val)
});

// Helper functions inside the component for clean layout
function getHospitalOverallState(item: any): RowState {
  if (!item || !item.cases) return '미확인';
  const states = item.cases.map((c: any) => props.persistedStates[c.key] || '미확인');
  if (states.includes('미확인')) return '미확인';
  if (states.includes('회신대기')) return '회신대기';
  return '최종완료';
}

function getHospitalStatusBadgeClass(item: any): string {
  const state = getHospitalOverallState(item);
  if (state === '미확인') return 'badge-unconfirmed';
  if (state === '회신대기') return 'badge-pending';
  return 'badge-resolved';
}

function getHospitalButtonLabelFromItem(item: any): string {
  const state = getHospitalOverallState(item);
  if (state === '미확인') return '회신대기 처리';
  if (state === '회신대기') return '최종완료 처리';
  return '미확인 초기화';
}

function getHospitalButtonClass(item: any): string {
  const state = getHospitalOverallState(item);
  if (state === '미확인') return 'sleek-btn-flat-success';
  if (state === '회신대기') return 'sleek-btn-flat-info';
  return 'sleek-btn-flat-warning';
}

function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num || 0);
}

// ==========================================================================
// 메일 전송 & 클립보드 복사 비즈니스 로직
// ==========================================================================

const settingsDialog = ref(false);
const introText = ref(localStorage.getItem('claim_intro_text') || '이메일 또는 메신저로 전달되는 자동화 문구입니다.');
const emailTitleTemplate = ref(localStorage.getItem('claim_title_template') || '[청구실패오류] {요양기관명} 청구 보정 요청 건 ({차수})');
const customInstructions = ref<Record<string, string>>(
  JSON.parse(localStorage.getItem('claim_custom_instructions') || '{}')
);

// 카테고리 명칭 공백/특수공백 정규화 헬퍼 함수
function normalizeCategoryName(cat: string | null | undefined): string {
  if (!cat) return '미분류';
  return cat.trim().replace(/\s+/g, ' ');
}

const uniqueCategories = computed(() => {
  const cats = new Set<string>();
  props.filteredHospitals.forEach(h => {
    if (h.cases) {
      h.cases.forEach((c: any) => {
        if (c.rows) {
          c.rows.forEach((r: any) => {
            if (r.category) {
              cats.add(normalizeCategoryName(r.category));
            }
          });
        }
      });
    }
  });
  return Array.from(cats);
});

// Reactivity 보장: uniqueCategories가 변경되면 customInstructions에 등록되지 않은 카테고리를 '해당사항없음'으로 사전 초기화
watch(uniqueCategories, (newCats) => {
  if (newCats) {
    newCats.forEach(cat => {
      const normCat = normalizeCategoryName(cat);
      if (customInstructions.value[normCat] === undefined || customInstructions.value[normCat] === null || customInstructions.value[normCat] === '') {
        customInstructions.value[normCat] = '해당사항없음';
      }
    });
  }
}, { immediate: true });

function saveSettings() {
  localStorage.setItem('claim_intro_text', introText.value);
  localStorage.setItem('claim_custom_instructions', JSON.stringify(customInstructions.value));
  localStorage.setItem('claim_title_template', emailTitleTemplate.value);
  settingsDialog.value = false;
  alert('설정이 저장되었습니다! 복사 시 반영됩니다.');
}

function applyFormatToIntro(before: string, after: string) {
  const el = document.getElementById('intro-textarea') as HTMLTextAreaElement;
  if (!el) return;
  const start = el.selectionStart;
  const end = el.selectionEnd;
  const text = introText.value || '';
  const selected = text.substring(start, end);
  const replacement = before + (selected || '텍스트') + after;
  introText.value = text.substring(0, start) + replacement + text.substring(end);

  // 포커싱 복구 및 포커싱 영역 재설정
  setTimeout(() => {
    el.focus();
    el.setSelectionRange(start + before.length, start + before.length + (selected || '텍스트').length);
  }, 50);
}

/**
 * 텍스트 내 줄바꿈(\n)을 HTML 개행(<br>)으로 치환하고,
 * 마크다운 굵은 글씨(**텍스트**) 및 글자크기 태그([size=15]텍스트[/size])를 HTML로 치환해주는 포맷터 함수
 */
function formatTextToHtml(text: string | null | undefined): string {
  if (!text) return '';
  let escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // **텍스트** -> <strong>텍스트</strong>
  escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // *텍스트* -> <em>텍스트</em>
  escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>');
  // [size=15]텍스트[/size] -> <span style="font-size: 15px;">텍스트</span>
  escaped = escaped.replace(/\[size=(\d+?)\](.*?)\[\/size\]/g, '<span style="font-size: $1px;">$2</span>');
  // 줄바꿈 -> <br>
  escaped = escaped.replace(/\n/g, '<br>');

  return escaped;
}

/**
 * 클립보드에 복사될 요양기관별 청구 실패 텍스트 및 HTML 포맷을 생성하는 헬퍼 함수
 * 💡 이 함수 내부의 문구(인사말, 고정 문구, 조치 가이드 등)를 수정하여 서식을 자유롭게 조절해 보세요!
 */
function appendApiSuffix(category: string, err?: any): string {
  const c = category || '';
  if (c.includes('/api/')) {
    return c;
  }
  if (err && err.api) {
    return `${c} (${err.api})`;
  }
  if (c.includes('영수증 조회')) {
    return c + ' (/api/get_medical_bill/v2)';
  }
  if (c.includes('진료비 영수증 목록 조회')) {
    return c + ' (/api/get_medical_bill_list/v2)';
  }
  if (c.includes('진료비 세부내역 조회')) {
    return c + ' (/api/get_medical_bill_detail/v2)';
  }
  if (c.includes('진료비 세부내역 항목별 내용 조회')) {
    return c + ' (/api/get_medical_bill_detail_list/v2)';
  }
  if (c.includes('원외처방전 조회')) {
    return c + ' (/api/get_prescription/v2)';
  }
  if (c.includes('원외 처방전 약품 목록 조회')) {
    return c + ' (/api/get_prescription_list/v2)';
  }
  if (c.includes('원외 처방전 질병분류 조회')) {
    return c + ' (/api/get_diagnosis_info/v2)';
  }
  return c;
}

/**
 * 클립보드에 복사될 요양기관별 청구 실패 텍스트 및 HTML 포맷을 생성하는 헬퍼 함수
 * 💡 이 함수 내부의 문구(인사말, 고정 문구, 조치 가이드 등)를 수정하여 서식을 자유롭게 조절해 보세요!
 */
function getClaimFailureReason(err: any): string {
  if (err.visitDate && err.visitDate !== '-' && err.uuid && err.uuid !== '-') {
    const categoryBase = err.category && err.category.includes('(') ? err.category.split('(')[0].trim() : (err.category || '');
    return `${categoryBase} (진료일자: ${err.visitDate.replace(/-/g, '')} / UUID: ${err.uuid}`;
  }
  return err.category || '-';
}

function formatClipboardText(hospital: string, institutionId: string, errors: any[]) {
  // 1. 중복 사유 추출
  const categories = Array.from(new Set(errors.map(e => normalizeCategoryName(e.category))));

  // 2. 오류 사유별 조치 지침 문구 매핑 함수 (필요에 따라 문구를 추가하거나 변경하세요)
  const getInstruction = (cat: string): string => {
    const normCat = normalizeCategoryName(cat);
    // 사용자 지정 지침 우선
    const custom = customInstructions.value[normCat];
    if (custom !== undefined && custom !== null && custom.trim() !== '') {
      return custom.trim();
    }
    // 기본 지침 매핑
    const c = normCat.toLowerCase();
    if (c.includes('진료 데이터') || c.includes('약품') || c.includes('조회 실패')) {
      return '의료기관 서버 혹은 위버케어 연동 모듈 장애가 감지되었습니다. EMR 약품 코드 세팅 상태 및 원외처방 데이터의 누락 여부를 확인하십시오.';
    } else if (c.includes('면허')) {
      return '청구 파일 내 의사면허번호 정보가 유실되었습니다. EMR 시스템 내 사용자 권한 설정에서 의사면허 등록 정보를 확인한 뒤 다시 저장해 주십시오.';
    } else if (c.includes('서식')) {
      return '심평원 고시 청구서 서식 표준과 상이합니다. EMR 소프트웨어가 최신 패치 버전을 사용하고 있는지 진단하십시오.';
    }
    return '원무 청구 화면에서 에러 코드를 대조한 뒤 적절한 상세 내역 보정을 진행해 주십시오.';
  };

  // ==========================================
  // [A] 일반 텍스트 (카카오톡, 메모장 등 붙여넣기용)
  // ==========================================
  let plain = `안녕하세요. ${hospital}입니다.\n\n`;
  plain += `[요양기관 청구 실패 내역 안내]\n`;

  // 일반 텍스트에서는 크기 태그 [size=...]를 제거하여 일반 글씨로 나오도록 처리
  const cleanIntro = (introText.value || '').replace(/\[size=\d+?\](.*?)\[\/size\]/g, '$1');
  plain += `${cleanIntro}\n\n`;

  plain += `■ ${hospital} - 청구 오류 내역 취합 현황\n\n`;

  categories.forEach((cat, catIdx) => {
    const catErrors = errors.filter(e => normalizeCategoryName(e.category) === cat);
    plain += `■ 청구실패 사유: ${appendApiSuffix(cat, catErrors[0])}\n`;
    plain += `No | 병원기관번호 | 병원명 | 병원EMR | 청구실패사유 | 진료내역\n`;
    plain += `------------------------------------------------------------\n`;
    catErrors.forEach((err, idx) => {
      const reasonVal = err.category && err.category.includes('(') ? err.category.split('(')[0].trim() : (err.category || '-');
      const detailsVal = (err.visitDate && err.visitDate !== '-' && err.uuid && err.uuid !== '-') 
        ? `(진료일자: ${err.visitDate.replace(/-/g, '')} / UUID: ${err.uuid}` 
        : (err.details || '-');
      if (idx > 0) {
        plain += `========================================================================\n`;
      }
      plain += `${idx + 1} | ${err.institutionId || '-'} | ${err.hospital || '-'} | ${err.emr || '-'} | ${reasonVal} | ${detailsVal}\n`;
    });
    plain += `------------------------------------------------------------\n\n`;
  });

  // 텍스트 버전 조치 지침 구성 (해당사항없음 제외)
  let plainInstructions = '';
  categories.forEach(cat => {
    const inst = getInstruction(cat);
    if (inst !== '해당사항없음') {
      const cleanInst = inst.replace(/\[size=\d+?\](.*?)\[\/size\]/g, '$1');
      const catErrors = errors.filter(e => normalizeCategoryName(e.category) === cat);
      plainInstructions += `- ${appendApiSuffix(cat, catErrors[0])}: ${cleanInst}\n`;
    }
  });

  if (plainInstructions) {
    plain += `[오류별 조치 요령 안내]\n` + plainInstructions + `\n`;
  }

  plain += `감사합니다.\n`;

  // ==========================================
  // [B] Rich HTML (Gmail, Outlook, Naver 메일, Word 등 붙여넣기용)
  // ==========================================
  let htmlTables = '';
  categories.forEach((cat, catIdx) => {
    const catErrors = errors.filter(e => normalizeCategoryName(e.category) === cat);
    const htmlRows = catErrors.map((err, idx) => {
      const reasonVal = err.category && err.category.includes('(') ? err.category.split('(')[0].trim() : (err.category || '-');
      const detailsVal = (err.visitDate && err.visitDate !== '-' && err.uuid && err.uuid !== '-') 
        ? `(진료일자: ${err.visitDate.replace(/-/g, '')} / UUID: ${err.uuid}` 
        : (err.details || '-');
      const separator = idx > 0 ? `
      <tr style="height: 20px;">
        <td colspan="6" style="border: none; text-align: center; color: #a6a6a6; font-size: 11px; padding: 4px 0;">
          ========================================================================
        </td>
      </tr>
      ` : '';
      return separator + `
      <tr style="height: 25px;">
        <td style="border: 1px solid #d9d9d9; padding: 4px 6px; text-align: center; color: #333;">${idx + 1}</td>
        <td style="border: 1px solid #d9d9d9; padding: 4px 6px; text-align: center; color: #333;">${err.institutionId || '-'}</td>
        <td style="border: 1px solid #d9d9d9; padding: 4px 6px; text-align: left; color: #333;">${err.hospital || '-'}</td>
        <td style="border: 1px solid #d9d9d9; padding: 4px 6px; text-align: center; color: #333;">${err.emr || '-'}</td>
        <td style="border: 1px solid #d9d9d9; padding: 4px 6px; text-align: left; color: #333;">${reasonVal}</td>
        <td style="border: 1px solid #d9d9d9; padding: 4px 6px; text-align: left; color: #333;">${detailsVal}</td>
      </tr>
      `;
    }).join('');

    htmlTables += `
  <div style="margin-top: 20px; margin-bottom: 8px; font-size: 14px; font-weight: bold; color: #1f4e78;">
    ■ 청구실패 사유: ${appendApiSuffix(cat, catErrors[0])}
  </div>
  <table style="width: 70%; border-collapse: collapse; border: 1.5px solid #1f4e78; margin-bottom: 20px; font-size: 11px;">
    <thead>
      <tr style="background-color: #1f4e78; color: #ffffff; height: 28px; font-weight: bold;">
        <th style="border: 1px solid #a6a6a6; padding: 5px; width: 40px; text-align: center;">No</th>
        <th style="border: 1px solid #a6a6a6; padding: 5px; width: 90px; text-align: center;">병원기관번호</th>
        <th style="border: 1px solid #a6a6a6; padding: 5px; width: 160px; text-align: center;">병원명</th>
        <th style="border: 1px solid #a6a6a6; padding: 5px; width: 90px; text-align: center;">병원EMR</th>
        <th style="border: 1px solid #a6a6a6; padding: 5px; width: 320px; text-align: center;">청구실패사유</th>
        <th style="border: 1px solid #a6a6a6; padding: 5px; width: 520px; text-align: center;">진료내역 (진료일자 및 UUID)</th>
      </tr>
    </thead>
    <tbody>
      ${htmlRows}
    </tbody>
  </table>
  `;
  });

  // 오류별 지침 HTML 리스트 (해당사항없음 제외)
  const guidelinesHtml = categories
    .map(cat => {
      const inst = getInstruction(cat);
      if (inst === '해당사항없음') return '';
      const catErrors = errors.filter(e => normalizeCategoryName(e.category) === cat);
      return `
    <li style="margin-bottom: 6px;">
      <strong>${appendApiSuffix(cat, catErrors[0])}</strong><br> ${formatTextToHtml(inst)}
    </li>`;
    })
    .filter(Boolean)
    .join('');

  let htmlGuidesSection = '';
  if (guidelinesHtml) {
    htmlGuidesSection = `
  <div style="background-color: #f2f5f8; width: 70%; border-left: 4px solid #1f4e78; padding: 12px 16px; margin: 20px 0; border-radius: 4px; font-size: 12px;">
        <ul style="margin: 0; padding-left: 18px; color: #444;">
      ${guidelinesHtml}
    </ul>
  </div>
  `;
  }

  let html = `<div style="font-family: '맑은 고딕', 'Malgun Gothic', sans-serif; font-size: 13px; line-height: 1.6; color: #333;">`;
  html += `<p>${formatTextToHtml(introText.value)}</p>`;
  html += htmlGuidesSection;
  html += `<div style="margin-top: 25px; margin-bottom: 5px; font-size: 16px; font-weight: bold; color: #002060;">`;
  html += `  ■ ${hospital} - 청구 오류 내역 취합 현황`;
  html += `</div>`;

  html += htmlTables;

  html += `<p style="margin-top: 20px;">처리되시면 회신 부탁드립니다.<br>감사합니다.</p>`;
  html += `</div>`;

  return { plain, html };
}

function copyHospitalErrors(item: any) {
  const institutionId = item.cases[0]?.institutionId || '-';
  const errors = item.cases.flatMap((c: any) => c.rows || []);

  const content = formatClipboardText(item.hospital, institutionId, errors);

  // 클립보드 아이템 생성 (Text와 HTML을 모두 제공하여 붙여넣는 앱에 맞춰 스마트하게 복사되도록 함)
  const textBlob = new Blob([content.plain], { type: 'text/plain' });
  const htmlBlob = new Blob([content.html], { type: 'text/html' });

  const clipboardItem = new ClipboardItem({
    'text/plain': textBlob,
    'text/html': htmlBlob
  });

  navigator.clipboard.write([clipboardItem])
    .then(() => {
      alert(`${item.hospital}의 오류 내역(${errors.length}건)이 클립보드에 복사되었습니다!\n\n💡 메일(Naver/Outlook/Gmail 등)이나 슬랙/워드에 붙여넣기(Ctrl+V) 하시면 실제 엑셀 표 서식 그대로 정렬되어 붙여넣어집니다.`);
    })
    .catch(err => {
      console.error("Rich HTML 클립보드 복사 실패. 일반 텍스트로 대체 시도:", err);
      // fallback
      navigator.clipboard.writeText(content.plain)
        .then(() => {
          alert(`${item.hospital}의 오류 내역(${errors.length}건)이 일반 텍스트 포맷으로 클립보드에 복사되었습니다.`);
        })
        .catch(e => {
          console.error("클립보드 복사 최종 실패:", e);
          alert("클립보드 복사에 실패했습니다.");
        });
    });
}
</script>

<style scoped>
.table-card {
  background: #ffffff;
  border-radius: 9px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}
.table-card-title { font-size: 14px; font-weight: 800; color: #0f172a; }
.table-card-header { border-bottom: 1px solid #f1f5f9; background-color: #ffffff; }

/* search-box */
.search-box { width: 180px; }
.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}
.search-input-icon {
  position: absolute;
  left: 10px;
  color: #94a3b8;
  font-size: 16px !important;
  pointer-events: none;
}
.sleek-search-input {
  width: 100%;
  height: 32px;
  box-sizing: border-box;
  padding: 6px 10px 6px 32px;
  font-size: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background-color: #f8fafc;
  color: #334155;
  outline: none;
  transition: border-color 0.2s, background-color 0.2s, box-shadow 0.2s;
}
.sleek-search-input:focus {
  border-color: #3b82f6;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.08);
}

/* custom-tab-group */
.custom-tab-group {
  display: flex;
  background-color: #f1f5f9;
  padding: 3px;
  border-radius: 8px;
  gap: 2px;
  height: 32px;
  box-sizing: border-box;
  align-items: center;
}
.custom-tab-btn {
  border: none;
  background: transparent;
  padding: 0 12px;
  height: 100%;
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  outline: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}
.custom-tab-btn.active {
  background-color: #ffffff;
  color: #2563eb;
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* table and progress */
.dashboard-table {
  width: 100%;
  border-collapse: collapse;
}
.dashboard-table :deep(th) {
  background-color: #f8fafc !important;
  color: #475569 !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  padding: 12px 14px !important;
  border-bottom: 1px solid #e2e8f0 !important;
  white-space: nowrap !important;
}
.dashboard-table :deep(td) {
  padding: 12px 14px !important;
  font-size: 12.5px !important;
  color: #334155 !important;
  border-bottom: 1px solid #f0f0f0 !important;
  height: auto !important;
  min-height: 52px !important;
  vertical-align: middle !important;
}
.dashboard-table :deep(tr) {
  height: auto !important;
}
.dashboard-table :deep(tr:hover) { background-color: #f8fafc !important; }
.custom-progress-track {
  width: 50px;
  height: 6px;
  background-color: #f1f5f9;
  border-radius: 100px;
  overflow: hidden;
  position: relative;
  display: inline-block;
}
.custom-progress-bar {
  height: 100%;
  background-color: #f59e0b; /* default orange */
  border-radius: 100px;
  transition: width 0.4s ease;
}
.custom-progress-bar.resolved {
  background-color: #10b981; /* green */
}

/* custom-badge for status */
.custom-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 700;
  border-radius: 4px;
  line-height: 1;
  white-space: nowrap;
}
.badge-unconfirmed {
  background-color: #f1f5f9;
  color: #64748b;
}
.badge-pending {
  background-color: #fffbeb;
  color: #d97706;
}
.badge-resolved {
  background-color: #ecfdf5;
  color: #059669;
}

/* sleek-btn */
.sleek-btn {
  border: 1px solid transparent;
  background-color: #f1f5f9;
  color: #475569;
  font-size: 11px;
  font-weight: 700;
  padding: 5px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  white-space: nowrap;
}
.sleek-btn-primary-outline {
  border-color: #e2e8f0;
  background-color: #ffffff;
  color: #0284c7;
}
.sleek-btn-primary-outline:hover {
  background-color: #f0f9ff;
  border-color: #0284c7;
}
.sleek-btn-info-outline {
  border-color: #e2e8f0;
  background-color: #ffffff;
  color: #475569;
}
.sleek-btn-info-outline:hover {
  background-color: #f1f5f9;
  border-color: #64748b;
}

.sleek-btn-flat-success {
  background-color: #ecfdf5;
  color: #059669;
  border-color: rgba(16, 185, 129, 0.05);
}
.sleek-btn-flat-success:hover {
  background-color: #d1fae5;
}
.sleek-btn-flat-warning {
  background-color: #fff1f2;
  color: #e11d48;
  border-color: rgba(225, 29, 72, 0.05);
}
.sleek-btn-flat-warning:hover {
  background-color: #ffe4e6;
}
.sleek-btn-flat-info {
  background-color: #f0f9ff;
  color: #0284c7;
  border-color: rgba(2, 132, 199, 0.05);
}
.sleek-btn-flat-info:hover {
  background-color: #e0f2fe;
}

/* custom-pagination */
.custom-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
.pag-btn {
  border: 1px solid #e2e8f0;
  background-color: #ffffff;
  color: #475569;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}
.pag-btn:hover:not(:disabled) {
  background-color: #f8fafc;
  color: #0f172a;
  border-color: #cbd5e1;
}
.pag-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.pag-info {
  font-size: 11.5px;
  font-weight: 700;
  color: #64748b;
}

.hospital-card-fixed {
  height: 650px;
  display: flex;
  flex-direction: column;
}
.hospital-card-fixed :deep(.v-table) {
  flex: 1 1 auto;
}
.hospital-card-fixed :deep(.v-table__wrapper) {
  flex: 1 1 auto;
}

.text-green { color: #10b981 !important; }
.text-orange { color: #f59e0b !important; }
.cursor-pointer { cursor: pointer; }
.user-select-none { user-select: none; }

/* Responsive View Toggle */
@media (min-width: 768px) {
  .mobile-card-list {
    display: none !important;
  }
}
@media (max-width: 767px) {
  .desktop-table-view {
    display: none !important;
  }
  .hospital-card-fixed {
    height: auto !important;
  }
}

.hospital-mobile-card {
  background-color: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 9px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
  transition: all 0.2s ease;
}
.hospital-mobile-card:active {
  transform: translateY(1px);
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.02);
}
.mobile-card-no {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  background-color: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
}
.mobile-field-label {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  margin-bottom: 2px;
}
.mobile-field-value {
  font-size: 13.5px;
  color: #0f172a;
}
.border-t {
  border-top: 1px solid rgba(15, 23, 42, 0.08);
}
.pa-4 {
  padding: 16px !important;
}
.mb-4 {
  margin-bottom: 16px !important;
}
.mb-3 {
  margin-bottom: 12px !important;
}
.mt-4 {
  margin-top: 16px !important;
}
.pt-3 {
  padding-top: 12px !important;
}
.mr-1 {
  margin-right: 4px !important;
}
.d-flex {
  display: flex !important;
}
.align-center {
  align-items: center !important;
}
.justify-space-between {
  justify-content: space-between !important;
}
.flex-grow-1 {
  flex-grow: 1 !important;
}

/* 복사 문구 설정 모달 UX/UI 개선 */
.settings-dialog-card {
  border-radius: 9px !important;
  border: 1px solid #cbd5e1 !important;
  background: #ffffff !important;
  overflow: hidden;
}
.settings-dialog-header {
  border-bottom: 1px solid #f1f5f9;
  padding: 16px 24px !important;
}
.settings-banner-info {
  background-color: #fafbfd;
  padding: 12px 24px !important;
  border-bottom: 1px solid #f1f5f9;
}
.banner-content {
  background-color: #eff6ff;
  color: #1e40af;
  border-radius: 8px;
  padding: 12px;
}
.settings-dialog-body {
  background-color: #ffffff;
  padding: 20px 24px !important;
}

/* Custom Scrollbar for sleek UI */
.settings-dialog-body::-webkit-scrollbar {
  width: 6px;
}
.settings-dialog-body::-webkit-scrollbar-track {
  background: #f8fafc;
}
.settings-dialog-body::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
.settings-dialog-body::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Section styling */
.settings-section {
  margin-bottom: 24px;
}
.settings-section.mb-0 {
  margin-bottom: 0px;
}
.section-label-wrapper {
  margin-bottom: 8px;
}
.section-label {
  color: #334155;
  font-size: 13.5px;
}

/* Category Item styling */
.category-setting-item {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
  padding: 14px !important;
  border-radius: 8px;
  margin-bottom: 14px;
}
.category-setting-item:last-child {
  margin-bottom: 0;
}
.category-setting-item:focus-within {
  border-color: #2563eb !important;
  background-color: #ffffff !important;
  box-shadow: 0 4px 12px -2px rgba(37, 99, 235, 0.08);
}
.category-setting-header {
  margin-bottom: 8px;
}
.category-name-tag {
  color: #1e293b;
  font-size: 13px;
  word-break: break-all;
}

/* Guide status badges */
.guide-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 8px;
  font-size: 10px;
  font-weight: 700;
  border-radius: 4px;
  line-height: 1;
  white-space: nowrap;
}
.guide-badge.badge-excluded {
  background-color: #f1f5f9;
  color: #64748b;
  border: 1px solid #cbd5e1;
}
.guide-badge.badge-included {
  background-color: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

/* Formatting Toolbar */
.formatting-toolbar {
  display: inline-flex;
  background-color: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 2px;
  gap: 2px;
}
.toolbar-btn {
  background: transparent;
  border: none;
  color: #475569;
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}
.toolbar-btn:hover {
  background-color: #e2e8f0;
  color: #0f172a;
}
.toolbar-menu-list {
  background-color: #ffffff !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: 6px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  padding: 4px 0 !important;
}
.toolbar-menu-list :deep(.v-list-item) {
  min-height: 28px !important;
  padding: 4px 12px !important;
  font-size: 12px !important;
}

/* Sleek inputs overrides */
.sleek-textarea :deep(.v-field__outline),
.sleek-text-field :deep(.v-field__outline) {
  --v-field-border-opacity: 0.15;
  border-color: #cbd5e1;
}
.sleek-textarea :deep(.v-field--focused .v-field__outline),
.sleek-text-field :deep(.v-field--focused .v-field__outline) {
  --v-field-border-opacity: 1;
  color: #2563eb;
}
.sleek-textarea, .sleek-text-field {
  font-size: 13px !important;
}

/* Footer & Buttons */
.settings-dialog-footer {
  background-color: #f8fafc;
  border-top: 1px solid #f1f5f9;
  padding: 12px 24px !important;
  display: flex !important;
  justify-content: flex-end !important;
  gap: 8px !important;
  box-sizing: border-box;
}
.modal-btn-cancel {
  border: 1px solid #cbd5e1 !important;
  background-color: #ffffff !important;
  color: #475569 !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  height: 34px !important;
  padding: 0 16px !important;
  border-radius: 6px !important;
  text-transform: none !important;
  box-shadow: none !important;
  transition: all 0.2s;
  letter-spacing: normal !important;
}
.modal-btn-cancel:hover {
  background-color: #f1f5f9 !important;
  border-color: #94a3b8 !important;
}
.modal-btn-save {
  background-color: #2563eb !important;
  color: #ffffff !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  height: 34px !important;
  padding: 0 16px !important;
  border-radius: 6px !important;
  text-transform: none !important;
  box-shadow: none !important;
  transition: all 0.2s;
  letter-spacing: normal !important;
}
.modal-btn-save:hover {
  background-color: #1d4ed8 !important;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
}
</style>
