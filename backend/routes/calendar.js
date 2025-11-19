const express = require('express');
const axios = require('axios');
const router = express.Router();

// 🚨 환경 변수 정의 (변수 이름 통일 및 실제 캘린더 ID 사용)
const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY;
const CALENDAR_ID = process.env.CALENDAR_ID;         // 기본 캘린더 ID
const KOREA_HOLIDAY_ID = process.env.KOREA_HOLIDAY_ID; // 공휴일 캘린더 ID
const ACCESS_TOKEN = process.env.GOOGLE_ACCESS_TOKEN;  // POST 요청용 OAuth 2.0 Token

// API 키 및 인증 토큰 누락 확인 미들웨어
router.use((req, res, next) => {
    // GET 요청은 API_KEY와 CALENDAR_ID만 필요
    if (req.method === 'GET' && (!GOOGLE_API_KEY || !CALENDAR_ID)) {
        console.error("ERROR: Google API Key or default Calendar ID missing.");
        return res.status(500).json({error: "Server configuration error: Google API credentials missing."});
    }
    // POST 요청은 ACCESS_TOKEN과 CALENDAR_ID가 필수
    if (req.method === 'POST' && (!ACCESS_TOKEN || !CALENDAR_ID)) {
        console.error("ERROR: Google OAuth Access Token or default Calendar ID missing for POST.");
        return res.status(500).json({error: "Server configuration error: OAuth token missing."});
    }
    next();
});

// -------------------------------------------------------------
// GET /api/events/:id : 특정 캘린더 ID(A, B 등)에 따른 일정 조회
// -------------------------------------------------------------
router.get('/api/events/:id', async (req, res) => {
    const calendarIdentifier = req.params;
    const timeMin = req.query.start;
    const timeMax = req.query.end;

    console.log(calendarIdentifier)

    // 캘린더 식별자(A/B)에 따라 Google Calendar ID 결정
    let searchParam = (calendarIdentifier.id === "A") ? CALENDAR_ID : (calendarIdentifier.id === "B") ? KOREA_HOLIDAY_ID : null; // 유효하지 않은 식별자 처리

    // 유효성 검사
    if (!searchParam) {
        return res.status(400).json({error: 'Invalid calendar identifier.'});
    }

    const encodedTimeMin = encodeURIComponent(timeMin);
    const encodedTimeMax = encodeURIComponent(timeMax);

    const googleApiUrl = `https://www.googleapis.com/calendar/v3/calendars/${searchParam}/events?key=${GOOGLE_API_KEY}&timeMin=${encodedTimeMin}&timeMax=${encodedTimeMax}&singleEvents=true&orderBy=startTime`;

    try {
        const response = await axios.get(googleApiUrl);
        const googleEvents = response.data.items;

        // FullCalendar 형식에 맞게 데이터 가공
        const fullCalendarEvents = googleEvents.map(event => ({
            id: event.id,
            title: event.summary || '(제목 없음)',
            start: event.start.dateTime || event.start.date,
            end: event.end.dateTime || event.end.date,
            allDay: !event.start.dateTime,
            url: event.htmlLink,
            // 캘린더 구분을 위한 확장 속성 추가 (선택 사항)
            extendedProps: {calendarId: calendarIdentifier}
        }));

        res.json(fullCalendarEvents);

    } catch (error) {
        console.error(`Google Calendar API GET 오류 (${calendarIdentifier}):`, error.message);
        const statusCode = error.response ? error.response.status : 500;
        const errorMessage = error.response && error.response.data && error.response.data.error
            ? error.response.data.error.message : 'Failed to fetch events from Google Calendar.';

        res.status(statusCode).json({error: errorMessage});
    }
});
// -------------------------------------------------------------

// -------------------------------------------------------------
// POST /api/insert : 일정 생성 (CREATE)
// -------------------------------------------------------------
router.post('/api/insert', async (req, res) => {
    // 기본 캘린더(CALENDAR_ID)에만 일정을 추가한다고 가정
    const targetCalendarId = CALENDAR_ID;

    const {title, start, end, allDay} = req.body;
    console.log({title, start, end, allDay})
    // Google Calendar API 요청 바디 구성
    const eventBody = {
        summary: title,
        start: allDay
            ? {date: start.substring(0, 10)}
            // 타임존을 포함해야 FullCalendar와 Google Calendar 간의 시간 일치 보장
            : {dateTime: start, timeZone: 'Asia/Seoul'},
        end: allDay
            ? {date: end.substring(0, 10)}
            : {dateTime: end, timeZone: 'Asia/Seoul'},
    };

    const googleApiUrl = `https://www.googleapis.com/calendar/v3/calendars/${targetCalendarId}/events`;

    try {
        const response = await axios.post(
            googleApiUrl,
            eventBody,
            {
                headers: {
                    'Content-Type': 'application/json',
                    // 🚨 OAuth 2.0 Access Token을 Authorization 헤더에 포함
                    'Authorization': `Bearer ${ACCESS_TOKEN}`
                }
            }
        );

        const createdEvent = response.data;
        console.log(createdEvent)
        // FullCalendar 형식에 맞게 응답 (클라이언트에서 addEvent 호출을 위함)
        res.status(201).json({
            id: createdEvent.id,
            title: createdEvent.summary,
            start: createdEvent.start.dateTime || createdEvent.start.date,
            end: createdEvent.end.dateTime || createdEvent.end.date,
            allDay: !createdEvent.start.dateTime,
            url: createdEvent.htmlLink
        });

    } catch (error) {
        console.error("Google Calendar API POST 오류:", error.message);

        // 상세 오류 처리 (401: Unauthorized, 403: Forbidden 등)
        const statusCode = error.response ? error.response.status : 500;
        const errorMessage = error.response && error.response.data && error.response.data.error
            ? error.response.data.error.message : 'Failed to create event.';

        res.status(statusCode).json({error: errorMessage});
    }
});

module.exports = router;