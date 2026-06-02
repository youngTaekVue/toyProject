const express = require('express');
const app = express();
require('dotenv').config();

const cors = require('cors');
NODE_TLS_REJECT_UNAUTHORIZED=0
const corsOptions = {
    origin: ['http://localhost:63342','http://localhost:3000'],
    optionsSuccessStatus: 200
};
app.use(cors(corsOptions));

// 라우터 불러오기
const commonRouter = require('./routes/browser/common');
const weatherRouter = require('./routes/browser/weather');
const newsRouter = require('./routes/browser/news');
const calendarRouter = require('./routes/browser/calendar');
const mapkeyRouter = require('./routes/browser/mapkey');
const busRouter = require('./routes/browser/bus');
const pythonRouter = require('./routes/python/python'); // Updated path
//const analytics = require('./routes/browser/analytics');

app.use(express.json({ limit: '50mb' })); // JSON 형식 요청 본문 처리, limit 증가
app.use(express.static('public')); // 정적 파일 서비스

// 라우터 마운트
app.use('/api', commonRouter);
app.use('/weather', weatherRouter);
app.use('/news', newsRouter);
app.use('/calendar', calendarRouter);
app.use('/mapkey', mapkeyRouter);
app.use('/bus', busRouter);
app.use('/python', pythonRouter); // Uncommented and enabled
//app.use('/analytics', analytics);

// 에러 핸들링 미들웨어 (기본 예시)
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('서버 내부에서 오류가 발생했습니다.');
});

module.exports = app;