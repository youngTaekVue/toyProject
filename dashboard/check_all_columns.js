import XLSX from 'xlsx';

const filePath = './public/files/0601_0622_병원별청구실패내역.xlsx';
const workbook = XLSX.readFile(filePath);

let printedCount = 0;

for (let name of workbook.SheetNames) {
  const sheet = workbook.Sheets[name];
  const jsonRows = XLSX.utils.sheet_to_json(sheet, { header: 1 });
  
  // Find a sheet with actual data rows (more than 5 rows)
  if (jsonRows.length > 5) {
    console.log(`\nSheet: ${name}, Total Rows: ${jsonRows.length}`);
    jsonRows.slice(3, 8).forEach((row, i) => {
      console.log(`  Row ${i}:`, row);
    });
    printedCount++;
    if (printedCount >= 3) break;
  }
}
