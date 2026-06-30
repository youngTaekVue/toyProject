import XLSX from 'xlsx';

const filePath = './public/files/0601_0622_병원별청구실패내역.xlsx';
const workbook = XLSX.readFile(filePath);

console.log("Workbook sheets:", workbook.SheetNames);
workbook.SheetNames.slice(0, 3).forEach((name) => {
  const sheet = workbook.Sheets[name];
  const jsonRows = XLSX.utils.sheet_to_json(sheet, { header: 1 });
  console.log(`\nSheet: ${name}, Total rows: ${jsonRows.length}`);
  console.log("First 8 rows:");
  jsonRows.slice(0, 8).forEach((row, i) => {
    console.log(`Row ${i}:`, row);
  });
});
