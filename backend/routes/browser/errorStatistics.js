const express = require('express');
const router = express.Router();
const ExcelJS = require('exceljs');
const path = require('path');
const fs = require('fs');

// Path to Excel files folder
const FILES_DIR = path.join(__dirname, '../../public/files');

const defaultHospital = '알 수 없는 병원';

// Helper functions (ported from frontend Dashboard.vue)
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
  const text = value.trim();
  const match = text.match(/청구실패\s*사유\s*[:：]?\s*(.*)$/i);
  if (match && match[1]) return match[1].trim();
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
    if (header) { // Only map columns that have a recognized header key
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

// 1. Get List of all Excel files (.xlsx)
router.get('/files', (req, res) => {
  try {
    if (!fs.existsSync(FILES_DIR)) {
      fs.mkdirSync(FILES_DIR, { recursive: true });
    }

    const files = fs.readdirSync(FILES_DIR)
      .filter(file => file.endsWith('.xlsx') && !file.startsWith('~$')) // Exclude temp Excel files
      .map(file => file.replace('.xlsx', ''));

    // Sort by name descending (newest first)
    files.sort((a, b) => b.localeCompare(a));

    return res.json({ success: true, files });
  } catch (error) {
    console.error('Error fetching files:', error);
    return res.status(500).json({ error: 'Failed to get excel files list' });
  }
});

// 2. Parse details from a specific Excel file
router.get('/data/:fileKey', async (req, res) => {
  const { fileKey } = req.params;
  const filePath = path.join(FILES_DIR, `${fileKey}.xlsx`);

  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: 'Excel file not found' });
  }

  try {
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.readFile(filePath);

    const loadedRows = [];

    workbook.worksheets.forEach((worksheet) => {
      const sheetName = worksheet.name;
      let headers = [];
      let currentCategory = '';

      // Read each row sequentially to prevent index shifting on empty cells
      worksheet.eachRow({ includeEmpty: false }, (row, rowIndex) => {
        const rawValues = [];
        const maxCol = Math.max(worksheet.columnCount || 0, worksheet.actualColumnCount || 0, 15);
        for (let colNum = 1; colNum <= maxCol; colNum++) {
          const val = row.getCell(colNum).value;
          rawValues.push(val === undefined ? null : val);
        }

        if (rawValues.length === 0) return;
        if (rawValues.every(cell => cell === undefined || cell === null || cell === '')) return;

        // Skip rows that act as separators (e.g. ===...=== or ---...---)
        if (rawValues.some(hasSeparatorPattern)) return;

        const firstCell = typeof rawValues[0] === 'string' ? rawValues[0].trim() : '';

        // Category marker
        if (/청구실패\s*사유/i.test(firstCell)) {
          currentCategory = normalizeSectionCategory(firstCell);
          headers = [];
          return;
        }

        // Header marker
        if (isHeaderRow(rawValues)) {
          headers = rawValues.map(normalizeHeaderValue);
          return;
        }

        if (!headers.length) return;

        // Data row
        const rowObject = buildRowObject(headers, rawValues);

        const hospital = rowObject.hospital ? String(rowObject.hospital).trim() : sheetName.trim() || defaultHospital;
        const institutionId = rowObject.institutionId ? String(rowObject.institutionId).trim() : '-';
        const emr = rowObject.emr && String(rowObject.emr).trim() !== '' ? String(rowObject.emr).trim() : '미지정';
        const category = currentCategory || (rowObject.category ? String(rowObject.category).trim() : '미분류');
        const details = rowObject.details ? String(rowObject.details).trim() : '-';

        const visitDate = parseVisitDate(details);
        const uuid = extractUuid(details);

        const rawPatient = rowObject.patient ? String(rowObject.patient).trim() : '-';
        const rawBirthDate = rowObject.birthDate ? String(rowObject.birthDate).trim() : '-';

        const patient = parsePatientName(details, rawPatient);
        const birthDate = parseBirthDate(details, rawBirthDate);

        // Retrieve state if exists in rowObject
        const state = (rowObject.state && ['미확인', '회신대기', '최종완료'].includes(rowObject.state)) 
          ? rowObject.state 
          : '미확인';

        const no = rowObject.no ? Number(rowObject.no) : rowIndex;

        loadedRows.push({
          no,
          fileKey,
          hospital,
          institutionId,
          emr,
          category,
          details,
          visitDate,
          uuid,
          patient,
          birthDate,
          state
        });
      });
    });

    return res.json({ success: true, rows: loadedRows });
  } catch (error) {
    console.error(`Error parsing file ${fileKey}:`, error);
    return res.status(500).json({ error: 'Failed to parse Excel file' });
  }
});

