const express = require('express');
const router = express.Router();

const GOOGLE_MAP_KEY = process.env.GOOGLE_API_KEY; 
const KAKAO_KEY = process.env.KAKAO_KEY; 

router.get('/getGMapKey', (req, res) => {
    const apiKey = GOOGLE_MAP_KEY;

    if (!apiKey) {
        console.error("ERROR: GOOGLE_MAP_KEY missing.");
        return res.status(500).json({ error: "Key missing." });
    }

    res.set({
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'Surrogate-Control': 'no-store'
    });

    res.status(200).json({
        googleMapAppKey: apiKey
    });
});

router.get('/getKakaoKey', (req, res) => {
    const apiKey = KAKAO_KEY; 

    if (!apiKey) {
        console.error("ERROR: KAKAO_MAP_APP_KEY missing.");
        return res.status(500).json({ error: "Key missing." });
    }

    res.set({
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'Surrogate-Control': 'no-store'
    });

    res.status(200).json({
        kakaoMapAppKey: apiKey
    });
});

module.exports = router;
