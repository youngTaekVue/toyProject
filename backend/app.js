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
const mapkeyRouter = require('./routes/kakao_map');


app.use(express.json()); / JSON 형식
app.use(express.static('public'))


app.use('/api', commonRouter);
app.use('/weather', weatherRouter);
app.use('/news', newsRouter);
app.use('/calendar', calendarRouter);
app.use('/mapkey', mapkeyRouter);


app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});