// 3. Update state in Excel file and save
router.put('/status', async (req, res) => {
  const { fileKey, fileKeys, hospital, patient, birthDate, category, state } = req.body;
  
  // Support both array fileKeys and single fileKey
  const targetFileKeys = fileKeys && Array.isArray(fileKeys) 
    ? fileKeys 
    : (fileKey ? [fileKey] : []);

  if (targetFileKeys.length === 0) {
    return res.status(400).json({ error: 'No fileKey or fileKeys provided' });
  }

  let isAnyUpdated = false;

  try {
    for (const fKey of targetFileKeys) {
      const filePath = path.join(FILES_DIR, `${fKey}.xlsx`);
      if (!fs.existsSync(filePath)) continue;

      const workbook = new ExcelJS.Workbook();
      await workbook.xlsx.readFile(filePath);

      // Select the worksheet representing the hospital name or fall back to the first sheet
      let worksheet = workbook.getWorksheet(hospital) || workbook.getWorksheet(hospital.trim());
      if (!worksheet) {
        // Find sheet by name (case-insensitive & trim matching)
        worksheet = workbook.worksheets.find(ws => ws.name.trim().toLowerCase() === hospital.trim().toLowerCase()) 
                    || workbook.worksheets[0];
      }

      if (!worksheet) continue;

      let isUpdated = false;
      let headers = [];
      let currentCategory = '';
      let stateColIndex = -1; // 1-indexed column number for exceljs

      // Find the matching row and update it
      worksheet.eachRow({ includeEmpty: false }, (row, rowIndex) => {
        const rawValues = [];
        const maxCol = Math.max(worksheet.columnCount || 0, worksheet.actualColumnCount || 0, 15);
        for (let colNum = 1; colNum <= maxCol; colNum++) {
          const val = row.getCell(colNum).value;
          rawValues.push(val === undefined ? null : val);
        }

        if (rawValues.length === 0) return;

        // Skip rows that act as separators (e.g. ===...=== or ---...---)
        if (rawValues.some(hasSeparatorPattern)) return;

        const firstCell = typeof rawValues[0] === 'string' ? rawValues[0].trim() : '';

        // Check category
        if (/청구실패\s*사유/i.test(firstCell)) {
          currentCategory = normalizeSectionCategory(firstCell);
          headers = [];
          return;
        }

        // Check header
        if (isHeaderRow(rawValues)) {
          // Build headers array to map column indices
          headers = rawValues.map(normalizeHeaderValue);
          
          // Find existing '진행상태' or '상태' column index
          stateColIndex = rawValues.findIndex(val => {
            const norm = String(val).trim().toLowerCase();
            return norm === '진행상태' || norm === '상태';
          });

          if (stateColIndex === -1) {
            // If not exists, we append '진행상태' at the end of the header row
            stateColIndex = rawValues.length; // 0-indexed index (which corresponds to next column index)
            // In exceljs, write to next cell
            row.getCell(stateColIndex + 1).value = '진행상태';
            row.commit();
          }
          
          return;
        }

        if (!headers.length) return;

        // Extract row data object
        const rowObject = buildRowObject(headers, rawValues);

        const rowPatient = parsePatientName(rowObject.details, rowObject.patient ? String(rowObject.patient).trim() : '-');
        const rowBirthDate = parseBirthDate(rowObject.details, rowObject.birthDate ? String(rowObject.birthDate).trim() : '-');
        const rowCategory = currentCategory || (rowObject.category ? String(rowObject.category).trim() : '미분류');

        // Check match with basic fields (hospital, patient, birthDate, category)
        const isMatch = (
          rowPatient === patient &&
          rowBirthDate === birthDate &&
          rowCategory === category
        );

        if (isMatch) {
          // Found the row! Update the state cell
          // stateColIndex is 0-indexed, exceljs cells are 1-indexed
          row.getCell(stateColIndex + 1).value = state;
          row.commit();
          isUpdated = true;
        }
      });

      if (isUpdated) {
        await workbook.xlsx.writeFile(filePath);
        isAnyUpdated = true;
      }
    }

    if (isAnyUpdated) {
      return res.json({ success: true, message: 'Excel row status updated successfully across files' });
    } else {
      return res.status(404).json({ error: 'Matching claim row not found in the target sheets' });
    }

  } catch (error) {
    console.error('Error updating status in excel:', error);
    return res.status(500).json({ error: 'Failed to update Excel row status' });
  }
});

module.exports = router;
