<template>
  <div class="dashboard-wrapper">
    <v-container fluid class="error-monitor-section pt-3 px-4 pb-8">
      
      <!-- 상단 헤더 & 차수 선택 -->
      <div class="d-flex align-center justify-space-between mb-6 mt-1 flex-wrap gap-y-3">
        <div>
          <h2 class="text-subtitle-1 font-weight-bold text-slate-800 mb-0 d-flex align-center">
            <v-icon color="primary" class="mr-2" size="small">mdi-email-send-outline</v-icon>
            메일 자동 발송기 (Mail Dispatcher)
          </h2>
          <p class="text-caption text-slate-500 mb-0 mt-0.5">
            오류 데이터를 선택 취합하여 간편하게 클립보드 복사할 수 있는 발송 보조 시스템입니다.
          </p>
        </div>
        <div class="d-flex align-center">
          <span class="text-caption font-weight-bold text-slate-600 mr-2.5 text-no-wrap">데이터 차수 선택:</span>
          <select v-model="selectedFileKey" class="sleek-select">
            <option v-for="opt in fileOptions" :key="opt.value" :value="opt.value">
              {{ opt.title }}
            </option>
          </select>
        </div>
      </div>

      <!-- 발송 기본 설정 카드 (고정 참조 및 제목 템플릿) -->
      <v-card class="table-card pa-5 mb-6" elevation="0">
        <div class="d-flex align-center mb-4 pb-2 border-b">
          <v-icon color="blue" class="mr-2">mdi-cog-outline</v-icon>
          <span class="font-weight-bold text-slate-800" style="font-size: 15px;">이메일 발송 기본 설정</span>
        </div>
        
        <v-row>
          <v-col cols="12" md="4">
            <div class="field-label mb-2">공통 참조 이메일 (CC)</div>
            <input type="text" v-model="fixedCc" placeholder="예: admin@company.com" class="sleek-input" />
            <p class="text-caption text-slate-400 mt-1">
              쉼표(,)로 구분하여 여러 명의 참조자를 지정할 수 있습니다.
            </p>
          </v-col>

          <v-col cols="12" md="4">
            <div class="field-label mb-2">공통 이메일 제목 템플릿</div>
            <input type="text" v-model="titleTemplate" placeholder="예: [안내] {요양기관명} 청구오류 보정 요청" class="sleek-input" />
            <p class="text-caption text-slate-400 mt-1" style="line-height: 1.3;">
              치환 키: <code>{요양기관명}</code>, <code>{차수}</code>
            </p>
          </v-col>

          <v-col cols="12" md="4">
            <div class="field-label mb-2">발송 방식 안내</div>
            <div class="info-alert-box d-flex align-start bg-blue-light" style="padding: 10px 14px;">
              <v-icon color="blue-darken-2" class="mr-2 mt-0.5" size="small">mdi-information-outline</v-icon>
              <div class="text-caption text-slate-700" style="line-height: 1.45;">
                원하는 항목을 선택하면 이메일 제목/내용이 자동 완성됩니다. **[📧 메일 작성]** 버튼 클릭 시 클립보드에 Rich 표 서식이 복사되고 복사 가이드 창이 열립니다.
              </div>
            </div>
          </v-col>
        </v-row>
      </v-card>

      <!-- 탭 컨트롤 (요양기관별 각각 발송 vs EMR사별 취합 발송) -->
      <div class="custom-nav-tabs mb-4">
        <button class="nav-tab-btn" :class="{ active: activeTab === 'hospital' }" @click="activeTab = 'hospital'">
          <v-icon class="mr-1">mdi-hospital-building</v-icon> 요양기관별 각각 발송
        </button>
        <button class="nav-tab-btn" :class="{ active: activeTab === 'emr' }" @click="activeTab = 'emr'">
          <v-icon class="mr-1">mdi-desktop-mac</v-icon> EMR사별 취합 발송
        </button>
      </div>

      <!-- [탭 1] 요양기관별 각각 발송 -->
      <div v-show="activeTab === 'hospital'">
        <v-card class="table-card" elevation="0">
          <v-card-title class="d-flex justify-space-between align-center py-3 px-5 table-card-header flex-wrap gap-y-3">
            <div class="d-flex align-center" style="gap: 8px;">
              <span class="table-card-title mr-2">요양기관별 에러 내역 리스트</span>
              <v-btn 
                v-if="selectedHospitalNames.length > 0"
                color="success" 
                variant="flat" 
                density="comfortable"
                class="font-weight-bold text-none px-3" 
                style="border-radius: 8px; font-size: 12px; height: 34px; letter-spacing: -0.2px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"
                prepend-icon="mdi-email-send-outline"
                @click="sendBatchToNaverDebugPort('naver')"
              >
                선택 전송 (네이버: {{ selectedHospitalNames.length }}건)
              </v-btn>
              <v-btn 
                v-if="selectedHospitalNames.length > 0"
                color="info" 
                variant="flat" 
                density="comfortable"
                class="font-weight-bold text-none px-3" 
                style="border-radius: 8px; font-size: 12px; height: 34px; letter-spacing: -0.2px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"
                prepend-icon="mdi-email-send-outline"
                @click="sendBatchToNaverDebugPort('hiworks')"
              >
                선택 전송 (하이웍스: {{ selectedHospitalNames.length }}건)
              </v-btn>
              <v-btn 
                v-if="selectedHospitalNames.length > 0"
                color="warning" 
                variant="flat" 
                density="comfortable"
                class="font-weight-bold text-none px-3" 
                style="border-radius: 8px; font-size: 12px; height: 34px; letter-spacing: -0.2px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"
                prepend-icon="mdi-email-send-outline"
                @click="sendBatchToNaverDebugPort('other')"
              >
                선택 전송 (기타: {{ selectedHospitalNames.length }}건)
              </v-btn>
            </div>
            <div class="d-flex align-center gap-2">
              <div class="search-box">
                <div class="search-input-wrapper">
                  <v-icon class="search-input-icon">mdi-magnify</v-icon>
                  <input type="text" v-model="hospitalSearch" placeholder="요양기관명 검색..." class="sleek-search-input" />
                </div>
              </div>
            </div>
          </v-card-title>

          <v-table class="dashboard-table">
            <thead>
              <tr>
                <th class="text-center" style="width: 50px;">
                  <input 
                    type="checkbox" 
                    :checked="isAllHospitalsSelected" 
                    @change="toggleAllHospitalsSelection" 
                    class="custom-checkbox"
                  />
                </th>
                <th class="text-center" style="width: 60px;">No</th>
                <th class="text-left" style="width: 250px;">요양기관명</th>
                <th class="text-center" style="width: 100px;">EMR사</th>
                <th class="text-right" style="width: 100px;">오류 건수</th>
                <th class="text-left" style="width: 280px;">수신 이메일 주소</th>
                <th class="text-center" style="width: 180px;">액션</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in filteredHospitals" :key="item.hospital">
                <td class="text-center">
                  <input 
                    type="checkbox" 
                    :value="item.hospital" 
                    v-model="selectedHospitalNames" 
                    class="custom-checkbox"
                  />
                </td>
                <td class="text-center text-slate-400">{{ idx + 1 }}</td>
                <td class="text-left font-weight-medium text-slate-800">{{ item.hospital }}</td>
                <td class="text-center">
                  <span :class="['emr-tag-badge', getEmrClass(item.emr)]">{{ item.emr }}</span>
                </td>
                <td class="text-right font-weight-bold text-red">{{ item.count }}건</td>
                <td class="text-left">
                  <input 
                    type="text" 
                    v-model="hospitalEmails[item.hospital]" 
                    @change="saveHospitalEmails" 
                    placeholder="이메일을 입력하세요..." 
                    class="table-cell-input"
                  />
                </td>
                <td class="text-center">
                  <button class="sleek-btn sleek-btn-primary-outline" @click="openHospitalMailSetup(item)">
                    <v-icon start size="x-small" class="mr-1">mdi-email-edit-outline</v-icon>
                    메일 작성
                  </button>
                </td>
              </tr>
              <tr v-if="filteredHospitals.length === 0">
                <td colspan="7" class="text-center py-10 text-slate-400">조회된 데이터가 없습니다.</td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </div>

      <!-- [탭 2] EMR사별 취합 발송 -->
      <div v-show="activeTab === 'emr'">
        <v-card class="table-card" elevation="0">
          <v-card-title class="py-3 px-5 table-card-header">
            <span class="table-card-title">EMR사별 취합 오류 리스트</span>
          </v-card-title>

          <v-table class="dashboard-table">
            <thead>
              <tr>
                <th class="text-center" style="width: 60px;">No</th>
                <th class="text-left" style="width: 150px;">EMR 개발사</th>
                <th class="text-left" style="width: 350px;">대상 요양기관 목록</th>
                <th class="text-right" style="width: 120px;">총 오류 건수</th>
                <th class="text-left" style="width: 280px;">EMR사 담당 이메일</th>
                <th class="text-center" style="width: 180px;">액션</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in emrSummary" :key="item.emr">
                <td class="text-center text-slate-400">{{ idx + 1 }}</td>
                <td class="text-left font-weight-bold text-slate-800">{{ item.emr }}</td>
                <td class="text-left text-slate-600 text-truncate" :title="item.hospitals.join(', ')">
                  {{ item.hospitals.join(', ') }}
                </td>
                <td class="text-right font-weight-bold text-red">{{ item.totalCount }}건</td>
                <td class="text-left">
                  <input 
                    type="text" 
                    v-model="emrEmails[item.emr]" 
                    @change="saveEmrEmails" 
                    placeholder="EMR사 담당 이메일 입력..." 
                    class="table-cell-input"
                  />
                </td>
                <td class="text-center">
                  <button class="sleek-btn sleek-btn-info-outline" @click="openEmrMailSetup(item)">
                    <v-icon start size="x-small" class="mr-1">mdi-folder-swap-outline</v-icon>
                    취합 및 편집 발송
                  </button>
                </td>
              </tr>
              <tr v-if="emrSummary.length === 0">
                <td colspan="6" class="text-center py-10 text-slate-400">조회된 데이터가 없습니다.</td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </div>

      <!-- [모달 1] 요양기관별 메일 세부 편집 및 복사 도우미 -->
      <v-dialog v-model="hospitalSetupDialog" max-width="1200px" persistent>
        <v-card class="copy-helper-card" elevation="24">
          <div class="copy-helper-header d-flex align-center">
            <v-icon color="primary" class="mr-2" size="large">mdi-email-edit-outline</v-icon>
            <span class="font-weight-bold text-slate-800" style="font-size: 16px;">요양기관별 오류 메일 복사 도우미</span>
            <v-spacer></v-spacer>
            <v-btn icon="mdi-close" variant="text" size="small" color="slate-400" @click="hospitalSetupDialog = false"></v-btn>
          </div>

          <div class="copy-helper-body pa-0">
            <v-row no-gutters>
              <!-- 좌측: 오류 카테고리별 필터링 ("넣을꺼 넣고 뺄꺼 빼고") -->
              <v-col cols="12" md="4" class="border-r pa-4 d-flex flex-column" style="max-height: 600px; background-color: #fafbfd;">
                <div class="d-flex align-center justify-space-between mb-3">
                  <span class="font-weight-bold text-slate-700" style="font-size: 13.5px;">📋 에러 항목 선택 ({{ selectedCategories.length }}/{{ currentHospitalCategories.length }})</span>
                  <div class="d-flex gap-1">
                    <button class="mini-text-btn" @click="selectAllHospitalCategories">전체 선택</button>
                    <span class="text-slate-300">|</span>
                    <button class="mini-text-btn" @click="deselectAllHospitalCategories">전체 해제</button>
                  </div>
                </div>

                <div class="error-selection-list flex-grow-1" style="overflow-y: auto;">
                  <div 
                    v-for="cat in currentHospitalCategories" 
                    :key="cat.name" 
                    class="error-select-card"
                    :class="{ active: selectedCategories.includes(cat.name) }"
                    @click="toggleCategorySelection(cat.name)"
                  >
                    <div class="d-flex align-center">
                      <input 
                        type="checkbox" 
                        :checked="selectedCategories.includes(cat.name)" 
                        @click.stop 
                        @change="toggleCategorySelection(cat.name)"
                        class="mr-3 cursor-pointer"
                      />
                      <div class="flex-grow-1" style="min-width: 0;">
                        <div class="d-flex justify-space-between align-center">
                          <span 
                            class="font-weight-bold text-slate-800 text-truncate" 
                            style="font-size: 13px; line-height: 1.35; max-width: 200px; display: inline-block;"
                            :title="cat.name"
                          >
                            {{ cat.name }}
                          </span>
                          <span class="error-count-tag">{{ cat.count }}건</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </v-col>

              <!-- 우측: 메일 양식 정보 및 HTML 미리보기 -->
              <v-col cols="12" md="8" class="pa-5 d-flex flex-column" style="max-height: 600px; overflow-y: auto; background-color: #ffffff; border-left: 1px solid #f1f5f9;">
                <div class="d-flex align-center mb-4 pb-2" style="border-bottom: 1.5px solid #eceff1;">
                  <v-icon color="indigo-darken-2" class="mr-2" size="20">mdi-email-send-outline</v-icon>
                  <span class="font-weight-bold text-slate-800" style="font-size: 14.5px; letter-spacing: -0.4px;">발송 정보 & 클립보드 도우미</span>
                </div>

                <!-- 받는 사람 -->
                <div class="mb-4">
                  <div class="field-title mb-1">
                    <v-icon size="15" class="mr-1 text-indigo-accent-3">mdi-account-arrow-right-outline</v-icon>
                    <span>받는 사람 (To)</span>
                  </div>
                  <div class="sleek-input-group">
                    <input type="text" v-model="hospitalSetupData.to" class="helper-read-input flex-grow-1" placeholder="수신 메일 주소" />
                    <button class="input-inline-btn" title="받는사람 복사" @click="copyText(hospitalSetupData.to, '받는 사람 주소가')">
                      <v-icon size="17">mdi-content-copy</v-icon>
                    </button>
                  </div>
                </div>

                <!-- 참조자 -->
                <div class="mb-4">
                  <div class="field-title mb-1">
                    <v-icon size="15" class="mr-1 text-indigo-accent-3">mdi-account-multiple-outline</v-icon>
                    <span>참조자 (CC)</span>
                  </div>
                  <div class="sleek-input-group">
                    <input type="text" v-model="hospitalSetupData.cc" class="helper-read-input flex-grow-1" placeholder="참조 메일 주소" />
                    <button class="input-inline-btn" title="참조자 복사" @click="copyText(hospitalSetupData.cc, '참조 주소가')">
                      <v-icon size="17">mdi-content-copy</v-icon>
                    </button>
                  </div>
                </div>

                <!-- 제목 -->
                <div class="mb-4">
                  <div class="field-title mb-1">
                    <v-icon size="15" class="mr-1 text-indigo-accent-3">mdi-bookmark-outline</v-icon>
                    <span>이메일 제목</span>
                  </div>
                  <div class="sleek-input-group">
                    <input type="text" v-model="hospitalSetupData.subject" class="helper-read-input flex-grow-1 font-weight-bold" placeholder="메일 제목" style="color: #3b82f6 !important;" />
                    <button class="input-inline-btn" title="제목 복사" @click="copyText(hospitalSetupData.subject, '이메일 제목이')">
                      <v-icon size="17">mdi-content-copy</v-icon>
                    </button>
                  </div>
                </div>

                <!-- 본문 헤더 및 복사 버튼 -->
                <div class="mb-2 d-flex align-center justify-space-between mt-2">
                  <div class="field-title">
                    <v-icon size="15" class="mr-1 text-slate-500">mdi-file-document-edit-outline</v-icon>
                    <span style="color: #64748b;">메일 본문 서식 미리보기</span>
                  </div>
                  <v-btn 
                    color="indigo-darken-1" 
                    variant="flat" 
                    size="small" 
                    class="font-weight-bold px-3 text-none" 
                    style="border-radius: 8px; height: 32px;"
                    @click="copyCurrentHospitalMailBody"
                  >
                    <v-icon start size="15" class="mr-1">mdi-clipboard-text-play-outline</v-icon>
                    본문 전체 다시 복사
                  </v-btn>
                </div>

                <!-- 실시간 렌더링 영역 (1개의 통합 표 + 중복 가이드 제거) -->
                <div class="helper-read-html flex-grow-1" v-html="currentHospitalHtmlBody" style="background-color: #ffffff; border: 1px solid #e2e8f0; min-height: 240px; border-radius: 12px; padding: 18px;"></div>
              </v-col>
            </v-row>
          </div>

          <div class="copy-helper-footer d-flex justify-end align-center" style="gap: 12px;">
            <v-btn 
              color="success" 
              variant="flat" 
              class="font-weight-bold text-none px-4" 
              style="border-radius: 8px; height: 38px;"
              prepend-icon="mdi-email-send-outline"
              @click="sendToNaverDebugPort('naver')"
            >
              네이버 메일(8080) 전송
            </v-btn>
            <v-btn 
              color="info" 
              variant="flat" 
              class="font-weight-bold text-none px-4" 
              style="border-radius: 8px; height: 38px;"
              prepend-icon="mdi-email-send-outline"
              @click="sendToNaverDebugPort('hiworks')"
            >
              하이웍스(8080) 전송
            </v-btn>
            <v-btn 
              color="warning" 
              variant="flat" 
              class="font-weight-bold text-none px-4" 
              style="border-radius: 8px; height: 38px;"
              prepend-icon="mdi-email-send-outline"
              @click="sendToNaverDebugPort('other')"
            >
              기타 메일(8080)
            </v-btn>
            <button class="sleek-btn sleek-btn-info-outline" @click="hospitalSetupDialog = false" style="height: 38px;">닫기</button>
          </div>
        </v-card>
      </v-dialog>

      <!-- [모달 2] EMR사별 메일 취합 및 듀얼 리스트 요양기관 이동 설정 모달 -->
      <v-dialog v-model="emrSetupDialog" max-width="1250px" persistent>
        <v-card class="copy-helper-card" elevation="24">
          <div class="copy-helper-header d-flex align-center">
            <v-icon color="info" class="mr-2" size="large">mdi-folder-swap-outline</v-icon>
            <span class="font-weight-bold text-slate-800" style="font-size: 16px;">EMR 기술지원 취합 발송 리스트 설정 ({{ currentEmrName }})</span>
            <v-spacer></v-spacer>
            <v-btn icon="mdi-close" variant="text" size="small" color="slate-400" @click="emrSetupDialog = false"></v-btn>
          </div>

          <div class="copy-helper-body pa-4" style="max-height: 700px; overflow-y: auto;">
            <!-- 듀얼 리스트 UI -->
            <v-row class="mb-6">
              <!-- 전체 요양기관 리스트 (왼쪽) -->
              <v-col cols="12" md="5">
                <div class="list-container-card">
                  <div class="list-container-header bg-slate-50 d-flex justify-space-between align-center">
                    <span class="list-title font-weight-bold text-slate-700">전체 대상 요양기관 ({{ emrSourceHospitals.length }})</span>
                    <button class="mini-text-btn" @click="moveAllHospitalsToTarget">전체 추가 &gt;&gt;</button>
                  </div>
                  <div class="list-body-scroll">
                    <div 
                      v-for="h in emrSourceHospitals" 
                      :key="h.hospital" 
                      class="transfer-item-card cursor-pointer"
                      @click="moveHospitalToTarget(h.hospital)"
                    >
                      <div class="d-flex align-center justify-space-between">
                        <div>
                          <div class="font-weight-bold text-slate-800" style="font-size: 13px;">{{ h.hospital }}</div>
                          <div class="text-caption text-slate-400">오류 대기건: {{ h.cases.reduce((sum, c) => sum + c.count, 0) }}건</div>
                        </div>
                        <v-icon color="slate-300">mdi-chevron-right</v-icon>
                      </div>
                    </div>
                    <div v-if="emrSourceHospitals.length === 0" class="empty-list-placeholder">추가할 요양기관이 없습니다.</div>
                  </div>
                </div>
              </v-col>

              <!-- 중앙 이동 아이콘 데코 -->
              <v-col cols="12" md="2" class="d-flex flex-column align-center justify-center gap-2">
                <div class="transfer-arrow-icon d-none d-md-flex">
                  <v-icon size="32" color="slate-400">mdi-swap-horizontal</v-icon>
                </div>
                <div class="text-caption text-slate-400 text-center font-weight-medium">
                  카드를 클릭하면<br>반대편으로 이동합니다.
                </div>
              </v-col>

              <!-- 발송리스트 (오른쪽) -->
              <v-col cols="12" md="5">
                <div class="list-container-card target-list-border">
                  <div class="list-container-header bg-blue-50 d-flex justify-space-between align-center">
                    <span class="list-title font-weight-bold text-blue-800">취합 발송리스트 ({{ emrTargetHospitals.length }})</span>
                    <button class="mini-text-btn text-blue-600" @click="moveAllHospitalsToSource">&lt;&lt; 전체 제외</button>
                  </div>
                  <div class="list-body-scroll">
                    <div 
                      v-for="h in emrTargetHospitals" 
                      :key="h.hospital" 
                      class="transfer-item-card target-card d-flex flex-column pa-3 mb-2"
                      style="border: 1px solid #bfdbfe; background-color: #f0f7ff; border-radius: 10px; cursor: default;"
                    >
                      <!-- 병원 카드 헤더 (제외 버튼 별도 분리) -->
                      <div class="d-flex align-center justify-space-between mb-2">
                        <div>
                          <div class="font-weight-bold text-blue-900" style="font-size: 13px;">{{ h.hospital }}</div>
                          <div class="text-caption text-blue-500" style="font-weight: 600;">
                            취합 오류 건수: <span class="text-blue-700">{{ getFilteredEmrHospitalCount(h) }}건</span>
                          </div>
                        </div>
                        <v-btn 
                          icon="mdi-minus-circle-outline" 
                          variant="text" 
                          size="small" 
                          color="red-darken-1" 
                          title="취합 제외"
                          style="min-width: 28px; width: 28px; height: 28px;"
                          @click="moveHospitalToSource(h.hospital)"
                        ></v-btn>
                      </div>

                      <!-- 병원 하위 오류 카테고리 체크박스 목록 (병원별 > 오류별 체크) -->
                      <div style="border-top: 1px dashed #bfdbfe; padding-top: 8px;" class="pl-1">
                        <div 
                          v-for="c in h.cases" 
                          :key="c.category" 
                          class="d-flex align-center py-1 cursor-pointer"
                          @click="toggleEmrHospitalCategory(h.hospital, normalizeCategoryName(c.category))"
                        >
                          <input 
                            type="checkbox" 
                            :checked="isEmrHospitalCategorySelected(h.hospital, normalizeCategoryName(c.category))" 
                            style="cursor: pointer; margin-right: 8px; width: 14px; height: 14px;"
                            @click.stop
                            @change="toggleEmrHospitalCategory(h.hospital, normalizeCategoryName(c.category))"
                          />
                          <span 
                            class="text-slate-700 text-truncate" 
                            style="font-size: 11.5px; max-width: 320px; font-weight: 500;" 
                            :title="c.category"
                          >
                            {{ appendApiSuffix(c.category, c.rows?.[0]) }} <span class="text-blue-600 font-weight-bold">({{ c.count }}건)</span>
                          </span>
                        </div>
                      </div>
                    </div>
                    <div v-if="emrTargetHospitals.length === 0" class="empty-list-placeholder">우측 발송리스트가 비어있습니다.</div>
                  </div>
                </div>
              </v-col>
            </v-row>

            <!-- 메일 수신 정보 및 본문 HTML 미리보기 -->
            <v-card class="pa-5 bg-slate-50 border mt-4" style="border-radius: 12px; border: 1px solid #e2e8f0 !important;" elevation="0">
              <div class="d-flex align-center mb-4 pb-2" style="border-bottom: 1.5px solid #eceff1;">
                <v-icon color="indigo-darken-2" class="mr-2" size="20">mdi-folder-zip-outline</v-icon>
                <span class="font-weight-bold text-slate-800" style="font-size: 14.5px; letter-spacing: -0.4px;">취합 메일 구성 정보</span>
              </div>
              
              <v-row>
                <v-col cols="12" md="4">
                  <div class="field-title mb-1">
                    <v-icon size="15" class="text-indigo-accent-3">mdi-account-arrow-right-outline</v-icon>
                    <span>EMR사 담당 수신인</span>
                  </div>
                  <div class="sleek-input-group">
                    <input type="text" v-model="emrSetupData.to" class="helper-read-input flex-grow-1" placeholder="수신인 주소" />
                    <button class="input-inline-btn" title="수신인 복사" @click="copyText(emrSetupData.to, '수신인 주소가')">
                      <v-icon size="17">mdi-content-copy</v-icon>
                    </button>
                  </div>
                </v-col>
                <v-col cols="12" md="4">
                  <div class="field-title mb-1">
                    <v-icon size="15" class="text-indigo-accent-3">mdi-account-multiple-outline</v-icon>
                    <span>참조처 (CC)</span>
                  </div>
                  <div class="sleek-input-group">
                    <input type="text" v-model="emrSetupData.cc" class="helper-read-input flex-grow-1" placeholder="참조 주소" />
                    <button class="input-inline-btn" title="참조자 복사" @click="copyText(emrSetupData.cc, '참조 주소가')">
                      <v-icon size="17">mdi-content-copy</v-icon>
                    </button>
                  </div>
                </v-col>
                <v-col cols="12" md="4">
                  <div class="field-title mb-1">
                    <v-icon size="15" class="text-indigo-accent-3">mdi-bookmark-outline</v-icon>
                    <span>취합 메일 제목</span>
                  </div>
                  <div class="sleek-input-group">
                    <input type="text" v-model="emrSetupData.subject" class="helper-read-input flex-grow-1 font-weight-bold" placeholder="메일 제목" style="color: #3b82f6 !important;" />
                    <button class="input-inline-btn" title="제목 복사" @click="copyText(emrSetupData.subject, '메일 제목이')">
                      <v-icon size="17">mdi-content-copy</v-icon>
                    </button>
                  </div>
                </v-col>
              </v-row>

              <div class="mt-4 mb-2 d-flex align-center justify-space-between">
                <div class="field-title">
                  <v-icon size="15" class="text-slate-500">mdi-file-document-edit-outline</v-icon>
                  <span style="color: #64748b;">취합 본문 미리보기</span>
                </div>
                <v-btn 
                  color="indigo-darken-1" 
                  variant="flat" 
                  size="small" 
                  class="font-weight-bold px-3 text-none" 
                  style="border-radius: 8px; height: 32px;"
                  @click="copyCurrentEmrMailBody"
                >
                  <v-icon start size="15" class="mr-1">mdi-clipboard-text-play-outline</v-icon>
                  취합 메일 본문 전체 복사
                </v-btn>
              </div>

              <!-- HTML 실시간 미리보기 -->
              <div class="helper-read-html" v-html="currentEmrHtmlBody" style="background-color: #ffffff; border: 1px solid #e2e8f0; min-height: 250px; border-radius: 12px; padding: 18px;"></div>
            </v-card>
          </div>

          <div class="copy-helper-footer d-flex justify-end gap-2 align-center">
            <v-btn 
              color="success" 
              variant="flat" 
              class="font-weight-bold mr-2 text-none"
              style="border-radius: 8px; height: 34px;"
              @click="confirmAndUpdateEmrStatus"
            >
              <v-icon start size="16" class="mr-1">mdi-check-circle-outline</v-icon>
              확인 완료 (상태 변경)
            </v-btn>
            <button class="sleek-btn sleek-btn-info-outline" @click="emrSetupDialog = false" style="height: 34px; padding: 0 16px;">닫기</button>
          </div>
        </v-card>
      </v-dialog>

      <!-- Overlay Loader -->
      <v-overlay :model-value="isLoading" class="align-center justify-center" persistent>
        <v-progress-circular color="primary" indeterminate size="64"></v-progress-circular>
      </v-overlay>

      <!-- Toast Notification (Snackbar) -->
      <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="2000" min-width="100px" style="z-index: 10000;">
        {{ snackbarText }}
      </v-snackbar>

    </v-container>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';

