const ExcelJS = require('exceljs');
const path = require('path');
const fs = require('fs');

const FILES_DIR = path.join(__dirname, '../../public/files');
const defaultHospital = '알 수 없는 병원';

// ==========================================================================
// Parsing & Normalization Helpers (Internal)
// ==========================================================================

function isHeaderRow(rowValues) {
  const normalized = rowValues.map((cell) => (cell ? String(cell).trim().toLowerCase() : ''));
  const known = [
    'no', 'timestamp', 'time', 'date', 'endpoint', 'api', 'status', 'errorcode', 'error code', 'retry', 'category', 'hospital', 'patient',
    '기관번호', '병원기관번호', '병원명', 'emr사', '병원emr', '피보험자', '생년월일', '청구실패사유', '청구실패 사유', '진료내역', '진료내역 (진료일자 및 uuid)', '진료 내역 (진료일자 및 uuid)',
    '이름', '환자명', '환자', '피보험자명', '생년'
  ];
  const score = normalized.filter((value) => known.includes(value)).length;
  return score >= 2;
}

function normalizeHeaderValue(value) {
  if (typeof value !== 'string') return '';
  const normalized = value.trim().toLowerCase();
  const map = {
    no: 'no',
    '기관번호': 'institutionId',
    '병원기관번호': 'institutionId',
    '병원명': 'hospital',
    'emr사': 'emr',
    '병원emr': 'emr',
    '청구실패사유': 'category',
    '청구실패 사유': 'category',
    '진료내역': 'details',
    '진료내역 (진료일자 및 uuid)': 'details',
    '진료 내역 (진료일자 및 uuid)': 'details',
    '피보험자': 'patient',
    '피보험자명': 'patient',
    '환자명': 'patient',
    '환자': 'patient',
    '이름': 'patient',
    '생년월일': 'birthDate',
    '생년': 'birthDate',
    '진행상태': 'state',
    '상태': 'state',
  };

  if (map[normalized]) return map[normalized];
  if (normalized.includes('진료') && normalized.includes('uuid')) return 'details';
  if (normalized.includes('청구실패') && normalized.includes('사유')) return 'category';
  return normalized;
}

function normalizeSectionCategory(value) {
  let text = value.trim();
  // 바깥쪽 대괄호 [ ] 껍질 제거
  if (text.startsWith('[') && text.endsWith(']')) {
    text = text.substring(1, text.length - 1).trim();
  }
  const match = text.match(/청구실패\s*사유\s*[:：]?\s*(.*)$/i);
  if (match && match[1]) {
    let res = match[1].trim();
    if (res.endsWith(']')) res = res.substring(0, res.length - 1).trim();
    return res;
  }
  const cleaned = text.replace(/^\?+\s*/g, '').trim();
  return cleaned || '미분류';
}

function parseVisitDate(detail) {
  if (!detail) return '-';
  const matchSep = detail.match(/일자\s*[:：]?\s*([0-9]{4})[-./]([0-9]{2})[-./]([0-9]{2})/);
  if (matchSep) {
    return `${matchSep[1]}-${matchSep[2]}-${matchSep[3]}`;
  }
  const matchNoSep = detail.match(/일자\s*[:：]?\s*([0-9]{4})([0-9]{2})([0-9]{2})/);
  if (matchNoSep) {
    return `${matchNoSep[1]}-${matchNoSep[2]}-${matchNoSep[3]}`;
  }
  return '-';
}

function extractUuid(detail) {
  if (!detail) return '-';
  const match = detail.match(/UUID\s*[:：]?\s*([A-Za-z0-9-]+)/i);
  return match ? match[1].trim() : '-';
}

function parsePatientName(details, rawPatient) {
  if (rawPatient && rawPatient !== '-') return rawPatient;
  if (!details) return '-';
  const match = details.match(/피보험자\s*[:：]?\s*([^\s/|]+)/);
  return match ? match[1].trim() : '-';
}

function parseBirthDate(details, rawBirthDate) {
  if (rawBirthDate && rawBirthDate !== '-') return rawBirthDate;
  if (!details) return '-';
  const match = details.match(/생년월일\s*[:：]?\s*([^\s/|]+)/);
  return match ? match[1].trim() : '-';
}

function getCellValueAsString(value) {
  if (value === undefined || value === null) return '';
  if (typeof value === 'object') {
    if (value.richText && Array.isArray(value.richText)) {
      return value.richText.map(t => t.text || '').join('').trim();
    }
    if (value.text !== undefined) {
      return String(value.text).trim();
    }
    if (value.result !== undefined) {
      return getCellValueAsString(value.result);
    }
    return String(JSON.stringify(value)).trim();
  }
  return String(value).trim();
}

function buildRowObject(headers, rowValues) {
  return headers.reduce((acc, header, index) => {
    if (header) {
      acc[header] = getCellValueAsString(rowValues[index]);
    }
    return acc;
  }, {});
}

function hasSeparatorPattern(cell) {
  if (cell === undefined || cell === null) return false;
  let str = '';
  if (typeof cell === 'object') {
    if (cell.richText) {
      str = cell.richText.map(t => t.text || '').join('');
    } else if (cell.text) {
      str = cell.text;
    } else if (cell.result !== undefined) {
      str = String(cell.result);
    } else {
      str = JSON.stringify(cell);
    }
  } else {
    str = String(cell);
  }
  return str.includes('===') || str.includes('---');
}

