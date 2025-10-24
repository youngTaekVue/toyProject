const express = require('express');
const app = express();
const port = 3000;
require('dotenv').config();

const cors = require('cors');
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
const corsOptions = {
    origin: 'http://localhost:63342', // 이 도메인만 허용
    optionsSuccessStatus: 200 // 일부 레거시 브라우저 지원
};
app.use(cors(corsOptions));

// news 라우트 파일 불러오기
// const weatherRouter = require('./routes/weather');
const newsRouter = require('./routes/news');
const calendarRouter = require('./routes/calendar');

app.use(express.json()); // JSON 형식

// /news 경로로 들어오는 모든 요청을 newsRouter로 전달
// app.use('/weather', weatherRouter);
app.use('/news', newsRouter);
app.use('/calendar', calendarRouter);



app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});