type RowState = '미확인' | '회신대기' | '최종완료';

interface ErrorDetail {
  no: number;
  fileKey: string;
  sheetName?: string;
  hospital: string;
  institutionId: string;
  emr: string;
  category: string;
  details: string;
  visitDate: string;
  uuid: string;
  patient: string;
  birthDate: string;
  state: RowState;
}

interface ClaimCase {
  key: string;
  hospital: string;
  institutionId: string;
  emr: string;
  category: string;
  patient: string;
  birthDate: string;
  count: number;
  state: RowState;
  fileKey: string;
  rows: ErrorDetail[];
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000') + '/api/errorStatistics';

const isLoading = ref(false);
const activeTab = ref<'hospital' | 'emr'>('hospital');

const getEmrClass = (emr: string) => {
  if (!emr || emr === '미지정') return 'emr-unassigned';
  if (emr.includes('인티그레이션')) return 'emr-integration';
  if (emr.includes('이원헬스케어')) return 'emr-eone';
  return 'emr-default';
};
const allFileKeys = ref<string[]>([]);
const selectedFileKey = ref<string>('');
const rawRows = ref<ErrorDetail[]>([]);

// 설정값들 (CC 및 제목 템플릿 보존)
const fixedCc = ref(localStorage.getItem('claim_fixed_cc') || '');
const titleTemplate = ref(localStorage.getItem('claim_title_template') || '[청구실패오류] {요양기관명} 청구 보정 요청 건 ({차수})');

watch(titleTemplate, (newVal) => {
  localStorage.setItem('claim_title_template', newVal);
});

watch(fixedCc, (newCc) => {
  localStorage.setItem('claim_fixed_cc', newCc);
});

// 이메일 주소 정보 (localStorage 연동)
const hospitalEmails = ref<Record<string, string>>(JSON.parse(localStorage.getItem('claim_hospital_emails') || '{}'));
const emrEmails = ref<Record<string, string>>(JSON.parse(localStorage.getItem('claim_emr_emails') || '{}'));

// 테이블 제어용
const hospitalSearch = ref('');
const selectedHospitalNames = ref<string[]>([]);

const isAllHospitalsSelected = computed(() => {
  return filteredHospitals.value.length > 0 && selectedHospitalNames.value.length === filteredHospitals.value.length;
});

function toggleAllHospitalsSelection() {
  if (isAllHospitalsSelected.value) {
    selectedHospitalNames.value = [];
  } else {
    selectedHospitalNames.value = filteredHospitals.value.map(h => h.hospital);
  }
}

// 토스트 피드백
const snackbar = ref(false);
const snackbarText = ref('');
const snackbarColor = ref('success');

function showSnackbar(text: string, color: string = 'success') {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbar.value = true;
}

// 텍스트 클립보드 복사 헬퍼
function copyText(text: string, label: string) {
  navigator.clipboard.writeText(text)
    .then(() => {
      showSnackbar(`${label} 클립보드에 복사되었습니다!`);
    })
    .catch(err => {
      console.error('복사 실패:', err);
      showSnackbar('복사에 실패했습니다.', 'error');
    });
}

// 리치 텍스트 클립보드 복사 헬퍼
function copyRichText(plainText: string, htmlText: string) {
  const textBlob = new Blob([plainText], { type: 'text/plain' });
  const htmlBlob = new Blob([htmlText], { type: 'text/html' });
  const clipboardItem = new ClipboardItem({
    'text/plain': textBlob,
    'text/html': htmlBlob
  });

  navigator.clipboard.write([clipboardItem])
    .then(() => {
      showSnackbar('메일 본문(표 서식 포함)이 클립보드에 복사되었습니다!');
    })
    .catch(err => {
      console.error('HTML 복사 실패, 일반 텍스트 대체:', err);
      navigator.clipboard.writeText(plainText)
        .then(() => {
          showSnackbar('메일 본문(일반 텍스트)이 복사되었습니다.');
        })
        .catch(e => {
          showSnackbar('복사에 실패했습니다.', 'error');
        });
    });
}

function cleanCategoryHeader(str: string): string {
  let res = str.trim();
  // 바깥쪽 대괄호 [ ] 껍질 제거
  if (res.startsWith('[') && res.endsWith(']')) {
    res = res.substring(1, res.length - 1).trim();
  }
  const match = res.match(/청구실패\s*사유\s*[:：]?\s*(.*)$/i);
  if (match && match[1]) {
    res = match[1].trim();
  }
  if (res.startsWith('■')) {
    res = res.substring(1).trim();
  }
  if (res.endsWith(']')) {
    res = res.substring(0, res.length - 1).trim();
  }
  return res;
}

// 엑셀 파싱 헬퍼 함수
function getGroupKey(row: ErrorDetail): string {
  let cleanDetails = row.details || '';
  let errorTitle = row.category && !row.category.includes('미분류') ? row.category : '미분류';
  if (errorTitle === '미분류') {
    if (cleanDetails.includes('===')) {
      const parts = cleanDetails.split(/={3,}/);
      if (parts[1] && parts[1].trim() !== '') {
        errorTitle = cleanCategoryHeader(parts[1]);
      } else {
        errorTitle = parts[0].trim().substring(0, 40);
      }
    } else {
      errorTitle = cleanDetails.substring(0, 40);
    }
  } else {
    errorTitle = cleanCategoryHeader(errorTitle);
  }
  return `${row.fileKey}|${row.hospital.trim()}|${errorTitle}`;
}

const fileOptions = computed(() => {
  const options = allFileKeys.value
      .map(key => ({ title: key.replace(/_/g, '-'), value: key }))
      .sort((a, b) => b.value.localeCompare(a.value));
  return [{ title: '전체', value: 'all' }, ...options];
});

const normalizedRows = computed<ErrorDetail[]>(() => {
  return rawRows.value.filter(row => row.hospital && !row.hospital.includes('청구실패 사유') && !row.hospital.startsWith('■'));
});

const allGroupedClaimCases = computed<ClaimCase[]>(() => {
  const groups: Record<string, ErrorDetail[]> = {};
  normalizedRows.value.forEach(row => {
    const key = getGroupKey(row);
    if (!groups[key]) groups[key] = [];
    groups[key].push(row);
  });

  return Object.entries(groups).map(([groupKey, rows]) => {
    const first = rows[0];
    let cleanDetails = first.details || '';
    let errorTitle = first.category && !first.category.includes('미분류') ? first.category : '미분류';
    if (errorTitle === '미분류') {
      if (cleanDetails.includes('===')) {
        const parts = cleanDetails.split(/={3,}/);
        if (parts[1] && parts[1].trim() !== '') {
          errorTitle = cleanCategoryHeader(parts[1]);
        } else {
          errorTitle = parts[0].trim().substring(0, 40);
        }
      } else {
        errorTitle = cleanDetails.substring(0, 40);
      }
    } else {
      errorTitle = cleanCategoryHeader(errorTitle);
    }

    return {
      key: groupKey, hospital: first.hospital.trim(), institutionId: first.institutionId,
      emr: first.emr, category: errorTitle,
      patient: rows.length > 1 ? `${first.patient} 외 ${rows.length - 1}명` : first.patient,
      birthDate: first.birthDate, count: rows.length,
      state: first.state || '미확인', fileKey: first.fileKey, rows
    };
  });
});

const groupedClaimCases = computed<ClaimCase[]>(() => {
  if (!selectedFileKey.value || selectedFileKey.value === 'all') return allGroupedClaimCases.value;
  return allGroupedClaimCases.value.filter(c => c.fileKey === selectedFileKey.value);
});

// 요양기관별 통계 목록
const groupedHospitals = computed(() => {
  const hospitalCounts: Record<string, { count: number; emr: string; cases: ClaimCase[] }> = {};
  groupedClaimCases.value.forEach(claimCase => {
    if (!hospitalCounts[claimCase.hospital]) {
      hospitalCounts[claimCase.hospital] = { count: 0, emr: claimCase.emr, cases: [] };
    }
    hospitalCounts[claimCase.hospital].count += claimCase.count;
    hospitalCounts[claimCase.hospital].cases.push(claimCase);
  });
  return Object.entries(hospitalCounts).map(([hospital, data]) => ({
    hospital, count: data.count, emr: data.emr, cases: data.cases
  }));
});

const filteredHospitals = computed(() => {
  const search = hospitalSearch.value.trim().toLowerCase();
  let list = groupedHospitals.value;
  if (search) {
    list = list.filter(h => h.hospital.toLowerCase().includes(search));
  }
  return list.sort((a, b) => b.count - a.count);
});

// EMR사별 통계 목록
const emrSummary = computed(() => {
  const emrGroups: Record<string, { totalCount: number; hospitals: Set<string>; cases: ClaimCase[] }> = {};
  groupedClaimCases.value.forEach(c => {
    // EMR 개발사가 '미지정'이거나 비어있으면 제외!
    if (!c.emr || c.emr === '미지정' || c.emr.trim() === '') return;

    if (!emrGroups[c.emr]) {
      emrGroups[c.emr] = { totalCount: 0, hospitals: new Set(), cases: [] };
    }
    emrGroups[c.emr].totalCount += c.count;
    emrGroups[c.emr].hospitals.add(c.hospital);
    emrGroups[c.emr].cases.push(c);
  });

  return Object.entries(emrGroups).map(([emr, data]) => ({
    emr,
    totalCount: data.totalCount,
    hospitals: Array.from(data.hospitals),
    cases: data.cases
  })).sort((a, b) => b.totalCount - a.totalCount);
});

function saveHospitalEmails() {
  localStorage.setItem('claim_hospital_emails', JSON.stringify(hospitalEmails.value));
}

function saveEmrEmails() {
  localStorage.setItem('claim_emr_emails', JSON.stringify(emrEmails.value));
}

// API를 통해 데이터 로드
async function loadExcelData() {
  isLoading.value = true;
  try {
    const filesRes = await fetch(`${API_BASE_URL}/files?t=${Date.now()}`);
    if (!filesRes.ok) throw new Error('Failed to load file list');
    const filesJson = await filesRes.json();

    if (filesJson.success && Array.isArray(filesJson.files)) {
      allFileKeys.value = filesJson.files;
      if (filesJson.files.length > 0 && !selectedFileKey.value) {
        const sorted = [...filesJson.files].sort((a, b) => b.localeCompare(a));
        selectedFileKey.value = sorted[0];
      }
    }

    const loadedRows: ErrorDetail[] = [];
    for (const fileKey of allFileKeys.value) {
      const dataRes = await fetch(`${API_BASE_URL}/data/${fileKey}?t=${Date.now()}`);
      if (!dataRes.ok) continue;
      const dataJson = await dataRes.json();
      if (dataJson.success && Array.isArray(dataJson.rows)) {
        dataJson.rows.forEach((row: ErrorDetail) => {
          loadedRows.push(row);
        });
      }
    }
    rawRows.value = loadedRows;
  } catch (error) {
    console.error('Data loading error:', error);
  } finally {
    isLoading.value = false;
  }
}

// 제목 빌더 헬퍼
function buildEmailSubject(hospital: string, fileKey: string) {
  const template = titleTemplate.value.trim() || '[청구실패오류] {요양기관명} 청구 보정 요청 건 ({차수})';
  const dateStr = fileKey.replace(/_/g, '-');
  return template
    .replace(/{요양기관명}/g, hospital)
    .replace(/{차수}/g, dateStr);
}

// ==========================================================================
// [모달 1] 요양기관별 각각 발송 - 뺄건 빼고 넣을건 넣는 로직 추가
// ==========================================================================

const hospitalSetupDialog = ref(false);
const currentHospitalName = ref('');
const currentHospitalErrors = ref<ErrorDetail[]>([]);
const selectedCategories = ref<string[]>([]);
const hospitalSetupData = ref({ to: '', cc: '', subject: '' });

// 탭 전환 시 설정창에서 저장한 텍스트 리액티브 바인딩
const localIntroText = ref(localStorage.getItem('claim_intro_text') || '이메일 또는 메신저로 전달되는 자동화 문구입니다.');
const localCustomInstructions = ref<Record<string, string>>(JSON.parse(localStorage.getItem('claim_custom_instructions') || '{}'));

// 현재 요양기관이 가지고 있는 에러 카테고리와 건수 계산
const currentHospitalCategories = computed(() => {
  const catsMap: Record<string, number> = {};
  currentHospitalErrors.value.forEach(err => {
    const name = normalizeCategoryName(err.category);
    catsMap[name] = (catsMap[name] || 0) + 1;
  });
  return Object.entries(catsMap).map(([name, count]) => ({ name, count }));
});

// 요양기관 세부 편집 모달 열기
function openHospitalMailSetup(item: any) {
  currentHospitalName.value = item.hospital;
  
  // 모달을 열 때마다 대시보드 복사 설정에서 저장한 최신 로컬데이터를 강제 재로드하여 리액티비티 보장
  localIntroText.value = localStorage.getItem('claim_intro_text') || '이메일 또는 메신저로 전달되는 자동화 문구입니다.';
  localCustomInstructions.value = JSON.parse(localStorage.getItem('claim_custom_instructions') || '{}');
  
  // 소속 행들을 전부 풀어서 세부 에러 배열로 추출
  const errors = item.cases.flatMap((c: any) => c.rows || []);
  currentHospitalErrors.value = errors;
  
  // 기본적으로 전체 카테고리가 선택된 상태로 설정
  const cats = Array.from(new Set(errors.map((e: any) => normalizeCategoryName(e.category))));
  selectedCategories.value = cats;
  
  // 메일 기본 정보
  hospitalSetupData.value = {
    to: hospitalEmails.value[item.hospital] || '',
    cc: fixedCc.value.trim(),
    subject: buildEmailSubject(item.hospital, selectedFileKey.value)
  };
  
  // 클립보드 복사도 모달 띄우자마자 초기 1회 기본 세팅 복사 진행
  setTimeout(() => {
    const { plain, html } = currentHospitalHtmlAndPlainBody.value;
    copyRichText(plain, html);
  }, 100);

  hospitalSetupDialog.value = true;
}

function toggleCategorySelection(catName: string) {
  const index = selectedCategories.value.indexOf(catName);
  if (index >= 0) {
    selectedCategories.value.splice(index, 1);
  } else {
    selectedCategories.value.push(catName);
  }
  
  // 선택이 바뀔 때마다 본문을 자동 복사해 주어 UX 최적화 유지
  setTimeout(() => {
    const { plain, html } = currentHospitalHtmlAndPlainBody.value;
    copyRichText(plain, html);
  }, 150);
}

function selectAllHospitalCategories() {
  selectedCategories.value = currentHospitalCategories.value.map(c => c.name);
  setTimeout(() => {
    const { plain, html } = currentHospitalHtmlAndPlainBody.value;
    copyRichText(plain, html);
  }, 150);
}

function deselectAllHospitalCategories() {
  selectedCategories.value = [];
  setTimeout(() => {
    const { plain, html } = currentHospitalHtmlAndPlainBody.value;
    copyRichText(plain, html);
  }, 150);
}

// 선택된 에러 데이터들만을 추출하여 대시보드 리치 HTML/Plain 구성
const currentHospitalHtmlAndPlainBody = computed(() => {
  const activeErrors = currentHospitalErrors.value.filter(e => {
    const cat = normalizeCategoryName(e.category);
    return selectedCategories.value.includes(cat);
  });
  const institutionId = activeErrors[0]?.institutionId || '-';
  
  if (activeErrors.length === 0) {
    return {
      plain: '선택된 오류 내역이 없습니다.',
      html: '<div style="color: #ef4444; font-weight: bold; padding: 10px;">선택된 오류 내역이 없습니다. 좌측에서 전송할 에러를 1개 이상 선택해 주세요.</div>'
    };
  }

  // 요양기관별 메일 템플릿 포맷팅 (찌그러짐 방지 - 중복되는 병원기관번호/병원명/EMR은 표에서 생략)
  return formatHospitalSpecificText(currentHospitalName.value, institutionId, activeErrors);
});

const currentHospitalHtmlBody = computed(() => currentHospitalHtmlAndPlainBody.value.html);

// 요양기관 수동 전체 본문 복사 기능 실행
function copyCurrentHospitalMailBody() {
  const { plain, html } = currentHospitalHtmlAndPlainBody.value;
  copyRichText(plain, html);
}

// 요양기관별 메일 8080 크롬 디버깅 포트 전송 API 호출
async function sendToNaverDebugPort(serviceType = 'naver') {
  try {
    const to = hospitalSetupData.value.to;
    const cc = hospitalSetupData.value.cc;
    const subject = hospitalSetupData.value.subject;
    const html_body = currentHospitalHtmlBody.value;

    // 로컬 백엔드 서버(Express)에 팝업 요청 전송
    const response = await fetch(`${API_BASE_URL}/open-naver-popup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        to,
        cc,
        subject,
        html_body,
        hospital: currentHospitalName.value,
        service: serviceType
      })
    });

    const res = await response.json();
    if (res.success) {
      alert(`✅ 크롬 디버깅 8080 포트를 통해 ${serviceType === 'naver' ? '네이버' : '하이웍스'} 메일 주입이 실행되었습니다!`);
    } else {
      alert(`❌ 전송 실패: ${res.error || '알 수 없는 오류'}`);
    }
  } catch (error) {
    console.error("메일 디버깅 전송 중 에러:", error);
    alert(`❌ 에러 발생: ${error.message || error}`);
  }
}

// 요양기관 선택 일괄 팝업 전송 API 호출
async function sendBatchToNaverDebugPort(serviceType = 'naver') {
  if (selectedHospitalNames.value.length === 0) {
    alert("선택된 요양기관이 없습니다.");
    return;
  }

  const selectedHospitals = filteredHospitals.value.filter(h => selectedHospitalNames.value.includes(h.hospital));

  // 1. 일괄 발송 확인 메시지
  if (!confirm(`선택한 ${selectedHospitalNames.value.length}개 요양기관의 메일 창(${serviceType === 'naver' ? '네이버' : '하이웍스'})을 띄우시겠습니까?`)) {
    return;
  }

  try {
    // 최신 설정 갱신
    localIntroText.value = localStorage.getItem('claim_intro_text') || '이메일 또는 메신저로 전달되는 자동화 문구입니다.';
    localCustomInstructions.value = JSON.parse(localStorage.getItem('claim_custom_instructions') || '{}');

    // 3. 메일 데이터 리스트 구성
    const mailList = selectedHospitals.map(h => {
      const errors = h.cases.flatMap((c: any) => c.rows || []);
      const institutionId = errors[0]?.institutionId || '-';
      
      // formatHospitalSpecificText(hospitalName, institutionId, activeErrors)
      const { html } = formatHospitalSpecificText(h.hospital, institutionId, errors);
      const subject = buildEmailSubject(h.hospital, selectedFileKey.value);
      const to = hospitalEmails.value[h.hospital];

      return {
        hospital: h.hospital,
        to: to,
        cc: fixedCc.value.trim(),
        subject: subject,
        html_body: html,
        service: serviceType
      };
    });

    // 4. 백엔드로 배치 요청 전송
    const response = await fetch(`${API_BASE_URL}/open-naver-popup-batch`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ mailList })
    });

    const res = await response.json();
    if (res.success) {
      alert(`✅ ${selectedHospitalNames.value.length}개 병원의 ${serviceType === 'naver' ? '네이버' : '하이웍스'} 메일 주입 스크립트가 실행되었습니다!`);
      selectedHospitalNames.value = []; // 성공 시 선택 초기화
    } else {
      alert(`❌ 전송 실패: ${res.error || '알 수 없는 오류'}`);
    }
  } catch (error: any) {
    console.error("배치 전송 중 에러:", error);
    alert(`❌ 에러 발생: ${error.message || error}`);
  }
}

// ==========================================================================
// [모달 2] EMR사별 취합 발송 - 듀얼 리스트 요양기관 이동 ("넣을꺼 넣고 뺄꺼 빼고")
// ==========================================================================

const emrSetupDialog = ref(false);
const currentEmrName = ref('');
const emrSourceHospitals = ref<{ hospital: string; cases: ClaimCase[] }[]>([]); // 왼쪽 (대기)
const emrTargetHospitals = ref<{ hospital: string; cases: ClaimCase[] }[]>([]); // 오른쪽 (발송리스트)
const emrSetupData = ref({ to: '', cc: '', subject: '' });

// EMR 취합에서 선택된 병원별 오류 카테고리 맵
const emrSelectedCategories = ref<Record<string, string[]>>({});

function isEmrHospitalCategorySelected(hospital: string, catName: string): boolean {
  const cats = emrSelectedCategories.value[hospital] || [];
  return cats.includes(catName);
}

function toggleEmrHospitalCategory(hospital: string, catName: string) {
  if (!emrSelectedCategories.value[hospital]) {
    emrSelectedCategories.value[hospital] = [];
  }
  const cats = emrSelectedCategories.value[hospital];
  const idx = cats.indexOf(catName);
  if (idx >= 0) {
    cats.splice(idx, 1);
  } else {
    cats.push(catName);
  }
  // 실시간으로 클립보드에 다시 빌드하여 복사
  setTimeout(() => {
    const { plain, html } = buildEmrMailContentCombined();
    copyRichText(plain, html);
  }, 100);
}

function getFilteredEmrHospitalCount(h: any): number {
  const selectedCats = emrSelectedCategories.value[h.hospital] || [];
  return h.cases.reduce((sum: number, c: any) => {
    const name = normalizeCategoryName(c.category);
    return sum + (selectedCats.includes(name) ? c.count : 0);
  }, 0);
}

// EMR 취합 편집 모달 열기
function openEmrMailSetup(item: any) {
  currentEmrName.value = item.emr;
  
  // 소속 병원 리스트 분석
  const hospitalList = item.hospitals.map((hName: string) => {
    const cases = item.cases.filter((c: any) => c.hospital === hName);
    return { hospital: hName, cases };
  });

  // 초기값: 전체 병원이 '발송리스트 (오른쪽)'에 들어가 있도록 설정
  emrSourceHospitals.value = [];
  emrTargetHospitals.value = hospitalList;

  // 병원별 오류 카테고리 체크 박스 기본값 (전부 선택으로 초기화)
  emrSelectedCategories.value = {};
  hospitalList.forEach((h: any) => {
    const cats = h.cases.map((c: any) => normalizeCategoryName(c.category));
    emrSelectedCategories.value[h.hospital] = cats;
  });

  // EMR 전용 취합 타이틀 템플릿 파싱 (요양기관별 공통 서식에 EMR사명만 치환 대입)
  emrSetupData.value = {
    to: emrEmails.value[item.emr] || '',
    cc: fixedCc.value.trim(),
    subject: buildEmailSubject(item.emr + ' 계열', selectedFileKey.value)
  };

  // 1회 자동 복사 실행
  setTimeout(() => {
    const { plain, html } = buildEmrMailContentCombined();
    copyRichText(plain, html);
  }, 100);

  emrSetupDialog.value = true;
}

// 왼쪽(대기)에서 -> 오른쪽(발송리스트)으로 이동
function moveHospitalToTarget(hName: string) {
  const idx = emrSourceHospitals.value.findIndex(h => h.hospital === hName);
  if (idx >= 0) {
    const [item] = emrSourceHospitals.value.splice(idx, 1);
    emrTargetHospitals.value.push(item);
  }
  // 실시간 클립보드 자동복사 동기화
  setTimeout(() => {
    const { plain, html } = buildEmrMailContentCombined();
    copyRichText(plain, html);
  }, 150);
}

// 오른쪽(발송리스트)에서 -> 왼쪽(대기)으로 제외
function moveHospitalToSource(hName: string) {
  const idx = emrTargetHospitals.value.findIndex(h => h.hospital === hName);
  if (idx >= 0) {
    const [item] = emrTargetHospitals.value.splice(idx, 1);
    emrSourceHospitals.value.push(item);
  }
  // 실시간 클립보드 자동복사 동기화
  setTimeout(() => {
    const { plain, html } = buildEmrMailContentCombined();
    copyRichText(plain, html);
  }, 150);
}

// 전체 이동
function moveAllHospitalsToTarget() {
  emrTargetHospitals.value.push(...emrSourceHospitals.value);
  emrSourceHospitals.value = [];
  setTimeout(() => {
    const { plain, html } = buildEmrMailContentCombined();
    copyRichText(plain, html);
  }, 150);
}

function moveAllHospitalsToSource() {
  emrSourceHospitals.value.push(...emrTargetHospitals.value);
  emrTargetHospitals.value = [];
  setTimeout(() => {
    const { plain, html } = buildEmrMailContentCombined();
    copyRichText(plain, html);
  }, 150);
}

// [확인 완료 (상태 변경)] 버튼 클릭 시 EMR사별 선택 요양기관들의 에러 내역을 '회신대기' 상태로 일괄 전환
async function confirmAndUpdateEmrStatus() {
  const activeHospitals = emrTargetHospitals.value.map(h => {
    const selectedCats = emrSelectedCategories.value[h.hospital] || [];
    const activeCases = h.cases.filter(c => selectedCats.includes(normalizeCategoryName(c.category)));
    return { ...h, cases: activeCases };
  }).filter(h => h.cases.length > 0);

  if (activeHospitals.length === 0) {
    alert('상태를 변경할 취합 요양기관 혹은 선택된 오류 내역이 없습니다.');
    return;
  }

  const isConfirmed = confirm(`선택된 요양기관들의 오류 실패 내역 상태를 [회신대기] 상태로 일괄 변경하시겠습니까?`);
  if (!isConfirmed) return;

  isLoading.value = true;
  try {
    const promises = activeHospitals.map(async (h) => {
      const allHospitalRows = h.cases.flatMap(c => c.rows || []);
      if (allHospitalRows.length === 0) return;

      const res = await fetch(`${API_BASE_URL}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fileKey: selectedFileKey.value,
          hospital: h.hospital,
          state: '회신대기',
          rows: allHospitalRows
        })
      });

      if (res.ok) {
        // 로컬 rawRows 실시간 갱신 처리
        allHospitalRows.forEach((r: any) => {
          const target = rawRows.value.find(row => row.uuid === r.uuid);
          if (target) {
            target.state = '회신대기';
          }
        });
      } else {
        throw new Error(`${h.hospital} 상태 업데이트 실패`);
      }
    });

    await Promise.all(promises);
    
    // 알림 표시
    showSnackbar('선택된 요양기관들의 오류 상태가 [회신대기]로 전환되었습니다.', 'success');
    
    emrSetupDialog.value = false; // 모달 닫기
  } catch (error) {
    console.error('EMR 취합 일괄 상태 변경 오류:', error);
    showSnackbar('일부 요양기관 상태 변경 중 오류가 발생했습니다.', 'error');
  } finally {
    isLoading.value = false;
  }
}