// ==========================================================================
// Service Methods (Exports)
// ==========================================================================

async function getExcelFilesList() {
  if (!fs.existsSync(FILES_DIR)) {
    fs.mkdirSync(FILES_DIR, { recursive: true });
  }

  const files = fs.readdirSync(FILES_DIR)
    .filter(file => file.endsWith('.xlsx') && !file.startsWith('~$'))
    .map(file => file.replace('.xlsx', ''));

  files.sort((a, b) => b.localeCompare(a));
  return files;
}

async function parseExcelFile(fileKey) {
  const filePath = path.join(FILES_DIR, `${fileKey}.xlsx`);

  if (!fs.existsSync(filePath)) {
    const err = new Error('Excel file not found');
    err.status = 404;
    throw err;
  }

  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);

  const loadedRows = [];

  workbook.worksheets.forEach((worksheet) => {
    const sheetName = worksheet.name;
    let headers = [];
    let currentCategory = '';

    worksheet.eachRow({ includeEmpty: false }, (row, rowIndex) => {
      const rawValues = [];
      const maxCol = Math.max(worksheet.columnCount || 0, worksheet.actualColumnCount || 0, 15);
      for (let colNum = 1; colNum <= maxCol; colNum++) {
        const val = row.getCell(colNum).value;
        rawValues.push(val === undefined ? null : val);
      }

      if (rawValues.length === 0) return;
      if (rawValues.every(cell => cell === undefined || cell === null || cell === '')) return;
      if (rawValues.some(hasSeparatorPattern)) return;

      const firstCell = typeof rawValues[0] === 'string' ? rawValues[0].trim() : '';

      if (/청구실패\s*사유/i.test(firstCell)) {
        currentCategory = normalizeSectionCategory(firstCell);
        headers = [];
        return;
      }

      if (isHeaderRow(rawValues)) {
        headers = rawValues.map(normalizeHeaderValue);
        return;
      }

      if (!headers.length) return;

      const rowObject = buildRowObject(headers, rawValues);

      const hospital = rowObject.hospital ? String(rowObject.hospital).trim() : sheetName.trim() || defaultHospital;
      const institutionId = rowObject.institutionId ? String(rowObject.institutionId).trim() : '-';
      const emr = rowObject.emr && String(rowObject.emr).trim() !== '' ? String(rowObject.emr).trim() : '미지정';
      const category = currentCategory || (rowObject.category ? String(rowObject.category).trim() : '미분류');
      const details = rowObject.details ? String(rowObject.details).trim() : '-';
      const api = rowObject.api ? String(rowObject.api).trim() : (rowObject.endpoint ? String(rowObject.endpoint).trim() : '');

      const visitDate = parseVisitDate(details);
      const uuid = extractUuid(details);

      const rawPatient = rowObject.patient ? String(rowObject.patient).trim() : '-';
      const rawBirthDate = rowObject.birthDate ? String(rowObject.birthDate).trim() : '-';

      const patient = parsePatientName(details, rawPatient);
      const birthDate = parseBirthDate(details, rawBirthDate);

      const state = (rowObject.state && ['미확인', '회신대기', '최종완료'].includes(rowObject.state)) 
        ? rowObject.state 
        : '미확인';

      const no = rowObject.no ? Number(rowObject.no) : rowIndex;

      loadedRows.push({
        no,
        fileKey,
        sheetName: String(sheetName || '').trim(),
        hospital,
        institutionId,
        emr,
        category,
        details,
        visitDate,
        uuid,
        patient,
        birthDate,
        state,
        api
      });
    });
  });

  return loadedRows;
}

