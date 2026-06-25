const express = require('express');
const router = express.Router();
const { google } = require('googleapis');
require('dotenv').config();

// Configure the OAuth2 client
const oauth2Client = new google.auth.OAuth2(
    process.env.GOOGLE_CLIENT_ID,
    process.env.GOOGLE_CLIENT_SECRET,
    process.env.GOOGLE_REDIRECT_URI
);
console.log('ENV CHECK:', {
    CLIENT_ID: process.env.GOOGLE_CLIENT_ID ? 'OK' : 'MISSING',
    REDIRECT_URI: process.env.GOOGLE_FIT_REDIRECT_URI // 👈 출력값 문자열이 제대로 나오는지 확인!
});
// Define the scopes required for Google Fit
const scopes = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.nutrition.read',
    // Add other scopes as needed
];

// Store tokens (in a real application, this would be associated with a user in a database)
let tokens = null;

// Route to initiate Google OAuth consent flow
router.get('/google-auth', (req, res) => {
    const authorizeUrl = oauth2Client.generateAuthUrl({
        access_type: 'offline', // Request a refresh token
        scope: scopes,
        prompt: 'consent' // Always ask for consent to ensure refresh token is granted
    });



    res.redirect(authorizeUrl);
});

// OAuth callback route
router.get('/google-fit/callback', async (req, res) => {
    const code = req.query.code;
    try {
        const { tokens: newTokens } = await oauth2Client.getToken(code);
        oauth2Client.setCredentials(newTokens);
        tokens = newTokens; // Store tokens
        console.log('Successfully authenticated with Google Fit. Tokens:', tokens);
        // Redirect to your dashboard or a success page
        res.send('<h1>Google Fit authentication successful! You can close this window.</h1><script>window.close();</script>');
    } catch (error) {
        console.error('Error during Google Fit authentication:', error);
        res.status(500).send('Authentication failed: ' + error.message);
    }
});

// Placeholder for Google Fit API endpoint
router.get('/google-fit-data', async (req, res) => {
    if (!tokens) {
        return res.status(401).json({ message: 'Not authenticated with Google Fit. Please authorize first.' });
    }

    try {
        // Set the credentials for the client
        oauth2Client.setCredentials(tokens);

        // Check if the access token is expired and refresh if necessary
        if (oauth2Client.isTokenExpiring()) {
            console.log('Access token expiring, refreshing...');
            const { credentials } = await oauth2Client.refreshAccessToken();
            oauth2Client.setCredentials(credentials);
            tokens = credentials; // Update stored tokens
            console.log('Tokens refreshed:', tokens);
        }

        const fitness = google.fitness({ version: 'v1', auth: oauth2Client });

        // Example: Fetch daily steps for the last 7 days
        const now = new Date();
        const endTimeMillis = now.getTime();
        const startTimeMillis = now.setDate(now.getDate() - 7); // 7 days ago

        const response = await fitness.users.dataset.aggregate({
            userId: 'me',
            requestBody: {
                aggregateBy: [{
                    dataTypeName: 'com.google.step_count.delta',
                    dataSourceId: 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps'
                }],
                bucketByTime: { durationMillis: 86400000 }, // Daily buckets
                startTimeMillis: startTimeMillis,
                endTimeMillis: endTimeMillis,
            },
        });

        res.status(200).json({ message: 'Google Fit data fetched successfully!', data: response.data });
    } catch (error) {
        console.error('Error fetching Google Fit data:', error.message);
        // If the error is due to invalid credentials, prompt re-authentication
        if (error.code === 401 || error.message.includes('invalid_token')) {
            return res.status(401).json({ message: 'Google Fit authentication expired or invalid. Please re-authorize.', error: error.message });
        }
        res.status(500).json({ message: 'Failed to fetch Google Fit data', error: error.message });
    }
});

module.exports = router;
