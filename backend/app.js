const express = require('express');
const app = express();
const port = 3000;
require('dotenv').config();

const cors = require('cors');
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
const corsOptions = {
    // 여러 도메인을 허용하기 위해 origin 값을 배열로 변경합니다.
    origin: ['http://localhost:63342','http://localhost:3000'],
    optionsSuccessStatus: 200 // 일부 레거시 브라우저 지원
};
app.use(cors(corsOptions));

// news 라우트 파일 불러오기
const commonRouter = require('./routes/common');
const weatherRouter = require('./routes/weather');
const newsRouter = require('./routes/news');
const calendarRouter = require('./routes/calendar');
const mapkeyRouter = require('./routes/getmapkey');


app.use(express.json()); //JSON 형식
app.use(express.static('public'))


app.use('/api', commonRouter);
app.use('/weather', weatherRouter);
app.use('/news', newsRouter);
app.use('/calendar', calendarRouter);
app.use('/mapkey', mapkeyRouter);

// app.js (또는 서버 설정 파일)의 맨 마지막에 추가
// 이렇게 하면 www.js가 이 Express 앱 인스턴스를 가져와 사용할 수 있습니다.
module.exports = app;