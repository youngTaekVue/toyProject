const express = require('express');
const router = express.Router();
const { google } = require('googleapis');
require('dotenv').config();

// [수정] 자격 증명 생성 시 환경 변수명을 GOOGLE_FIT_REDIRECT_URI로 통일
const oauth2Client = new google.auth.OAuth2(
    process.env.GOOGLE_CLIENT_ID,
    process.env.GOOGLE_CLIENT_SECRET,
    process.env.GOOGLE_REDIRECT_URI 
);

// 디버그 로그 확인용
console.log('ENV CHECK:', {
    CLIENT_ID: process.env.GOOGLE_CLIENT_ID ? 'OK' : 'MISSING',
    REDIRECT_URI: process.env.GOOGLE_FIT_REDIRECT_URI ? 'OK' : 'MISSING'
});

// Define the scopes required for Google Fit
const scopes = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.nutrition.read',
];

// 메모리 토큰 저장소 (테스트용)
let tokens = null;

// Route to initiate Google OAuth consent flow
// Vue에서 handleAuthorize 호출 시 이곳으로 진입합니다.
router.get('/google-fit/auth', (req, res) => {
    const authorizeUrl = oauth2Client.generateAuthUrl({
        access_type: 'offline', 
        scope: scopes,
        prompt: 'select_account consent' // [수정] 테스팅 계정에서 리프레시 토큰 유실 방지
    });
    res.redirect(authorizeUrl);
});

// OAuth callback route
router.get('/google-fit/callback', async (req, res) => {
    const code = req.query.code;
    try {
        const { tokens: newTokens } = await oauth2Client.getToken(code);
        oauth2Client.setCredentials(newTokens);
        tokens = newTokens; 
        console.log('Successfully authenticated with Google Fit. Tokens:', tokens);
        
        // [수정] 새창(팝업)으로 열렸을 때 부모창(Vue)을 갱신하고 본인은 닫히는 정석 스크립트
        res.send(`
            <h1>인증 성공!</h1>
            <p>잠시 후 이 창이 닫힙니다.</p>
            <script>
                if (window.opener) {
                    window.opener.location.reload(); 
                }
                window.close();
            </script>
        `);
    } catch (error) {
        console.error('Error during Google Fit authentication:', error);
        res.status(500).send('Authentication failed: ' + error.message);
    }
});

// Fetch Google Fit Daily Steps
// Vue에서 마운트 시 호출하는 엔드포인트입니다.
router.get('/google-fit/data', async (req, res) => {
    if (!tokens) {
        return res.status(401).json({ message: 'Not authenticated with Google Fit. Please authorize first.' });
    }

    try {
        oauth2Client.setCredentials(tokens);

        // Access 토큰 만료 체크 및 리프레시 자동 실행
        if (oauth2Client.isTokenExpiring()) {
            console.log('Access token expiring, refreshing...');
            const { credentials } = await oauth2Client.refreshAccessToken();
            oauth2Client.setCredentials(credentials);
            tokens = credentials; 
            console.log('Tokens refreshed:', tokens);
        }

        const fitness = google.fitness({ version: 'v1', auth: oauth2Client });

        const now = new Date();
        const endTimeMillis = now.getTime();
        // [수정] 날짜 변조 버그가 없는 깔끔한 7일 전 계산 방식
        const startTimeMillis = endTimeMillis - (7 * 24 * 60 * 60 * 1000); 

        const response = await fitness.users.dataset.aggregate({
            userId: 'me',
            requestBody: {
                aggregateBy: [{
                    dataTypeName: 'com.google.step_count.delta',
                    dataSourceId: 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps'
                }],
                bucketByTime: { durationMillis: 86400000 }, 
                startTimeMillis: startTimeMillis,
                endTimeMillis: endTimeMillis,
            },
        });

        // Vue 대시보드가 response.data.bucket을 바로 읽을 수 있도록 그대로 서빙합니다.
        res.status(200).json(response.data);
    } catch (error) {
        console.error('Error fetching Google Fit data:', error.message);
        if (error.code === 401 || error.message.includes('invalid_token')) {
            tokens = null; // 꼬인 토큰 비우기
            return res.status(401).json({ message: 'Google Fit authentication expired. Please re-authorize.' });
        }
        res.status(500).json({ message: 'Failed to fetch Google Fit data', error: error.message });
    }
});

// 연동 해제 전용 API 추가 (Vue 연동 해제 버튼과 매칭)
router.get('/google-fit/clear-tokens', (req, res) => {
    tokens = null;
    res.status(200).send('Tokens cleared');
});

module.exports = router;