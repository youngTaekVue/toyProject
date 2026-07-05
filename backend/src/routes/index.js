const express = require('express');
const router = express.Router();

// Router imports
const commonRouter = require('./common');
const errorStatisticsRouter = require('./errorStatistics');
const weatherRouter = require('./weather');
const newsRouter = require('./news');
const calendarRouter = require('./calendar');
const mapkeyRouter = require('./mapkey');
const busRouter = require('./bus');
const pythonRouter = require('./python');
const healthRouter = require('./health');

// Route mounts
router.use('/api', commonRouter);
router.use('/api/errorStatistics', errorStatisticsRouter);
router.use('/weather', weatherRouter);
router.use('/news', newsRouter);
router.use('/calendar', calendarRouter);
router.use('/mapkey', mapkeyRouter);
router.use('/bus', busRouter);
router.use('/python', pythonRouter);
router.use('/health', healthRouter);

module.exports = router;
