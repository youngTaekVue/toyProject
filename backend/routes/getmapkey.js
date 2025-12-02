// configRouter.js
const express = require('express');
const router = express.Router();
const axios = require('axios'); // axios는 이미 정의되어 있으므로 그대로 사용
// request 모듈은 axios로 대체할 수 있으므로 제거하거나 사용하지 않습니다.

// 🚨 환경 변수 정의 (카카오 REST API 키 추가)
const GOOGLE_MAP_KEY = process.env.GOOGLE_API_KEY; // GET /getkey 용
const KAKAO_KEY = process.env.KAKAO_KEY; // GET /getkey 용

// -------------------------------------------------------------
// GET /getGMapKey : 클라이언트에게 google map Key 제공
// -------------------------------------------------------------
router.get('/getGMapKey', (req, res) => {
    const apiKey = GOOGLE_MAP_KEY;

    if (!apiKey) {
        console.error("ERROR: GOOGLE_MAP_KEY missing.");
        return res.status(500).json({ error: "Key missing." });
    }

    // 캐시 방지 헤더 설정
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

// -------------------------------------------------------------
// GET /getkey : 클라이언트에게 카카오맵 JS App Key 제공
// -------------------------------------------------------------
router.get('/getKakaoKey', (req, res) => {
    const apiKey = KAKAO_KEY; // mapkeyRouter.js에서는 key_num을 사용했지만, 통일성 위해 변경

    if (!apiKey) {
        console.error("ERROR: KAKAO_MAP_APP_KEY missing.");
        return res.status(500).json({ error: "Key missing." });
    }

    // 캐시 방지 헤더 설정
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