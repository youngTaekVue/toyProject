const ExcelJS = require('exceljs');
const path = require('path');
const fs = require('fs');

const FILES_DIR = path.join(__dirname, 'public/files');

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
  let str = String(cell);
  return str.includes('===') || str.includes('---');
}

async function run() {
  console.log('FILES_DIR:', FILES_DIR);
  if (!fs.existsSync(FILES_DIR)) {
    console.log('Dir not found');
    return;
  }
  const files = fs.readdirSync(FILES_DIR).filter(f => f.endsWith('.xlsx'));
  console.log('Excel Files:', files);

  for (const file of files) {
    console.log('\n----------------------------------------');
    console.log('Reading file:', file);
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.readFile(path.join(FILES_DIR, file));

    workbook.worksheets.forEach(worksheet => {
      console.log(`  Worksheet: ${worksheet.name} (Rows: ${worksheet.rowCount})`);
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
          const text = firstCell.trim();
          const match = text.match(/청구실패\s*사유\s*[:：]?\s*(.*)$/i);
          currentCategory = match && match[1] ? match[1].trim() : '미분류';
          headers = [];
          return;
        }

        if (isHeaderRow(rawValues)) {
          headers = rawValues.map(normalizeHeaderValue);
          console.log('    Headers parsed:', headers);
          return;
        }

        if (!headers.length) return;

        const rowObject = buildRowObject(headers, rawValues);
        
        // Print row if state is set or if matching 나사렛국제병원
        const isTarget = rowObject.hospital && String(rowObject.hospital).includes('나사렛국제병원');
        if (isTarget || (rowObject.state && rowObject.state !== '미확인')) {
          console.log(`    MATCHED Row [Line ${rowIndex}]:`, {
            hospital: rowObject.hospital || worksheet.name,
            patient: rowObject.patient || '-',
            category: currentCategory || rowObject.category || '미분류',
            state: rowObject.state || '미확인',
            rawValues: rawValues
          });
        }
      });
    });
  }
}

run().catch(console.error);
