const express = require('express');
const router = express.Router();
const { OAuth2Client } = require('google-auth-library');
const { google } = require('googleapis');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables from .env file
dotenv.config({ path: path.resolve(__dirname, '../../.env') });
// --- 추가된 디버깅 라인 ---
console.log('Loaded GOOGLE_FIT_CLIENT_ID:', process.env.GOOGLE_CLIENT_ID ? '*****' : 'Not Loaded');
console.log('Loaded GOOGLE_FIT_CLIENT_SECRET:', process.env.GOOGLE_CLIENT_SECRET ? '*****' : 'Not Loaded');
console.log('Loaded GOOGLE_FIT_REDIRECT_URI:', process.env.GOOGLE_FIT_REDIRECT_URI ? process.env.GOOGLE_FIT_REDIRECT_URI : 'Not Loaded');
// --- 디버깅 라인 끝 ---

// Google OAuth2 Configuration
const CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;
const REDIRECT_URI = process.env.GOOGLE_FIT_REDIRECT_URI; // e.g., http://localhost:3000/health/google-fit/callback

// Ensure environment variables are loaded
if (!CLIENT_ID || !CLIENT_SECRET || !REDIRECT_URI) {
    console.error("Missing Google Fit environment variables. Please check .env file.");
    // In a production app, you might want to throw an error or disable the routes
    // process.exit(1);
}

const oAuth2Client = new OAuth2Client(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI);

// Define the scopes needed for Google Fit API
const FITNESS_ACTIVITY_READ_SCOPE = 'https://www.googleapis.com/auth/fitness.activity.read';
const FITNESS_BODY_READ_SCOPE = 'https://www.googleapis.com/auth/fitness.body.read';
const SCOPES = [FITNESS_ACTIVITY_READ_SCOPE, FITNESS_BODY_READ_SCOPE];
console.log(SCOPES);
// --- Google Fit API Endpoints ---

// 1. Start Google Fit OAuth flow
router.get('/google-fit/auth', (req, res) => {
    console.log('Starting Google Fit OAuth flow...');
    const authorizeUrl = oAuth2Client.generateAuthUrl({
        access_type: 'offline', // To get a refresh token
        scope: SCOPES,
        prompt: 'consent', // To ensure refresh token is always returned
    });
    // --- 추가된 디버깅 라인 ---
    console.log('Redirecting to Google Auth URL:', authorizeUrl);
    // --- 디버깅 라인 끝 ---
    res.redirect(authorizeUrl);
});

// 2. Google Fit OAuth callback
router.get('/google-fit/callback', async (req, res) => {
    console.log('Google Fit OAuth callback received.');
    const { code } = req.query;

    if (!code) {
        console.error('Google Fit OAuth callback: No code received.');
        return res.status(400).send('Authorization code not provided.');
    }

    try {
        const { tokens } = await oAuth2Client.getToken(code);
        oAuth2Client.setCredentials(tokens);

        console.log('Google Fit OAuth callback: Successfully obtained tokens.');
        console.log('Access Token:', tokens.access_token);
        console.log('Refresh Token:', tokens.refresh_token); // Store this securely in your DB for future use

        // In a real application, you would save these tokens (especially refresh_token)
        // to your database associated with the user.
        // For now, they are stored in the oAuth2Client instance in memory.

        res.send('Google Fit authorization successful! You can now fetch data.');
    } catch (error) {
        console.error('Google Fit OAuth callback error:', error.message);
        res.status(500).send('Error during Google Fit authorization.');
    }
});

// 3. Fetch Google Fit data (example: daily steps)
router.get('/google-fit/data', async (req, res) => {
    console.log('Fetching Google Fit data...');
    // Check if credentials (including access_token) are set
    if (!oAuth2Client.credentials || !oAuth2Client.credentials.access_token) {
        console.warn('Google Fit data fetch: No access token available. User needs to authorize first.');
        return res.status(401).send('Please authorize with Google Fit first by visiting /health/google-fit/auth');
    }

    try {
        // The 'googleapis' library, when used with an OAuth2Client that has a refresh_token,
        // will automatically handle refreshing the access token if it's expired.
        // No explicit manual refresh check is typically needed here.

        const fitness = google.fitness({ version: 'v1', auth: oAuth2Client });

        // Example: Fetch daily step count for the last 7 days
        const now = new Date();
        const endTimeMillis = now.getTime();
        // Last 7 days, starting from the beginning of 7 days ago
        const startTimeMillis = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 7).setHours(0, 0, 0, 0);

        const response = await fitness.users.dataset.aggregate({
            userId: 'me',
            requestBody: {
                aggregateBy: [{
                    dataTypeName: 'com.google.step_count.delta',
                    dataSourceId: 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps'
                }],
                bucketByTime: { durationMillis: 86400000 }, // Daily buckets (24 hours in milliseconds)
                startTimeMillis: startTimeMillis,
                endTimeMillis: endTimeMillis,
            },
        });

        console.log('Google Fit data fetch successful.');
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching Google Fit data:', error.message);
        // Handle token expiration specifically if refresh token is not used or fails
        if (error.response && error.response.status === 401) {
            // If the access token is invalid or expired and refresh failed (or no refresh token)
            return res.status(401).send('Access token expired or invalid. Please re-authorize.');
        }
        res.status(500).json({ message: 'Failed to fetch Google Fit data', error: error.message });
    }
});

module.exports = router;