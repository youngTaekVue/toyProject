const express = require('express');
const router = express.Router();
const errorStatisticsController = require('../controllers/errorStatisticsController');

// 1. Get List of all Excel files (.xlsx)
router.get('/files', errorStatisticsController.getFiles);

// 2. Parse details from a specific Excel file
router.get('/data/:fileKey', errorStatisticsController.getFileData);

// 3. Update status of Excel row items
router.put('/status', errorStatisticsController.updateStatus);

// 4. Send email via SMTP
router.post('/sendMail', errorStatisticsController.sendMail);

module.exports = router;