// 오른쪽 리스트에 담긴 EMR 병원 데이터 기반으로 취합 메일 본문 빌드
function buildEmrMailContentCombined() {
  // 실제 선택된 카테고리가 1개라도 있는 병원들만 필터링하여 취합 대상 정의
  const activeHospitals = emrTargetHospitals.value.map(h => {
    const selectedCats = emrSelectedCategories.value[h.hospital] || [];
    const activeCases = h.cases.filter(c => selectedCats.includes(normalizeCategoryName(c.category)));
    return { ...h, cases: activeCases };
  }).filter(h => h.cases.length > 0);

  if (activeHospitals.length === 0) {
    return {
      plain: '취합할 요양기관 혹은 선택된 오류 내역이 없습니다.',
      html: '<div style="color: #ef4444; font-weight: bold; padding: 10px;">취합할 발송리스트(우측)가 비어있거나, 선택된 오류 카테고리가 없습니다.</div>'
    };
  }

  const dateStr = selectedFileKey.value.replace(/_/g, '-');
  const emrName = currentEmrName.value;

  // 0) 공통 인사말 (템플릿 동기화)
  const rawIntro = localIntroText.value || '안녕하세요, {요양기관명} 담당자님.\n소속 요양기관들에서 접수된 청구 실패 내역을 아래와 같이 취합하여 공유하오니, 확인 및 점검을 부탁드립니다.';
  const emrIntro = rawIntro.replace(/{요양기관명}/g, `${emrName} EMR 기술지원`);

  // 1) 오류별 조치 지침 수집
  let plainInstructions = '';
  const plainSeenInstructions = new Set<string>();
  
  activeHospitals.forEach(h => {
    h.cases.forEach(c => {
      const cat = normalizeCategoryName(c.category);
      const inst = getGlobalInstruction(cat);
      if (inst !== '해당사항없음' && inst.trim() !== '') {
        const cleanInst = inst.replace(/\[size=\d+?\](.*?)\[\/size\]/g, '$1').trim();
        const fullKey = `${cat}:${cleanInst}`;
        if (!plainSeenInstructions.has(fullKey)) {
          plainSeenInstructions.add(fullKey);
          plainInstructions += `- ${appendApiSuffix(cat, c.rows?.[0])}: ${cleanInst}\n`;
        }
      }
    });
  });

  const htmlSeenInstructions = new Set<string>();
  const guidelinesHtml = activeHospitals.flatMap(h => {
    return h.cases.map(c => {
      const cat = normalizeCategoryName(c.category);
      const inst = getGlobalInstruction(cat);
      if (inst === '해당사항없음' || inst.trim() === '') return '';
      
      const normInst = inst.trim();
      const fullKey = `${cat}:${normInst}`;
      if (htmlSeenInstructions.has(fullKey)) return '';
      htmlSeenInstructions.add(fullKey);
      
      return `
    <li style="margin-bottom: 6px;">
      <strong>${appendApiSuffix(cat, c.rows?.[0])}</strong><br> ${formatTextToHtml(inst)}
    </li>`;
    });
  }).filter(Boolean).join('');

  // ----------------------------------------------------
  // [A] Plain Text 빌드
  // ----------------------------------------------------
  const cleanIntro = emrIntro.replace(/\[size=\d+?\](.*?)\[\/size\]/g, '$1');
  let plain = `${cleanIntro}\n\n`;

  // 조치 가이드 배치 (인사말 아래)
  if (plainInstructions) {
    plain += `[오류별 조치 요령 안내]\n` + plainInstructions + `\n`;
  }

  activeHospitals.forEach((h) => {
    plain += `■ ${h.hospital} - 청구 오류 내역 취합 현황\n\n`;
    
    // 병원별 소속 에러 행 추출
    const allHospitalRows = h.cases.flatMap(c => c.rows || []);
    const categories = Array.from(new Set(allHospitalRows.map(e => normalizeCategoryName(e.category))));
    
    categories.forEach((cat) => {
      const catErrors = allHospitalRows.filter(e => normalizeCategoryName(e.category) === cat);
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
  });

  plain += `처리되시면 회신 부탁드립니다.\n감사합니다.\n`;

  // ----------------------------------------------------
  // [B] Rich HTML 표 서식 취합 빌드
  // ----------------------------------------------------
  let html = `<div style="font-family: '맑은 고딕', 'Malgun Gothic', sans-serif; font-size: 13px; line-height: 1.6; color: #333;">`;
  html += `<p>${formatTextToHtml(emrIntro)}</p>`;
  
  // 조치 가이드 배치 (인사말 아래)
  if (guidelinesHtml) {
    html += `
    <div style="background-color: #f2f5f8; border-left: 4px solid #1f4e78; padding: 12px 16px; margin: 15px 0 20px 0; border-radius: 4px; font-size: 12px;">
      <div style="font-weight: bold; margin-bottom: 8px; color: #1f4e78;">[오류별 조치 요령 안내]</div>
      <ul style="margin: 0; padding-left: 18px; color: #444; line-height: 1.6;">
        ${guidelinesHtml}
      </ul>
    </div>`;
  }

  activeHospitals.forEach((h, hIdx) => {
    const allHospitalRows = h.cases.flatMap(c => c.rows || []);
    const categories = Array.from(new Set(allHospitalRows.map(e => normalizeCategoryName(e.category))));
    
    let htmlTables = '';
    categories.forEach((cat) => {
      const catErrors = allHospitalRows.filter(e => normalizeCategoryName(e.category) === cat);
      const htmlRows = catErrors.map((err, idx) => {
        const reasonVal = err.category && err.category.includes('(') ? err.category.split('(')[0].trim() : (err.category || '-');
        const detailsVal = (err.visitDate && err.visitDate !== '-' && err.uuid && err.uuid !== '-') 
          ? `진료일자: ${err.visitDate.replace(/-/g, '')} / UUID: ${err.uuid}` 
          : (err.details || '-');
        
        return `
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
    <div style="margin-top: 20px; margin-bottom: 8px; font-size: 14px; font-weight: bold; color: #333;">
      ■ 청구실패 사유: ${appendApiSuffix(cat, catErrors[0])}
    </div>
    <table style="width: 100%; border-collapse: collapse; border: 1px solid #a6a6a6; margin-bottom: 20px; font-size: 11px;">
      <thead>
        <tr style="background-color: #f2f2f2; color: #333333; height: 28px; font-weight: bold;">
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 40px; text-align: center;">No</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 90px; text-align: center;">병원기관번호</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 160px; text-align: center;">병원명</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 90px; text-align: center;">병원EMR</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 170px; text-align: center;">청구실패사유</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; text-align: center;">진료내역 (진료일자 및 UUID)</th>
        </tr>
      </thead>
      <tbody>
        ${htmlRows}
      </tbody>
    </table>
    `;
    });

    html += `
    <div style="margin-top: 25px; margin-bottom: 5px; font-size: 16px; font-weight: bold; color: #002060;">
      ■ ${h.hospital} - 청구 오류 내역 취합 현황
    </div>
    ${htmlTables}
    `;
  });

  html += `<p style="margin-top: 20px;">처리되시면 회신 부탁드립니다.<br>감사합니다.</p>`;
  html += `</div>`;

  return { plain, html };
}

const currentEmrHtmlBody = computed(() => buildEmrMailContentCombined().html);

function copyCurrentEmrMailBody() {
  const { plain, html } = buildEmrMailContentCombined();
  copyRichText(plain, html);
}

function getGlobalInstruction(cat: string): string {
  const normCat = normalizeCategoryName(cat);
  const custom = localCustomInstructions.value[normCat];
  if (custom !== undefined && custom !== null && custom.trim() !== '') {
    return custom.trim();
  }
  const c = normCat.toLowerCase();
  if (c.includes('진료 데이터') || c.includes('약품') || c.includes('조회 실패')) {
    return '의료기관 서버 혹은 위버케어 연동 모듈 장애가 감지되었습니다. EMR 약품 코드 세팅 상태 및 원외처방 데이터의 누락 여부를 확인하십시오.';
  } else if (c.includes('면허')) {
    return '청구 파일 내 의사면허번호 정보가 유실되었습니다. EMR 시스템 내 사용자 권한 설정에서 의사면허 등록 정보를 확인한 뒤 다시 저장해 주십시오.';
  } else if (c.includes('서식')) {
    return '심평원 고시 청구서 서식 표준과 상이합니다. EMR 소프트웨어가 최신 패치 버전을 사용하고 있는지 진단하십시오.';
  }
  return '원무 청구 화면에서 에러 코드를 대조한 뒤 적절한 상세 내역 보정을 진행해 주십시오.';
}

// ==========================================================================
// 복사 문구 설정 헬퍼 (대시보드 복사 로직 완전 동기화)
// ==========================================================================

function normalizeCategoryName(cat: string | null | undefined): string {
  if (!cat) return '미분류';
  return cat.trim().replace(/\s+/g, ' ');
}

function formatTextToHtml(text: string | null | undefined): string {
  if (!text) return '';
  let escaped = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>');
  escaped = escaped.replace(/\[size=(\d+?)\](.*?)\[\/size\]/g, '<span style="font-size: $1px;">$2</span>');
  escaped = escaped.replace(/\n/g, '<br>');
  return escaped;
}

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

// 요양기관 각각 발송용 콤팩트 테이블 포맷터
// 요양기관 각각 발송용 콤팩트 테이블 포맷터
function formatHospitalSpecificText(hospital: string, institutionId: string, errors: any[]) {
  const introTextVal = localIntroText.value;
  const customInstructionsVal = localCustomInstructions.value;
  
  const categories = Array.from(new Set(errors.map(e => normalizeCategoryName(e.category))));
  
  const getInstruction = (cat: string): string => {
    const normCat = normalizeCategoryName(cat);
    const custom = customInstructionsVal[normCat];
    if (custom !== undefined && custom !== null && custom.trim() !== '') {
      return custom.trim();
    }
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

  // 1) 일반 텍스트 버전
  let plain = `안녕하세요. ${hospital} 원무팀 담당자님.\n\n`;
  plain += `[요양기관 청구 실패 내역 안내]\n`;
  const cleanIntro = introTextVal.replace(/\[size=\d+?\](.*?)\[\/size\]/g, '$1');
  plain += `${cleanIntro}\n\n`;
  plain += `■ ${hospital} - 청구 오류 내역\n\n`;
  
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

  // 지침 중복 제거 (Plain)
  const plainSeenInstructions = new Set<string>();
  let plainInstructions = '';
  categories.forEach(cat => {
    const inst = getInstruction(cat);
    if (inst !== '해당사항없음' && inst.trim() !== '') {
      const cleanInst = inst.replace(/\[size=\d+?\](.*?)\[\/size\]/g, '$1').trim();
      if (!plainSeenInstructions.has(cleanInst)) {
        plainSeenInstructions.add(cleanInst);
        const catErrors = errors.filter(e => normalizeCategoryName(e.category) === cat);
        plainInstructions += `- ${appendApiSuffix(cat, catErrors[0])}: ${cleanInst}\n`;
      }
    }
  });

  if (plainInstructions) {
    plain += `[오류별 조치 요령 안내]\n` + plainInstructions + `\n`;
  }
  plain += `확인 후 보정 회신을 요청드립니다.\n감사합니다.\n`;

  // 2) Rich HTML 버전 (카테고리별로 개별 표들을 각각 나누어 렌더링 - 왼쪽 이미지 형태)
  let htmlTables = '';
  categories.forEach((cat, catIdx) => {
    const catErrors = errors.filter(e => normalizeCategoryName(e.category) === cat);
    const htmlRows = catErrors.map((err, idx) => {
      const reasonVal = err.category && err.category.includes('(') ? err.category.split('(')[0].trim() : (err.category || '-');
      const detailsVal = (err.visitDate && err.visitDate !== '-' && err.uuid && err.uuid !== '-') 
        ? `진료일자: ${err.visitDate.replace(/-/g, '')} / UUID: ${err.uuid}` 
        : (err.details || '-');

      return `
      <tr style="height: 25px;">
        <td style="border: 1px solid #d9d9d9; padding: 8px 12px; text-align: center; color: #333;">${idx + 1}</td>
        <td style="border: 1px solid #d9d9d9; padding: 8px 12px; text-align: center; color: #333;">${err.institutionId || '-'}</td>
        <td style="border: 1px solid #d9d9d9; padding: 8px 12px; text-align: left; color: #333;">${err.hospital || '-'}</td>
        <td style="border: 1px solid #d9d9d9; padding: 8px 12px; text-align: center; color: #333;">${err.emr || '-'}</td>
        <td style="border: 1px solid #d9d9d9; padding: 8px 12px; text-align: left; color: #333;">${reasonVal}</td>
        <td style="border: 1px solid #d9d9d9; padding: 8px 12px; text-align: left; color: #555; word-break: break-all;">${detailsVal}</td>
      </tr>
      `;
    }).join('');

    htmlTables += `
    <div style="margin-top: 18px; margin-bottom: 6px; font-size: 13.5px; font-weight: bold; color: #333;">
      ■ 청구실패 사유: ${appendApiSuffix(cat, catErrors[0])}
    </div>
    <table style="width: 100%; border-collapse: collapse; border: 1px solid #a6a6a6; margin-bottom: 18px; font-size: 12px;">
      <thead>
        <tr style="background-color: #f2f2f2; color: #333333; height: 28px; font-weight: bold;">
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 40px; text-align: center;">No</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 90px; text-align: center;">병원기관번호</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 160px; text-align: center;">병원명</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 90px; text-align: center;">병원EMR</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; width: 170px; text-align: center;">청구실패사유</th>
          <th style="border: 1px solid #a6a6a6; padding: 5px; text-align: center;">진료내역 (진료일자 및 UUID)</th>
        </tr>
      </thead>
      <tbody>
        ${htmlRows}
      </tbody>
    </table>
    `;
  });

  // 지침 중복 제거 (HTML)
  const htmlSeenInstructions = new Set<string>();
  const guidelinesHtml = categories
    .map(cat => {
      const inst = getInstruction(cat);
      if (inst === '해당사항없음' || inst.trim() === '') return '';
      
      const normInst = inst.trim();
      if (htmlSeenInstructions.has(normInst)) return '';
      htmlSeenInstructions.add(normInst);
      
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
  <div style="background-color: #f2f5f8; border-left: 4px solid #1f4e78; padding: 12px 16px; margin: 15px 0; border-radius: 4px; font-size: 12px;">
    <ul style="margin: 0; padding-left: 18px; color: #444;">
      ${guidelinesHtml}
    </ul>
  </div>
  `;
  }

  let html = `<div style="font-family: '맑은 고딕', 'Malgun Gothic', sans-serif; font-size: 13px; line-height: 1.6; color: #333;">`;
  html += `<p>${formatTextToHtml(introTextVal)}</p>`;
  html += htmlGuidesSection;
  html += `<div style="margin-top: 25px; margin-bottom: 5px; font-size: 15px; font-weight: bold; color: #002060;">`;
  html += `  ■ ${hospital} - 청구 오류 내역 취합 현황`;
  html += `</div>`;
  html += htmlTables;
  html += `<p style="margin-top: 20px;">처리되시면 회신 부탁드립니다.<br>감사합니다.</p>`;
  html += `</div>`;

  return { plain, html };
}

// 대시보드 전체 복사 본문 빌더 포맷터 (기존 규격 호환용)
function formatClipboardText(hospital: string, institutionId: string, errors: any[]) {
  const introTextVal = localStorage.getItem('claim_intro_text') || '이메일 또는 메신저로 전달되는 자동화 문구입니다.';
  const customInstructionsVal: Record<string, string> = JSON.parse(localStorage.getItem('claim_custom_instructions') || '{}');
  
  const categories = Array.from(new Set(errors.map(e => normalizeCategoryName(e.category))));
  
  const getInstruction = (cat: string): string => {
    const normCat = normalizeCategoryName(cat);
    const custom = customInstructionsVal[normCat];
    if (custom !== undefined && custom !== null && custom.trim() !== '') {
      return custom.trim();
    }
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

  // 1) 일반 텍스트 버전
  let plain = `안녕하세요. ${hospital}입니다.\n\n`;
  plain += `[요양기관 청구 실패 내역 안내]\n`;
  const cleanIntro = introTextVal.replace(/\[size=\d+?\](.*?)\[\/size\]/g, '$1');
  plain += `${cleanIntro}\n\n`;
  plain += `■ ${hospital} - 청구 오류 내역 취합 현황\n\n`;
  
  categories.forEach((cat, catIdx) => {
    const catErrors = errors.filter(e => normalizeCategoryName(e.category) === cat);
    plain += `■ 청구실패 사유: ${cat}\n`;
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

  let plainInstructions = '';
  categories.forEach(cat => {
    const inst = getInstruction(cat);
    if (inst !== '해당사항없음') {
      const cleanInst = inst.replace(/\[size=\d+?\](.*?)\[\/size\]/g, '$1');
      plainInstructions += `- ${cat}: ${cleanInst}\n`;
    }
  });

  if (plainInstructions) {
    plain += `[오류별 조치 요령 안내]\n` + plainInstructions + `\n`;
  }
  plain += `감사합니다.\n`;

  // 2) Rich HTML 버전
  let htmlTables = '';
  categories.forEach((cat, catIdx) => {
    const catErrors = errors.filter(e => normalizeCategoryName(e.category) === cat);
    const htmlRows = catErrors.map((err, idx) => {
      const reasonVal = err.category && err.category.includes('(') ? err.category.split('(')[0].trim() : (err.category || '-');
      const detailsVal = (err.visitDate && err.visitDate !== '-' && err.uuid && err.uuid !== '-') 
        ? `진료일자: ${err.visitDate.replace(/-/g, '')} / UUID: ${err.uuid}` 
        : (err.details || '-');

      return `
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
  <div style="margin-top: 20px; margin-bottom: 8px; font-size: 14px; font-weight: bold; color: #333;">
    ■ 청구실패 사유: ${cat}
  </div>
  <table style="width: 100%; border-collapse: collapse; border: 1px solid #a6a6a6; margin-bottom: 20px; font-size: 11px;">
    <thead>
      <tr style="background-color: #f2f2f2; color: #333333; height: 28px; font-weight: bold;">
        <th style="border: 1px solid #a6a6a6; padding: 5px; width: 40px; text-align: center;">No</th>
        <th style="border: 1px solid #a6a6a6; padding: 5px; width: 90px; text-align: center;">병원기관번호</th>
        <th style="border: 1px solid #a6a6a6; padding: 5px; width: 160px; text-align: center;">병원명</th>
        <th style="border: 1px solid #a6a6a6; padding: 5px; width: 90px; text-align: center;">병원EMR</th>
        <th style="border: 1px solid #a6a6a6; padding: 5px; width: 170px; text-align: center;">청구실패사유</th>
        <th style="border: 1px solid #a6a6a6; padding: 5px; text-align: center;">진료내역 (진료일자 및 UUID)</th>
      </tr>
    </thead>
    <tbody>
      ${htmlRows}
    </tbody>
  </table>
  `;
  });

  const guidelinesHtml = categories
    .map(cat => {
      const inst = getInstruction(cat);
      if (inst === '해당사항없음') return '';
      return `
    <li style="margin-bottom: 6px;">
      <strong>${cat}</strong><br> ${formatTextToHtml(inst)}
    </li>`;
    })
    .filter(Boolean)
    .join('');

  let htmlGuidesSection = '';
  if (guidelinesHtml) {
    htmlGuidesSection = `
  <div style="background-color: #f2f5f8; border-left: 4px solid #1f4e78; padding: 12px 16px; margin: 15px 0; border-radius: 4px; font-size: 12px;">
    <ul style="margin: 0; padding-left: 18px; color: #444;">
      ${guidelinesHtml}
    </ul>
  </div>
  `;
  }

  let html = `<div style="font-family: '맑은 고딕', 'Malgun Gothic', sans-serif; font-size: 13px; line-height: 1.6; color: #333;">`;
  html += `<p>${formatTextToHtml(introTextVal)}</p>`;
  html += htmlGuidesSection;
  html += `<div style="margin-top: 25px; margin-bottom: 5px; font-size: 16px; font-weight: bold; color: #002060;">`;
  html += `  ■ ${hospital} - 청구 오류 내역 취합 현황`;
  html += `</div>`;
  html += htmlTables;
  html += `<p style="margin-top: 20px;">처리되시면 회신 부탁드립니다.<br>감사합니다.</p>`;
  html += `</div>`;

  return { plain, html };
}

onMounted(() => {
  loadExcelData();
});
</script>

<style scoped>
/* 구글 폰트 및 Pretendard 적용 */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.dashboard-wrapper {
  width: 100%;
  margin: 0 auto;
  font-family: 'Plus Jakarta Sans', 'Pretendard', sans-serif;
}

.error-monitor-section {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: 100vh;
}

/* 프리미엄 카드 디자인 */
.table-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px !important;
  border: 1px solid rgba(226, 232, 240, 0.8) !important;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.04), 0 1px 1px rgba(0, 0, 0, 0.01) !important;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.table-card-title {
  font-size: 15px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.3px;
}

.table-card-header {
  border-bottom: 1px solid #f1f5f9;
  background-color: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
}

.field-label {
  font-size: 13px;
  font-weight: 700;
  color: #475569;
  letter-spacing: -0.2px;
}

/* 인풋창 스타일링 */
.sleek-input {
  width: 100%;
  height: 40px;
  box-sizing: border-box;
  padding: 8px 14px;
  font-size: 13.5px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background-color: #f8fafc;
  outline: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02);
}
.sleek-input:focus {
  border-color: #4f46e5;
  background-color: #ffffff;
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.15), inset 0 1px 1px rgba(0, 0, 0, 0.01);
}

/* 차수 선택 셀렉트 박스 */
.sleek-select {
  appearance: none;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  padding: 6px 36px 6px 14px;
  font-size: 13px;
  font-weight: 700;
  color: #334155;
  outline: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23475569' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19.5 8.25l-7.5 7.5-7.5-7.5'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 14px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  height: 38px;
}
.sleek-select:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.15);
}

/* 안내 배너 박스 */
.info-alert-box {
  background-color: #eff6ff;
  border-left: 4px solid #3b82f6;
  padding: 12px 16px;
  border-radius: 8px;
}

.bg-blue-light {
  background-color: #f0f7ff !important;
  border-left: 4px solid #3b82f6 !important;
}

/* 슬라이딩 캡슐 형태의 네비게이션 탭 (Vercel/Stripe 스타일) */
.custom-nav-tabs {
  display: inline-flex;
  background-color: #e2e8f0;
  padding: 6px;
  border-radius: 12px;
  gap: 4px;
  border: 1px solid #cbd5e1;
}
.nav-tab-btn {
  border: none;
  background: transparent;
  padding: 8px 18px;
  font-size: 13.5px;
  font-weight: 700;
  color: #475569;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  display: flex;
  align-items: center;
}
.nav-tab-btn:hover {
  color: #0f172a;
  background-color: rgba(255, 255, 255, 0.4);
}
.nav-tab-btn.active {
  color: #4f46e5;
  background-color: #ffffff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
}

/* 검색 박스 */
.search-box {
  width: 220px;
}
.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}
.search-input-icon {
  position: absolute;
  left: 12px;
  color: #64748b;
  font-size: 17px !important;
  pointer-events: none;
}
.sleek-search-input {
  width: 100%;
  height: 36px;
  box-sizing: border-box;
  padding: 6px 12px 6px 36px;
  font-size: 12.5px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background-color: #f8fafc;
  color: #1e293b;
  outline: none;
  transition: all 0.3s ease;
}
.sleek-search-input:focus {
  border-color: #4f46e5;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12);
}

/* 프리미엄 테이블 스타일링 */
.dashboard-table {
  width: 100%;
  border-collapse: collapse;
}
.dashboard-table th {
  background-color: #f8fafc;
  font-size: 11.5px;
  font-weight: 800;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e2e8f0;
  padding: 14px 18px;
}
.dashboard-table td {
  padding: 10px 18px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 13px;
  color: #334155;
  vertical-align: middle;
}
.dashboard-table tbody tr {
  transition: background-color 0.2s ease;
}
.dashboard-table tbody tr:hover {
  background-color: rgba(241, 245, 249, 0.5) !important;
}

/* 테이블 내부 이메일 입력 박스 */
.table-cell-input {
  width: 100%;
  height: 32px;
  box-sizing: border-box;
  padding: 0 12px;
  font-size: 12.5px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background-color: #f8fafc;
  outline: none;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
}
.table-cell-input:focus {
  border-color: #3b82f6;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

/* 프리미엄 커스텀 체크박스 */
.custom-checkbox {
  appearance: none;
  width: 18px;
  height: 18px;
  border: 2px solid #cbd5e1;
  border-radius: 5px;
  outline: none;
  background-color: #ffffff;
  cursor: pointer;
  position: relative;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-block;
  vertical-align: middle;
}
.custom-checkbox:hover {
  border-color: #94a3b8;
}
.custom-checkbox:checked {
  border-color: #4f46e5;
  background-color: #4f46e5;
}
.custom-checkbox:checked::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 1.5px;
  width: 5px;
  height: 9px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

/* EMR사별 맞춤형 컬러 배지 스타일 */
.emr-tag-badge {
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 800;
  box-sizing: border-box;
}
.emr-tag-badge.emr-unassigned {
  background-color: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
}
.emr-tag-badge.emr-integration {
  background-color: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}
.emr-tag-badge.emr-eone {
  background-color: #f5f3ff;
  color: #7c3aed;
  border: 1px solid #ddd6fe;
}
.emr-tag-badge.emr-default {
  background-color: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}

.text-red {
  color: #ef4444;
}

/* 액션 버튼 고정 스타일 */
.sleek-btn {
  border: 1px solid transparent;
  background-color: #f1f5f9;
  color: #475569;
  font-size: 11.5px;
  font-weight: 700;
  height: 32px;
  padding: 0 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}
.sleek-btn:hover {
  background-color: #e2e8f0;
  transform: translateY(-1px);
}
.sleek-btn-primary-outline {
  border-color: #e2e8f0;
  background-color: #f8fafc;
  color: #4f46e5;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}
.sleek-btn-primary-outline:hover {
  background-color: #4f46e5;
  color: #ffffff;
  border-color: #4f46e5;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
}
.sleek-btn-info-outline {
  border-color: #e2e8f0;
  background-color: #ffffff;
  color: #475569;
}
.sleek-btn-info-outline:hover {
  background-color: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
}

/* ==========================================================================
   복사 도우미 다이얼로그 전용 프리미엄 스타일
   ========================================================================== */
.copy-helper-card {
  font-family: 'Pretendard', sans-serif !important;
  border-radius: 16px !important;
  background-color: #ffffff !important;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15) !important;
}

.copy-helper-header {
  border-bottom: 1px solid #f1f5f9;
  padding: 18px 24px !important;
  background-color: #ffffff;
}

.copy-helper-body {
  padding: 0 !important;
}

/* 본문 자동 복사 안내 띠 배너 */
.clipboard-toast-banner {
  background-color: #ecfdf5 !important;
  border-bottom: 1px solid #a7f3d0 !important;
}

.helper-banner {
  display: flex;
  background-color: #eff6ff;
  border-left: 4px solid #3b82f6;
  border-radius: 8px;
  padding: 12px 16px;
  color: #1e3a8a;
}

.field-title {
  font-size: 13px;
  font-weight: 700;
  color: #475569;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  letter-spacing: -0.3px;
  margin-bottom: 6px;
}

/* 프리미엄 인라인 복사형 인풋 그룹 */
.sleek-input-group {
  display: flex;
  position: relative;
  border: 1px solid #cbd5e1;
  background-color: #f8fafc;
  border-radius: 10px;
  overflow: hidden;
  height: 42px;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02);
}
.sleek-input-group:hover {
  border-color: #cbd5e1;
  background-color: #f1f5f9;
}
.sleek-input-group:focus-within {
  border-color: #4f46e5;
  background-color: #ffffff;
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.15), inset 0 1px 1px rgba(0, 0, 0, 0.01);
}

.helper-read-input {
  border: none !important;
  background: transparent !important;
  outline: none !important;
  height: 100%;
  padding: 8px 14px;
  font-size: 13.5px;
  font-weight: 600;
  color: #1e293b;
  font-family: 'Pretendard', sans-serif;
  letter-spacing: -0.2px;
}

.input-inline-btn {
  background: #ffffff;
  border: none;
  border-left: 1px solid #cbd5e1;
  color: #64748b;
  width: 44px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}
.input-inline-btn:hover {
  background-color: #4f46e5;
  color: #ffffff;
  border-left-color: #4f46e5;
}
.input-inline-btn:active {
  transform: scale(0.92);
}

.helper-read-textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 12px;
  font-size: 12.5px;
  font-family: 'Fira Code', Consolas, Monaco, monospace;
  line-height: 1.5;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background-color: #f8fafc;
  outline: none;
  color: #334155;
  resize: none;
  transition: all 0.3s ease;
}
.helper-read-textarea:focus {
  border-color: #4f46e5;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12);
}

.copy-helper-footer {
  background-color: #f8fafc;
  border-top: 1px solid #e2e8f0;
  padding: 16px 24px !important;
}

.helper-read-html {
  width: 100%;
  max-height: 350px;
  overflow-y: auto;
  box-sizing: border-box;
  padding: 20px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  background-color: #ffffff;
  outline: none;
  font-size: 13px;
  line-height: 1.6;
  color: #334155;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  font-family: 'Pretendard', sans-serif !important;
  transition: border-color 0.3s ease;
}
.helper-read-html:hover {
  border-color: #cbd5e1;
}

.helper-read-html::-webkit-scrollbar {
  width: 6px;
}
.helper-read-html::-webkit-scrollbar-track {
  background: #f8fafc;
}
.helper-read-html::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
.helper-read-html::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 내부 렌더링 테이블 스타일 조정 */
.helper-read-html :deep(table) {
  width: 100% !important;
  border-collapse: collapse !important;
  font-size: 12px !important;
  margin: 16px 0 !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
  font-family: 'Pretendard', sans-serif !important;
}
.helper-read-html :deep(th) {
  background-color: #1f4e78 !important;
  color: #ffffff !important;
  padding: 8px 12px !important;
  border: 1px solid #a6a6a6 !important;
  text-align: center !important;
  font-weight: bold !important;
  font-size: 12px !important;
}
.helper-read-html :deep(td) {
  border: 1px solid #d9d9d9 !important;
  padding: 8px 12px !important;
  color: #333333 !important;
  background-color: #ffffff !important;
  font-size: 12px !important;
  word-break: break-all !important;
  line-height: 1.5 !important;
}
.helper-read-html :deep(ul) {
  margin: 0 !important;
  padding-left: 18px !important;
}
.helper-read-html :deep(li) {
  margin-bottom: 4px !important;
}

.border-r {
  border-right: 1px solid #cbd5e1;
}

/* 요양기관별 필터링 전용 스타일 */
.mini-text-btn {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  padding: 2px 4px;
}
.mini-text-btn:hover {
  text-decoration: underline;
}

.error-selection-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 520px;
  overflow-y: auto;
  padding-right: 4px;
}

.error-select-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}
.error-select-card:hover {
  background-color: #f1f5f9;
  border-color: #cbd5e1;
}
.error-select-card.active {
  background-color: #eff6ff;
  border-color: #bfdbfe;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.04);
}

.error-count-tag {
  background-color: #e2e8f0;
  color: #334155;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  line-height: 1;
}

/* ==========================================================================
   EMR 듀얼 리스트 전용 스타일 (픽리스트)
   ========================================================================== */
.list-container-card {
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  overflow: hidden;
  background-color: #ffffff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.target-list-border {
  border-color: #3b82f6;
}

.list-container-header {
  padding: 12px 16px;
  border-bottom: 1px solid #cbd5e1;
}

.list-title {
  font-size: 13.5px;
}

.list-body-scroll {
  height: 250px;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background-color: #fafbfd;
}

.transfer-item-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
  transition: all 0.2s;
}
.transfer-item-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
  border-color: #cbd5e1;
}

.transfer-item-card.target-card {
  background-color: #f0f7ff;
  border-color: #bfdbfe;
}
.transfer-item-card.target-card:hover {
  border-color: #3b82f6;
  background-color: #e0f2fe;
}

.empty-list-placeholder {
  text-align: center;
  padding-top: 80px;
  font-size: 12.5px;
  color: #94a3b8;
}

.transfer-arrow-icon {
  background-color: #f1f5f9;
  width: 50px;
  height: 50px;
  border-radius: 100px;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
</style>
