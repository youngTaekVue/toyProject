// routes/calendar.js

const express = require('express');
const axios = require('axios');
const router = express.Router();

// 🚨 환경 변수 사용을 위한 변수 재정의
const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY;
const CALENDAR_ID = process.env.GOOGLE_CLIENT_ID;
// Node.js 환경에서 사용 예시
const timeMin = '2024-10-01T00:00:00+09:00'; // FullCalendar 요청 쿼리 (req.query.start)
const timeMax = '2025-10-31T23:59:59+09:00'; // FullCalendar 요청 쿼리 (req.query.end)

const encodedTimeMin = encodeURIComponent(timeMin);
// 결과: "2025-10-01T00%3A00%3A00%2B09%3A00"

const encodedTimeMax = encodeURIComponent(timeMax);
// API 키나 캘린더 ID가 설정되었는지 확인하는 간단한 미들웨어 (선택 사항)

// 🚨🚨🚨 중요: POST 요청을 위한 OAuth 2.0 Access Token
// 이 값은 실제 OAuth 2.0 인증 흐름을 통해 백엔드에서 획득해야 합니다.
const ACCESS_TOKEN = process.env.GOOGLE_ACCESS_TOKEN;



// API 키나 캘린더 ID가 설정되었는지 확인하는 미들웨어
router.use((req, res, next) => {
    // POST 요청을 위해 ACCESS_TOKEN도 확인합니다.
    if (!GOOGLE_API_KEY || !CALENDAR_ID || (!ACCESS_TOKEN && req.method === 'POST')) {
        console.error(`ERROR: Google API credentials missing. Method: ${req.method}`);
        return res.status(500).json({
            error: "Server configuration error: Calendar credentials missing."
        });
    }
    next();
});

// -------------------------------------------------------------
// GET /api/events : 일정 조회 (READ)
// FullCalendar 클라이언트가 호출하는 엔드포인트 (API Key 사용)
// -------------------------------------------------------------
router.get('/api/events', async (req, res) => {
    // FullCalendar 요청에서 시작일과 종료일 가져오기
    const timeMin = req.query.start;
    const timeMax = req.query.end;

    // 💡 참고: 이전 코드에서 상수(encodedTimeMin/Max)를 사용했지만,
    // 여기서는 FullCalendar가 전송하는 쿼리 매개변수(timeMin/timeMax)를 인코딩하여 사용해야 합니다.
    const encodedTimeMin = encodeURIComponent(timeMin);
    const encodedTimeMax = encodeURIComponent(timeMax);

    const googleApiUrl = `https://www.googleapis.com/calendar/v3/calendars/${CALENDAR_ID}/events?key=${GOOGLE_API_KEY}&timeMin=${encodedTimeMin}&timeMax=${encodedTimeMax}&singleEvents=true&orderBy=startTime`;

    try {
        const response = await axios.get(googleApiUrl);
        const googleEvents = response.data.items;

        // FullCalendar Event Object 형식에 맞게 데이터 가공
        const fullCalendarEvents = googleEvents.map(event => ({
            id: event.id,
            title: event.summary || '(제목 없음)',
            start: event.start.dateTime || event.start.date,
            end: event.end.dateTime || event.end.date,
            allDay: !event.start.dateTime,
            url: event.htmlLink
        }));

        res.json(fullCalendarEvents);

    } catch (error) {
        console.error("Google Calendar API 조회 오류:", error.message);
        // 오류 응답 상세 출력 (디버깅 목적)
        if (error.response) {
            console.error("오류 상세:", error.response.data);
        }
        res.status(500).json({ error: 'Failed to fetch events from Google Calendar.' });
    }
});

// -------------------------------------------------------------
// POST /api/insert : 일정 생성 (CREATE)
// FullCalendar에서 select 콜백을 통해 호출되는 엔드포인트 (OAuth Token 사용)
// -------------------------------------------------------------
router.post('/api/insert', async (req, res) => {
    const { title, start, end, allDay } = req.body;

    // Google Calendar API 요청 바디 구성
    const eventBody = {
        summary: title,
        start: allDay
            ? { date: start.substring(0, 10) }
            : { dateTime: start, timeZone: 'Asia/Seoul' },
        end: allDay
            ? { date: end.substring(0, 10) }
            : { dateTime: end, timeZone: 'Asia/Seoul' },
    };

    const googleApiUrl = `https://www.googleapis.com/calendar/v3/calendars/${CALENDAR_ID}/events`;

    try {
        const response = await axios.post(
            googleApiUrl,
            eventBody,
            {
                headers: {
                    // 🚨 일정 생성/수정/삭제는 OAuth Access Token이 필수입니다.
                    'Authorization': `Bearer ${ACCESS_TOKEN}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        const createdEvent = response.data;

        // FullCalendar 형식에 맞게 응답
        res.status(201).json({
            id: createdEvent.id,
            title: createdEvent.summary,
            start: createdEvent.start.dateTime || createdEvent.start.date,
            end: createdEvent.end.dateTime || createdEvent.end.date,
            allDay: !createdEvent.start.dateTime,
            url: createdEvent.htmlLink
        });

    } catch (error) {
        console.error("Google Calendar API 일정 생성 오류:", error.message);

        let errorMessage = '일정 생성 실패';
        let statusCode = 500;
        if (error.response) {
            statusCode = error.response.status;
            // 401, 403 등 인증 오류 시 상세 메시지 전달
            if (error.response.data && error.response.data.error) {
                errorMessage = error.response.data.error.message || errorMessage;
            }
            console.error("오류 상세:", error.response.data);
        }

        res.status(statusCode).json({ error: errorMessage });
    }
});

// 라우터 객체를 모듈로 내보내기
module.exports = router;