async function updateClaimState(fileKey, hospital, category, state, targetRows) {
  const filePath = path.join(FILES_DIR, `${fileKey}.xlsx`);
  if (!fs.existsSync(filePath)) {
    const err = new Error(`지정한 엑셀 파일(${fileKey})을 찾을 수 없습니다.`);
    err.status = 404;
    throw err;
  }

  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);

  const targetSheetName = (targetRows && targetRows[0] && targetRows[0].sheetName)
    ? targetRows[0].sheetName
    : hospital;

  let worksheet = workbook.getWorksheet(targetSheetName) || workbook.getWorksheet(targetSheetName.trim());
  if (!worksheet) {
    worksheet = workbook.worksheets.find(ws => ws.name.trim().toLowerCase() === targetSheetName.trim().toLowerCase())
        || workbook.worksheets.find(ws => ws.name.trim().toLowerCase() === hospital.trim().toLowerCase())
        || workbook.worksheets[0];
  }

  if (!worksheet) {
    const err = new Error(`${targetSheetName}에 해당하는 시트를 엑셀에서 찾을 수 없습니다.`);
    err.status = 404;
    throw err;
  }

  let isUpdated = false;
  let headers = [];
  let currentCategory = '';
  const targetStateColIndex = 8; // H열 고정

  worksheet.eachRow({ includeEmpty: false }, (row, rowIndex) => {
    const rawValues = [];
    const maxCol = Math.max(worksheet.columnCount || 0, worksheet.actualColumnCount || 0, 15);
    for (let colNum = 1; colNum <= maxCol; colNum++) {
      const val = row.getCell(colNum).value;
      rawValues.push(val === undefined ? null : val);
    }

    if (rawValues.length === 0) return;
    if (rawValues.some(hasSeparatorPattern)) return;

    const firstCell = typeof rawValues[0] === 'string' ? rawValues[0].trim() : '';

    if (/청구실패\s*사유/i.test(firstCell)) {
      currentCategory = normalizeSectionCategory(firstCell);
      headers = [];
      return;
    }

    if (isHeaderRow(rawValues)) {
      headers = rawValues.map(normalizeHeaderValue);

      const headerCell = row.getCell(targetStateColIndex);
      headerCell.value = '진행상태';
      headerCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFC8E6C9' } };
      headerCell.font = { name: '맑은 고딕', size: 11, bold: true, color: { argb: 'FF2E7D32' } };
      headerCell.alignment = { horizontal: 'center', vertical: 'middle' };
      row.commit();
      return;
    }

    if (!headers.length) return;

    const rowObject = buildRowObject(headers, rawValues);
    const rowPatient = parsePatientName(rowObject.details, rowObject.patient ? String(rowObject.patient).trim() : '-');
    const rowBirthDate = parseBirthDate(rowObject.details, rowObject.birthDate ? String(rowObject.birthDate).trim() : '-');
    const rowCategory = currentCategory || (rowObject.category ? String(rowObject.category).trim() : '미분류');

    const isMatch = targetRows && Array.isArray(targetRows) && targetRows.some(tRow => {
      return (
          tRow.patient === rowPatient &&
          tRow.birthDate === rowBirthDate &&
          tRow.category === rowCategory
      );
    });

    if (isMatch) {
      const stateCell = row.getCell(targetStateColIndex);
      stateCell.value = state;
      stateCell.alignment = { horizontal: 'center', vertical: 'middle' };
      stateCell.font = { name: '맑은 고딕', size: 10, bold: state === '최종완료' };

      row.commit();
      isUpdated = true;
    }
  });

  if (isUpdated) {
    worksheet.getColumn(targetStateColIndex).width = 14;
    await workbook.xlsx.writeFile(filePath);
    return { success: true, message: `H열 상태가 [${state}]로 일괄 갱신되었습니다.` };
  } else {
    const err = new Error('엑셀 내부에서 매칭되는 청구 대상을 찾지 못했습니다.');
    err.status = 404;
    throw err;
  }
}

async function updateClaimStateMultiple(fileKey, state, updates) {
  const filePath = path.join(FILES_DIR, `${fileKey}.xlsx`);
  if (!fs.existsSync(filePath)) {
    const err = new Error(`지정한 엑셀 파일(${fileKey})을 찾을 수 없습니다.`);
    err.status = 404;
    throw err;
  }

  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);

  let anyUpdated = false;

  for (const update of updates) {
    const { hospital, rows: targetRows } = update;
    const targetSheetName = (targetRows && targetRows[0] && targetRows[0].sheetName)
      ? targetRows[0].sheetName
      : hospital;

    let worksheet = workbook.getWorksheet(targetSheetName) || workbook.getWorksheet(targetSheetName.trim());
    if (!worksheet) {
      worksheet = workbook.worksheets.find(ws => ws.name.trim().toLowerCase() === targetSheetName.trim().toLowerCase())
          || workbook.worksheets.find(ws => ws.name.trim().toLowerCase() === hospital.trim().toLowerCase())
          || workbook.worksheets[0];
    }

    if (!worksheet) continue;

    let headers = [];
    let currentCategory = '';
    const targetStateColIndex = 8; // H열 고정

    worksheet.eachRow({ includeEmpty: false }, (row, rowIndex) => {
      const rawValues = [];
      const maxCol = Math.max(worksheet.columnCount || 0, worksheet.actualColumnCount || 0, 15);
      for (let colNum = 1; colNum <= maxCol; colNum++) {
        const val = row.getCell(colNum).value;
        rawValues.push(val === undefined ? null : val);
      }

      if (rawValues.length === 0) return;
      if (rawValues.some(hasSeparatorPattern)) return;

      const firstCell = typeof rawValues[0] === 'string' ? rawValues[0].trim() : '';

      if (/청구실패\s*사유/i.test(firstCell)) {
        currentCategory = normalizeSectionCategory(firstCell);
        headers = [];
        return;
      }

      if (isHeaderRow(rawValues)) {
        headers = rawValues.map(normalizeHeaderValue);

        const headerCell = row.getCell(targetStateColIndex);
        headerCell.value = '진행상태';
        headerCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFC8E6C9' } };
        headerCell.font = { name: '맑은 고딕', size: 11, bold: true, color: { argb: 'FF2E7D32' } };
        headerCell.alignment = { horizontal: 'center', vertical: 'middle' };
        row.commit();
        return;
      }

      if (!headers.length) return;

      const rowObject = buildRowObject(headers, rawValues);
      const rowPatient = parsePatientName(rowObject.details, rowObject.patient ? String(rowObject.patient).trim() : '-');
      const rowBirthDate = parseBirthDate(rowObject.details, rowObject.birthDate ? String(rowObject.birthDate).trim() : '-');
      const rowCategory = currentCategory || (rowObject.category ? String(rowObject.category).trim() : '미분류');

      const isMatch = targetRows && Array.isArray(targetRows) && targetRows.some(tRow => {
        return (
            tRow.patient === rowPatient &&
            tRow.birthDate === rowBirthDate &&
            tRow.category === rowCategory
        );
      });

      if (isMatch) {
        const stateCell = row.getCell(targetStateColIndex);
        stateCell.value = state;
        stateCell.alignment = { horizontal: 'center', vertical: 'middle' };
        stateCell.font = { name: '맑은 고딕', size: 10, bold: state === '최종완료' };

        row.commit();
        anyUpdated = true;
      }
    });

    if (anyUpdated) {
      worksheet.getColumn(targetStateColIndex).width = 14;
    }
  }

  if (anyUpdated) {
    await workbook.xlsx.writeFile(filePath);
    return { success: true, message: `선택된 병원들의 진행상태가 [${state}]로 일괄 갱신되었습니다.` };
  } else {
    const err = new Error('엑셀 내부에서 매칭되는 대상을 찾지 못했습니다.');
    err.status = 404;
    throw err;
  }
}

