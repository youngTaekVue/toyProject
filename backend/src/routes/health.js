const express = require('express');
const router = express.Router();
const { google } = require('googleapis');
require('dotenv').config();

const oauth2Client = new google.auth.OAuth2(
    process.env.GOOGLE_CLIENT_ID,
    process.env.GOOGLE_CLIENT_SECRET,
    process.env.GOOGLE_REDIRECT_URI 
);

console.log('ENV CHECK:', {
    CLIENT_ID: process.env.GOOGLE_CLIENT_ID ? 'OK' : 'MISSING',
    REDIRECT_URI: process.env.GOOGLE_REDIRECT_URI ? 'OK' : 'MISSING'
});

const scopes = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.nutrition.read',
];

let tokens = null;

router.get('/google-fit/auth', (req, res) => {
    const authorizeUrl = oauth2Client.generateAuthUrl({
        access_type: 'offline', 
        scope: scopes,
        prompt: 'select_account consent' 
    });
    res.redirect(authorizeUrl);
});

router.get('/google-fit/callback', async (req, res) => {
    const code = req.query.code;
    try {
        const { tokens: newTokens } = await oauth2Client.getToken(code);
        oauth2Client.setCredentials(newTokens);
        tokens = newTokens; 
        console.log('Successfully authenticated with Google Fit. Tokens:', tokens);
        
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

router.get('/google-fit/data', async (req, res) => {
    if (!tokens) {
        return res.status(401).json({ message: 'Not authenticated with Google Fit. Please authorize first.' });
    }

    try {
        oauth2Client.setCredentials(tokens);

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

        res.status(200).json(response.data);
    } catch (error) {
        console.error('Error fetching Google Fit data:', error.message);
        if (error.code === 401 || error.message.includes('invalid_token')) {
            tokens = null; 
            return res.status(401).json({ message: 'Google Fit authentication expired. Please re-authorize.' });
        }
        res.status(500).json({ message: 'Failed to fetch Google Fit data', error: error.message });
    }
});

router.get('/google-fit/clear-tokens', (req, res) => {
    tokens = null;
    res.status(200).send('Tokens cleared');
});

module.exports = router;
