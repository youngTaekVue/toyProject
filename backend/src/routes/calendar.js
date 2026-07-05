const express = require('express');
const axios = require('axios');
const router = express.Router();

const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY;
const CALENDAR_ID = process.env.CALENDAR_ID;         
const KOREA_HOLIDAY_ID = process.env.KOREA_HOLIDAY_ID; 
const ACCESS_TOKEN = process.env.GOOGLE_CLIENT_ID;  

router.use((req, res, next) => {
    if (req.method === 'GET' && (!GOOGLE_API_KEY || !CALENDAR_ID)) {
        console.error("ERROR: Google API Key or default Calendar ID missing.");
        return res.status(500).json({error: "Server configuration error: Google API credentials missing."});
    }
    if (req.method === 'POST' && (!ACCESS_TOKEN || !CALENDAR_ID)) {
        console.error("ERROR: Google OAuth Access Token or default Calendar ID missing for POST.");
        return res.status(500).json({error: "Server configuration error: OAuth token missing."});
    }
    next();
});

router.get('/api/events/:id', async (req, res) => {
    const calendarIdentifier = req.params;
    const timeMin = req.query.start;
    const timeMax = req.query.end;

    let searchParam = (calendarIdentifier.id === "A") ? CALENDAR_ID : (calendarIdentifier.id === "B") ? KOREA_HOLIDAY_ID : null; 

    if (!searchParam) {
        return res.status(400).json({error: 'Invalid calendar identifier.'});
    }

    const encodedTimeMin = encodeURIComponent(timeMin);
    const encodedTimeMax = encodeURIComponent(timeMax);

    const googleApiUrl = `https://www.googleapis.com/calendar/v3/calendars/${searchParam}/events?key=${GOOGLE_API_KEY}&timeMin=${encodedTimeMin}&timeMax=${encodedTimeMax}&singleEvents=true&orderBy=startTime`;

    try {
        const response = await axios.get(googleApiUrl);
        const googleEvents = response.data.items;

        const fullCalendarEvents = googleEvents.map(event => ({
            id: event.id,
            title: event.summary || '(제목 없음)',
            start: event.start.dateTime || event.start.date,
            end: event.end.dateTime || event.end.date,
            allDay: !event.start.dateTime,
            url: event.htmlLink,
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

router.post('/api/insert', async (req, res) => {
    const targetCalendarId = CALENDAR_ID;
    const {title, start, end, allDay} = req.body;
    
    const eventBody = {
        summary: title,
        start: allDay
            ? {date: start.substring(0, 10)}
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
                    'Authorization': `Bearer ${ACCESS_TOKEN}`
                }
            }
        );

        const createdEvent = response.data;
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
        const statusCode = error.response ? error.response.status : 500;
        const errorMessage = error.response && error.response.data && error.response.data.error
            ? error.response.data.error.message : 'Failed to create event.';

        res.status(statusCode).json({error: errorMessage});
    }
});

module.exports = router;
