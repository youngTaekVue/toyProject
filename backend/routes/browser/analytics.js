// // Load environment variables from .env file
// require('dotenv').config();
//
// // Import the Firebase Admin SDK
// const admin = require('firebase-admin');
// const express = require('express');
// const router = express.Router();
//
// // Import Google Analytics Data API client
// const { BetaAnalyticsDataClient } = require('@google-analytics/data');
//
// // Path to your service account key file
// // IMPORTANT: This path is relative to the current file (analytics.js).
// // If analytics.js is in 'backend/routes/' and your key is in 'backend/config/',
// // the path should be '../config/serviceAccountKey.json'.
// // Make sure this file is kept secure and not exposed publicly.
// const serviceAccount = require('../../config/serviceAccountKey.json'); // <-- 경로 확인 완료!
//
// // Initialize Firebase Admin SDK
// admin.initializeApp({
//   credential: admin.credential.cert(serviceAccount),
//   // If you are using Realtime Database or Cloud Storage, you might need to specify
//   // the databaseURL or storageBucket.
//   // databaseURL: "https://<DATABASE_NAME>.firebaseio.com"
// });
//
// console.log('Firebase Admin SDK initialized successfully with service account.');
//
// // Initialize Google Analytics Data API client
// // The service account credentials from Firebase Admin SDK can be reused.
// const analyticsDataClient = new BetaAnalyticsDataClient({
//   credentials: {
//     client_email: serviceAccount.client_email,
//     private_key: serviceAccount.private_key.replace(/\\n/g, '\n'), // Handle private key newlines
//   },
// });
//
// // Get GA4 Property ID from environment variables
// const GA4_PROPERTY_ID = process.env.GA4_PROPERTY_ID;
//
// // Validate if GA4_PROPERTY_ID is set
// if (!GA4_PROPERTY_ID) {
//   console.error('ERROR: GA4_PROPERTY_ID is not set in the .env file.');
//   console.error('Please create a .env file in your project root with GA4_PROPERTY_ID=YOUR_ACTUAL_GA4_PROPERTY_ID');
//   // Depending on your application's needs, you might want to exit or throw an error here.
//   // For now, we'll let the route handler catch the error if it tries to use an undefined ID.
// } else {
//   console.log(`GA4_PROPERTY_ID loaded: ${GA4_PROPERTY_ID}`);
// }
//
//
// // --- Firebase Analytics Data Retrieval Route ---
// router.get('/analytics-summary', async (req, res) => {
//   try {
//     if (!GA4_PROPERTY_ID) {
//       return res.status(500).json({
//         error: 'Configuration Error',
//         details: 'GA4_PROPERTY_ID is not set. Please check your .env file.',
//       });
//     }
//
//     // Default date range for the last 7 days
//     const today = new Date();
//     const sevenDaysAgo = new Date(today);
//     sevenDaysAgo.setDate(today.getDate() - 7);
//
//     const startDate = req.query.startDate || sevenDaysAgo.toISOString().split('T')[0];
//     const endDate = req.query.endDate || today.toISOString().split('T')[0];
//
//     // Run a report to get basic analytics data
//     const [response] = await analyticsDataClient.runReport({
//       property: `properties/${GA4_PROPERTY_ID}`,
//       dateRanges: [
//         {
//           startDate: startDate,
//           endDate: endDate,
//         },
//       ],
//       dimensions: [
//         {
//           name: 'date',
//         },
//       ],
//       metrics: [
//         {
//           name: 'activeUsers',
//         },
//         {
//           name: 'newUsers',
//         },
//         {
//           name: 'eventCount',
//         },
//       ],
//     });
//
//     const analyticsSummary = {
//       message: `Analytics data for property ${GA4_PROPERTY_ID} from ${startDate} to ${endDate}`,
//       report: response.rows.map(row => ({
//         date: row.dimensionValues[0].value,
//         activeUsers: row.metricValues[0].value,
//         newUsers: row.metricValues[1].value,
//         eventCount: row.metricValues[2].value,
//       })),
//       totals: response.rows.reduce((acc, row) => {
//         acc.activeUsers += parseInt(row.metricValues[0].value);
//         acc.newUsers += parseInt(row.metricValues[1].value);
//         acc.eventCount += parseInt(row.metricValues[2].value);
//         return acc;
//       }, { activeUsers: 0, newUsers: 0, eventCount: 0 })
//     };
//
//     res.status(200).json(analyticsSummary);
//
//   } catch (error) {
//     console.error('Error fetching analytics summary:', error);
//     res.status(500).json({
//       error: 'Failed to fetch analytics summary',
//       details: error.message,
//       hint: "Make sure you have enabled Google Analytics Data API in your Google Cloud project and set GA4_PROPERTY_ID in your .env file."
//     });
//   }
// });
//
// // You can add more analytics-related routes here, e.g., for specific events or user segments.
// // router.get('/analytics/events/:eventName', async (req, res) => { /* ... */ });
//
// module.exports = router;