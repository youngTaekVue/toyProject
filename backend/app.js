const express = require('express');
const path = require('path');
const cors = require('cors');
const app = express();
require('dotenv').config();

const corsOptions = {
    origin: ['http://localhost:63342', 'http://localhost:3000', 'http://localhost:3001'],
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true,
    optionsSuccessStatus: 200
};
app.use(cors(corsOptions));

// 공유 데이터베이스 연결 풀 초기화 (src/config/db.js)
const { initDbPool } = require('./src/config/db');
initDbPool();

app.use(express.json({ limit: '50mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// 통합 API 게이웨이 라우터 마운트
app.use('/', require('./src/routes'));

// 에러 핸들링 미들웨어
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('서버 내부에서 오류가 발생했습니다.');
});

module.exports = app;