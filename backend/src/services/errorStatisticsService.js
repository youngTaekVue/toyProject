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

module.exports = {
  getExcelFilesList,
  parseExcelFile,
  updateClaimState,
  updateClaimStateMultiple,
  sendMailViaSmtp
};