async function sendMailViaSmtp(to, cc, subject, body) {
  let nodemailer;
  try {
    nodemailer = require('nodemailer');
  } catch (e) {
    const err = new Error("백엔드에 nodemailer 모듈이 설치되어 있지 않습니다. backend 폴더에서 'npm install'을 실행해 주세요.");
    err.status = 500;
    throw err;
  }
  const user = process.env.NAVER_USER;
  const pass = process.env.NAVER_PASS;

  if (!user || !pass) {
    console.warn('NAVER_USER 또는 NAVER_PASS 환경변수가 설정되지 않아 시뮬레이션 모드로 작동합니다.');
    return {
      success: true,
      simulated: true,
      message: '시뮬레이션 전송에 성공했습니다. (.env 에 NAVER_USER, NAVER_PASS 설정 시 실제 발송됩니다.)'
    };
  }

  const transporter = nodemailer.createTransport({
    host: 'smtp.naver.com',
    port: 465,
    secure: true, // SSL 사용
    auth: { user, pass }
  });

  const mailOptions = {
    from: user, // 네이버는 로그인한 본인 계정만 보낸사람으로 지정 가능
    to,
    cc,
    subject,
    text: body
  };

  await transporter.sendMail(mailOptions);
  return { success: true, message: '네이버 SMTP를 통해 메일이 성공적으로 발송되었습니다.' };
}

