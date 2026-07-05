const errorStatisticsService = require('../services/errorStatisticsService');

async function getFiles(req, res) {
  try {
    const files = await errorStatisticsService.getExcelFilesList();
    return res.json({ success: true, files });
  } catch (error) {
    console.error('Error in getFiles controller:', error);
    return res.status(error.status || 500).json({ error: error.message || 'Failed to get excel files list' });
  }
}

async function getFileData(req, res) {
  const { fileKey } = req.params;
  try {
    if (!fileKey) {
      return res.status(400).json({ error: 'fileKey 파라미터가 누락되었습니다.' });
    }
    const rows = await errorStatisticsService.parseExcelFile(fileKey);
    return res.json({ success: true, rows });
  } catch (error) {
    console.error(`Error in getFileData controller for ${fileKey}:`, error);
    return res.status(error.status || 500).json({ error: error.message || 'Failed to parse Excel file' });
  }
}

async function updateStatus(req, res) {
  const { fileKey, hospital, category, state, rows } = req.body;
  try {
    if (!fileKey) {
      return res.status(400).json({ error: '정확한 fileKey가 제공되지 않았습니다.' });
    }
    if (!hospital || !state || !rows) {
      return res.status(400).json({ error: '필수 매개변수(hospital, state, rows)가 누락되었습니다.' });
    }
    
    const result = await errorStatisticsService.updateClaimState(fileKey, hospital, category, state, rows);
    return res.json(result);
  } catch (error) {
    console.error('Error in updateStatus controller:', error);
    return res.status(error.status || 500).json({ error: error.message || '서버 오류가 발생했습니다.' });
  }
}
module.exports = {
  getFiles,
  getFileData,
  updateStatus
};
