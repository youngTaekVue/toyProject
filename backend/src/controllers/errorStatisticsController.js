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

async function updateMultipleStatus(req, res) {
  const { fileKey, state, updates } = req.body;
  try {
    if (!fileKey || !updates || !Array.isArray(updates)) {
      return res.status(400).json({ error: '필수 매개변수(fileKey, updates 배열)가 누락되었습니다.' });
    }
    const result = await errorStatisticsService.updateClaimStateMultiple(fileKey, state, updates);
    return res.json(result);
  } catch (error) {
    console.error('Error in updateMultipleStatus controller:', error);
    return res.status(error.status || 500).json({ error: error.message || '서버 오류가 발생했습니다.' });
  }
}

async function sendMail(req, res) {
  const { to, cc, subject, body } = req.body;
  try {
    if (!to || !subject || !body) {
      return res.status(400).json({ error: '필수 매개변수(to, subject, body)가 누락되었습니다.' });
    }
    const result = await errorStatisticsService.sendMailViaSmtp(to, cc, subject, body);
    return res.json(result);
  } catch (error) {
    console.error('Error in sendMail controller:', error);
    return res.status(error.status || 500).json({ error: error.message || '이메일 발송 중 오류가 발생했습니다.' });
  }
}

async function openNaverPopup(req, res) {
  const { to, cc, subject, html_body, hospital, service } = req.body;
  try {
    const result = await errorStatisticsService.openNaverPopupDebug(to, cc, subject, html_body, hospital, service);
    return res.json(result);
  } catch (error) {
    console.error('Error in openNaverPopup controller:', error);
    return res.status(error.status || 500).json({ error: error.message || '팝업 실행 중 오류가 발생했습니다.' });
  }
}

async function openNaverPopupBatch(req, res) {
  const { mailList } = req.body;
  try {
    if (!mailList || !Array.isArray(mailList)) {
      return res.status(400).json({ error: '필수 매개변수(mailList 배열)가 누락되었습니다.' });
    }
    const result = await errorStatisticsService.openMailPopupBatch(mailList);
    return res.json(result);
  } catch (error) {
    console.error('Error in openNaverPopupBatch controller:', error);
    return res.status(error.status || 500).json({ error: error.message || '일괄 팝업 실행 중 오류가 발생했습니다.' });
  }
}

module.exports = {
  getFiles,
  getFileData,
  updateStatus,
  updateMultipleStatus,
  sendMail,
  openNaverPopup,
  openNaverPopupBatch
};