// 백그라운드 크롬 디버깅 포트(8080) 브라우저 자동 기입 로직 (네이티브 Node.js Puppeteer 이식)
async function executeMailPopupAutomation(mailList) {
  const puppeteer = require('puppeteer-core');
  
  let browser;
  try {
    console.log('[Express Automation] Connecting to Chrome debugger at port 8080...');
    browser = await puppeteer.connect({
      browserURL: 'http://127.0.0.1:8080',
      defaultViewport: null
    });
    console.log('✅ Connected to Chrome successfully!');
  } catch (err) {
    console.error('❌ Failed to connect to Chrome at port 8080:', err);
    throw new Error('포트 8080으로 실행된 크롬 브라우저를 찾을 수 없습니다. 크롬을 완전히 종료 후 디버깅 모드(--remote-debugging-port=8080)로 다시 실행해 주세요.');
  }

  // 1) 하이웍스 도메인 동적 자동 감지 (사용자가 열어둔 탭 탐색)
  let detectedHiworksDomain = 'https://mails.office.hiworks.com';
  try {
    const pages = await browser.pages();
    for (const page of pages) {
      const url = page.url();
      if (url.includes('mails.office.hiworks.com')) {
        detectedHiworksDomain = 'https://mails.office.hiworks.com';
        console.log(`🔍 [하이웍스 감지] 신형 메일 플랫폼 감지: ${detectedHiworksDomain}`);
        break;
      } else if (url.includes('office.hiworks.com')) {
        const parts = url.split('/');
        if (parts.length >= 4) {
          detectedHiworksDomain = parts.slice(0, 4).join('/');
          console.log(`🔍 [하이웍스 감지] 구형 오피스 플랫폼 감지: ${detectedHiworksDomain}`);
          break;
        }
      }
    }
  } catch (err) {
    console.warn('⚠️ 하이웍스 도메인 탐색 중 실패 (폴백 사용):', err.message);
  }

  // 2) 개별 메일 팝업 창 생성 및 주입
  for (let idx = 0; idx < mailList.length; idx++) {
    const hosp = mailList[idx];
    const itemService = hosp.service || 'naver';
    
    let writeUrl = '';
    let isNaver = false;
    let isHiworks = false;
    let isOther = false;
    
    if (itemService === 'naver') {
      writeUrl = 'https://mail.naver.com/v2/popup/new';
      isNaver = true;
    } else if (itemService === 'hiworks') {
      const hDomain = hosp.hiworks_domain || detectedHiworksDomain;
      if (hDomain.includes('mails.office.hiworks.com')) {
        writeUrl = `${hDomain}/write?mode=normal`;
      } else {
        writeUrl = `${hDomain}/mail/write/`;
      }
      isHiworks = true;
    } else if (itemService === 'portal' || itemService === 'other') {
      const toVal = hosp.to ? hosp.to : 'silsonapi.dev@kidi.or.kr';
      const subjectVal = hosp.subject ? encodeURIComponent(hosp.subject) : 'undefined';
      writeUrl = `https://portal.kidi.or.kr/mail/userMail/goMailWindowWritePopup.do?uid=undefined&listSubject=undefined&folderNm=undefined&userMail=silsonapi.dev@kidi.or.kr&inputUserId=KIDI_silsonapi&messageId=undefined&popup=Y`;
      if (itemService === 'portal') isPortal = true;
      else isOther = true;
    }
    
    console.log(`📂 [${idx + 1}/${mailList.length}] ${hosp.hospital} 팝업 창 띄우는 중 (서비스: ${itemService}, 주소: ${writeUrl})...`);
    
    try {
      // 새 탭 생성 및 이동
      const page = await browser.newPage();
      
      // 네이버는 팝업 크기 조절 (Puppeteer viewport)
      if (isNaver) {
        await page.setViewport({ width: 1100, height: 750 });
      }
      
      await page.goto(writeUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
      
      // 주소창 로딩 대기
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      if (isNaver) {
        // [네이버 받는사람 입력]
        const toSelector = '#recipient_input_element, textarea[placeholder*="받는 사람"], input[placeholder*="받는 사람"], textarea[placeholder*="받는사람"]';
        try {
          await page.waitForSelector(toSelector, { timeout: 8000 });
          if (hosp.to && hosp.to.trim()) {
            const toEl = await page.$(toSelector);
            if (toEl) {
              await toEl.click();
              await toEl.type(hosp.to);
              await page.keyboard.press('Enter');
            }
          }
        } catch (e) {
          console.warn(`⚠️ [${hosp.hospital}] 네이버 받는사람 입력창 대기 시간 초과 또는 실패: ${e.message}`);
        }
        
        // [네이버 제목 입력]
        try {
          const subSelector = '#subject_title, input[placeholder*="제목"]';
          const subEl = await page.$(subSelector);
          if (subEl) {
            await subEl.click();
            await page.evaluate(el => el.value = '', subEl);
            await subEl.type(hosp.subject);
          }
        } catch (e) {
          console.warn(`⚠️ [${hosp.hospital}] 네이버 제목 주입 실패: ${e.message}`);
        }
        
        // [네이버 HTML 탭 클릭]
        let htmlBtnClicked = false;
        try {
          htmlBtnClicked = await page.evaluate(() => {
            const xpath = "//button[contains(., 'HTML')] | //span[contains(., 'HTML')] | //a[contains(., 'HTML')]";
            const res = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            const el = res.singleNodeValue;
            if (el) { el.click(); return true; }
            return false;
          });
        } catch (e) {}

        if (!htmlBtnClicked) {
          const frames = page.frames();
          for (const frame of frames) {
            try {
              htmlBtnClicked = await frame.evaluate(() => {
                const xpath = "//button[contains(., 'HTML')] | //span[contains(., 'HTML')] | //a[contains(., 'HTML')]";
                const res = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                const el = res.singleNodeValue;
                if (el) { el.click(); return true; }
                return false;
              });
              if (htmlBtnClicked) {
                console.log("👉 [HTML] 버튼 클릭 성공 (iframe 내부)");
                break;
              }
            } catch (e) {}
          }
        }
        
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // [네이버 HTML 소스 코드 입력창(textarea) 주입]
        let sourceInputFilled = false;
        const taSelector = "textarea[class*='source'], textarea[class*='editor'], textarea#ir1, textarea";
        
        try {
          const ta = await page.$(taSelector);
          if (ta) {
            await page.evaluate((el, val) => {
              el.value = val;
              el.dispatchEvent(new Event('change'));
            }, ta, hosp.html_body);
            sourceInputFilled = true;
          }
        } catch (e) {}

        if (!sourceInputFilled) {
          const frames = page.frames();
          for (const frame of frames) {
            try {
              const ta = await frame.$(taSelector);
              if (ta) {
                await frame.evaluate((el, val) => {
                  el.value = val;
                  el.dispatchEvent(new Event('change'));
                }, ta, hosp.html_body);
                sourceInputFilled = true;
                console.log("👉 HTML 소스 코드 주입 완료 (iframe 내부)");
                break;
              }
            } catch (e) {}
          }
        }

        await new Promise(resolve => setTimeout(resolve, 300));

        // [네이버 Editor 탭 복귀]
        let editorBtnClicked = false;
        try {
          editorBtnClicked = await page.evaluate(() => {
            const xpath = "//button[contains(., 'Editor')] | //span[contains(., 'Editor')] | //button[contains(., '에디터')] | //span[contains(., '에디터')]";
            const res = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            const el = res.singleNodeValue;
            if (el) { el.click(); return true; }
            return false;
          });
        } catch (e) {}

        if (!editorBtnClicked) {
          const frames = page.frames();
          for (const frame of frames) {
            try {
              editorBtnClicked = await frame.evaluate(() => {
                const xpath = "//button[contains(., 'Editor')] | //span[contains(., 'Editor')] | //button[contains(., '에디터')] | //span[contains(., '에디터')]";
                const res = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                const el = res.singleNodeValue;
                if (el) { el.click(); return true; }
                return false;
              });
              if (editorBtnClicked) {
                console.log("👉 [Editor] 버튼 복원 완료 (iframe 내부)");
                break;
              }
            } catch (e) {}
          }
        }
        
      } else if (isHiworks) {
        // [하이웍스 받는사람 입력]
        const toSelector = "input[placeholder*='구분하여 입력하세요'], input[class*='AddressInput_address-input'], input[name='to'], #mail_to_input";
        try {
          await page.waitForSelector(toSelector, { timeout: 8000 });
          if (hosp.to && hosp.to.trim()) {
            const toEl = await page.$(toSelector);
            if (toEl) {
              await toEl.click();
              await toEl.type(hosp.to);
              await page.keyboard.press('Enter');
            }
          }
        } catch (e) {
          console.warn(`⚠️ [${hosp.hospital}] 하이웍스 받는사람 입력 실패: ${e.message}`);
        }
        
        // [하이웍스 숨은참조 입력 (선택)]
        if (hosp.cc && hosp.cc.trim()) {
          try {
            // 1) 숨은참조 입력창이 현재 노출 상태인지 확인
            let bccVisible = await page.evaluate(() => {
              const xpath = "//*[contains(text(), '숨은참조')]/ancestor::tr//input[contains(@class, 'AddressInput_address-input')] | //th[contains(., '숨은참조')]/..//input | //*[contains(text(), '숨은참조')]/..//input";
              const res = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
              const el = res.singleNodeValue;
              return el && el.offsetWidth > 0 && el.offsetHeight > 0;
            });

            // 2) 숨겨져 있다면 활성화 버튼 클릭
            if (!bccVisible) {
              await page.evaluate(() => {
                const xpath = "//button[contains(., '숨은참조')] | //span[contains(., '숨은참조')] | //a[contains(., '숨은참조')]";
                const res = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                const el = res.singleNodeValue;
                if (el) el.click();
              });
              await new Promise(resolve => setTimeout(resolve, 300));
            }

            // 3) 다시 숨은참조 입력창 타겟팅 및 입력
            await page.evaluate((ccValue) => {
              const xpath = "//*[contains(text(), '숨은참조')]/ancestor::tr//input[contains(@class, 'AddressInput_address-input')] | //th[contains(., '숨은참조')]/..//input | //*[contains(text(), '숨은참조')]/..//input";
              const res = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
              let el = res.singleNodeValue;
              
              if (!el) {
                const addrInputs = document.querySelectorAll("input[class*='AddressInput_address-input']");
                if (addrInputs.length > 2) {
                  el = addrInputs[2];
                } else if (addrInputs.length > 1) {
                  el = addrInputs[1];
                }
              }
              
              if (el) {
                el.focus();
                el.value = ccValue;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
              }
              return false;
            }, hosp.cc);
            
            await page.keyboard.press('Enter');
            console.log("👉 하이웍스 숨은참조(BCC) 주입 완료");
          } catch (ccErr) {
            console.warn('⚠️ 하이웍스 숨은참조(BCC) 입력 실패:', ccErr.message);
          }
        }
        
        // [하이웍스 제목 입력]
        try {
          const subSelector = "input[class*='Input_input-right-padding'], input[class*='Input_input__'], input[name='subject'], #mail_subject_input";
          const subEl = await page.$(subSelector);
          if (subEl) {
            await subEl.click();
            await page.evaluate(el => el.value = '', subEl);
            await subEl.type(hosp.subject);
          }
        } catch (e) {
          console.warn(`⚠️ [${hosp.hospital}] 하이웍스 제목 주입 실패: ${e.message}`);
        }
        
        // [하이웍스 에디터 본문 주입 - SynapEditor iframe]
        try {
          const iframeSelector = "iframe.se-contents-edit, iframe[title='웹에디터'], iframe.editor-iframe";
          await page.waitForSelector(iframeSelector, { timeout: 8000 });
          
          const frames = page.frames();
          let synapFrame = null;
          for (const frame of frames) {
            const hasContents = await frame.$('div.se-contents');
            if (hasContents) {
              synapFrame = frame;
              break;
            }
          }
          
          if (synapFrame) {
            await synapFrame.evaluate((bodyHtml) => {
              var contentsDiv = document.querySelector('div.se-contents');
              var signBody = document.getElementById('sign_body');
              if (contentsDiv) {
                  var mailWrapper = document.createElement('div');
                  mailWrapper.innerHTML = bodyHtml + '<br>';
                  
                  if (signBody) {
                      contentsDiv.insertBefore(mailWrapper, signBody);
                      var firstP = contentsDiv.querySelector('p');
                      if (firstP && firstP !== signBody && (firstP.innerHTML === '<br>' || firstP.textContent.trim() === '')) {
                          try { contentsDiv.removeChild(firstP); } catch(e) {}
                      }
                  } else {
                      contentsDiv.appendChild(mailWrapper);
                  }
                  return true;
              }
              return false;
            }, hosp.html_body);
            console.log("👉 하이웍스 에디터 본문 주입 완료 (서명 보존)");
          }
        } catch (e) {
          console.warn(`⚠️ [${hosp.hospital}] 하이웍스 에디터 본문 주입 실패: ${e.message}`);
        }
        
      } else if (isPortal || isOther) {
        // [사내포털 받는사람 입력]
        const toSelector = '#orgAutoCon';
        try {
          await page.waitForSelector(toSelector, { timeout: 8000 });
          if (hosp.to && hosp.to.trim()) {
            const toEl = await page.$(toSelector);
            if (toEl) {
              await toEl.click();
              await page.evaluate(el => el.value = '', toEl);
              
              // 쉼표(,)나 세미콜론(;)으로 구분된 이메일 주소들을 분할하여 하나씩 입력 (토큰 등록용)
              const toEmails = hosp.to.split(/[,;]/).map(e => e.trim()).filter(Boolean);
              for (const email of toEmails) {
                await toEl.type(email);
                await page.keyboard.press('Enter');
                await new Promise(resolve => setTimeout(resolve, 300)); // 토큰 등록 대기
              }
            }
          }
        } catch (e) {
          console.warn(`⚠️ [${hosp.hospital}] 사내포털 받는사람 입력창 대기 시간 초과 또는 실패: ${e.message}`);
        }

        // [사내포털 숨은 참조(BCC) 입력]
        const bccSelector = '#orgAutoConBCC';
        try {
          if (hosp.cc && hosp.cc.trim()) {
            const bccEl = await page.$(bccSelector);
            if (bccEl) {
              await bccEl.click();
              await page.evaluate(el => el.value = '', bccEl);
              
              // 쉼표(,)나 세미콜론(;)으로 구분된 이메일 주소들을 분할하여 하나씩 입력 (토큰 등록용)
              const ccEmails = hosp.cc.split(/[,;]/).map(e => e.trim()).filter(Boolean);
              for (const email of ccEmails) {
                await bccEl.type(email);
                await page.keyboard.press('Enter');
                await new Promise(resolve => setTimeout(resolve, 300)); // 토큰 등록 대기
              }
            }
          }
        } catch (e) {
          console.warn(`⚠️ [${hosp.hospital}] 사내포털 숨은참조 입력 실패: ${e.message}`);
        }
        
        // [사내포털 제목 입력]
        try {
          const subSelector = '#subject, #txtSubject, input[name="subject"], input[name="Subject"], #subject_title';
          const subEl = await page.$(subSelector);
          if (subEl) {
            await subEl.click();
            await page.evaluate(el => el.value = '', subEl);
            await subEl.type(hosp.subject);
          }
        } catch (e) {
          console.warn(`⚠️ [${hosp.hospital}] 사내포털 제목 주입 실패: ${e.message}`);
        }
        
        // [사내포털 본문(TinyMCE Editor) 주입]
        console.log(`[사내포털] 본문 주입 시도...`);
        let bodyInjected = false;
        
        // 방법 1: 네이버 메일 스타일 (HTML 탭 클릭 -> textarea에 HTML 주입 -> Editor 탭 복귀)
        try {
          // 1) HTML 버튼 클릭 시도 (메인 프레임 및 모든 iframe 검색)
          let htmlBtnClicked = false;
          const htmlXpath = "//button[contains(., 'HTML')] | //span[contains(., 'HTML')] | //a[contains(., 'HTML')]";
          
          try {
            htmlBtnClicked = await page.evaluate((xpath) => {
              const res = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
              const el = res.singleNodeValue;
              if (el) { el.click(); return true; }
              return false;
            }, htmlXpath);
          } catch (e) {}

          if (!htmlBtnClicked) {
            const frames = page.frames();
            for (const frame of frames) {
              try {
                htmlBtnClicked = await frame.evaluate((xpath) => {
                  const res = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                  const el = res.singleNodeValue;
                  if (el) { el.click(); return true; }
                  return false;
                }, htmlXpath);
                if (htmlBtnClicked) {
                  console.log("👉 HTML 버튼 클릭 성공 (iframe 내부)");
                  break;
                }
              } catch (e) {}
            }
          }

          if (htmlBtnClicked) {
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // 2) HTML 소스 코드 입력창(textarea#covieditorContainer_html)에 본문 주입
            const taSelector = '#covieditorContainer_html';
            let sourceInputFilled = false;
            
            try {
              const ta = await page.$(taSelector);
              if (ta) {
                await page.evaluate((el, val) => {
                  el.value = val;
                  el.dispatchEvent(new Event('input', { bubbles: true }));
                  el.dispatchEvent(new Event('change', { bubbles: true }));
                }, ta, hosp.html_body);
                sourceInputFilled = true;
              }
            } catch (e) {}

            if (!sourceInputFilled) {
              const frames = page.frames();
              for (const frame of frames) {
                try {
                  const ta = await frame.$(taSelector);
                  if (ta) {
                    await frame.evaluate((el, val) => {
                      el.value = val;
                      el.dispatchEvent(new Event('input', { bubbles: true }));
                      el.dispatchEvent(new Event('change', { bubbles: true }));
                    }, ta, hosp.html_body);
                    sourceInputFilled = true;
                    console.log("👉 HTML 소스 코드 주입 완료 (iframe 내부 textarea)");
                    break;
                  }
                } catch (e) {}
              }
            }

            if (sourceInputFilled) {
              await new Promise(resolve => setTimeout(resolve, 300));
              
              // 3) Editor 탭 복귀 버튼 클릭 시도 (메인 프레임 및 모든 iframe 검색)
              let editorBtnClicked = false;
              const editorXpath = "//button[contains(., 'Editor')] | //span[contains(., 'Editor')] | //button[contains(., '에디터')] | //span[contains(., '에디터')]";
              
              try {
                editorBtnClicked = await page.evaluate((xpath) => {
                  const res = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                  const el = res.singleNodeValue;
                  if (el) { el.click(); return true; }
                  return false;
                }, editorXpath);
              } catch (e) {}

              if (!editorBtnClicked) {
                const frames = page.frames();
                for (const frame of frames) {
                  try {
                    editorBtnClicked = await frame.evaluate((xpath) => {
                      const res = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                      const el = res.singleNodeValue;
                      if (el) { el.click(); return true; }
                      return false;
                    }, editorXpath);
                    if (editorBtnClicked) {
                      console.log("👉 [Editor] 버튼 복원 완료 (iframe 내부)");
                      break;
                    }
                  } catch (e) {}
                }
              }
              
              if (editorBtnClicked) {
                bodyInjected = true;
                console.log('👉 [방법 1] 네이버 스타일 HTML/에디터 탭 전환을 통한 주입 성공!');
              }
            }
          }
        } catch (err) {
          console.warn('⚠️ 네이버 스타일 탭 전환 주입 중 예외 발생 (폴백 진행):', err.message);
        }

        // 방법 2 (폴백): 페이지 컨텍스트 내 TinyMCE API 직접 활용
        if (!bodyInjected) {
          try {
            bodyInjected = await page.evaluate((html) => {
              if (window.tinymce) {
                const editor = window.tinymce.get('covieditorContainer') || window.tinymce.activeEditor;
                if (editor) {
                  editor.setContent(html);
                  return true;
                }
              }
              return false;
            }, hosp.html_body);
            if (bodyInjected) {
              console.log('👉 [방법 2] TinyMCE API를 통한 본문 주입 성공 (폴백)');
            }
          } catch (e) {
            console.warn('⚠️ TinyMCE API 주입 실패 (DOM 직접 삽입 폴백 진행):', e.message);
          }
        }

        // 방법 3 (최종 폴백): TinyMCE iframe 내부의 body[contenteditable="true"]에 직접 주입
        if (!bodyInjected) {
          try {
            const iframeSelector = '#covieditorContainer_ifr';
            await page.waitForSelector(iframeSelector, { timeout: 8000 });
            const iframeHandle = await page.$(iframeSelector);
            if (iframeHandle) {
              const frame = await iframeHandle.contentFrame();
              if (frame) {
                bodyInjected = await frame.evaluate((html) => {
                  const body = document.querySelector('body#tinymce, body[contenteditable="true"], body');
                  if (body) {
                    body.innerHTML = html;
                    return true;
                  }
                  return false;
                }, hosp.html_body);
                
                if (bodyInjected) {
                  console.log('👉 [방법 3] TinyMCE iframe 내부 DOM 직접 삽입 성공 (최종 폴백)');
                }
              }
            }
          } catch (e) {
            console.warn(`⚠️ [${hosp.hospital}] TinyMCE iframe 본문 주입 실패: ${e.message}`);
          }
        }
      }
      
      console.log(`✅ [${hosp.hospital}] 팝업 데이터 자동 기입 완료!`);
      
    } catch (popupErr) {
      console.error(`❌ [${hosp.hospital}] 메일 창 자동 제어 실패:`, popupErr.message);
    }
    
    // 창 전환 속도 및 부하 대기
    await new Promise(resolve => setTimeout(resolve, 3000));
  }
}

async function openNaverPopupDebug(to, cc, subject, html_body, hospital, service) {
  const mailData = [{
    hospital: hospital || '알 수 없는 병원',
    to: to || '',
    cc: cc || '',
    subject: subject || '',
    html_body: html_body || '',
    service: service || 'naver'
  }];

  console.log(`[Express Service] Starting native Chrome debugger automation for single mail (${service})`);
  
  // 비동기로 자동 기입 백그라운드 구동 (API 응답 지연 방지)
  executeMailPopupAutomation(mailData).catch(err => {
    console.error('[Express Automation Error] 단일 메일 자동 주입 실패:', err.message);
  });

  return { success: true, message: '백엔드 크롬 원격 제어가 백그라운드에서 실행되었습니다.' };
}

async function openMailPopupBatch(mailList) {
  const mailData = mailList.map(item => ({
    hospital: item.hospital || '알 수 없는 병원',
    to: item.to || '',
    cc: item.cc || '',
    subject: item.subject || '',
    html_body: item.html_body || '',
    service: item.service || 'naver'
  }));

  console.log(`[Express Service] Starting native Chrome debugger automation for batch (${mailData.length}건)`);
  
  // 비동기 일괄 자동 기입 백그라운드 구동
  executeMailPopupAutomation(mailData).catch(err => {
    console.error('[Express Automation Error] 일괄 메일 자동 주입 실패:', err.message);
  });

  return { success: true, message: `총 ${mailData.length}건의 일괄 백엔드 크롬 원격 제어가 시작되었습니다.` };
}

module.exports = {
  getExcelFilesList,
  parseExcelFile,
  updateClaimState,
  updateClaimStateMultiple,
  sendMailViaSmtp,
  openNaverPopupDebug,
  openMailPopupBatch
};
