// configRouter.js
const express = require('express');
const router = express.Router();
const axios = require('axios'); // axios는 이미 정의되어 있으므로 그대로 사용
// request 모듈은 axios로 대체할 수 있으므로 제거하거나 사용하지 않습니다.

// 🚨 환경 변수 정의 (카카오 REST API 키 추가)
const KAKAO_KEY = process.env.KAKAO_KEY; // GET /getkey 용
const KAKAO_REST_API_KEY = process.env.KAKAO_REST_API_KEY; // ⭐⭐ Geocoding 용 (새로 정의) ⭐⭐
const SERVICE_KEY = process.env.REALESTATE;
const API_URL = 'https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev'; // 부동산 API Base URL

// .env 파일 로드는 이미 require("dotenv").config(); 에 의해 처리됨

// -------------------------------------------------------------
// GET /getkey : 클라이언트에게 카카오맵 JS App Key 제공
// -------------------------------------------------------------
router.get('/getkey', (req, res) => {
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

// -------------------------------------------------------------
// GET /trade : 국토교통부 실거래가 정보 조회
// -------------------------------------------------------------
// router.get('/trade', async (req, res) => {
//
//     // 💡 API URL 수정 (LAWD_CD와 DEAL_YMD 사용): 정확한 엔드포인트 확인 필요
//     let api_base_url = `https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev?serviceKey=${SERVICE_KEY}&numOfRows=1000&pageNo=1&LAWD_CD=41113&DEAL_YMD=202503`;
//
//     try {
//         const response = await axios.get(api_base_url);
//         // XML 형식이면 JSON 파싱이 필요 없거나 다른 처리가 필요할 수 있지만,
//         // 현재 코드가 response.data.response.body.items를 가정하므로 그대로 둡니다.
//         res.status(200).json(response.data.response.body.items);
//     } catch (e) {
//         console.error('부동산 데이터 API 호출 또는 처리 중 오류:', e.message);
//         res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
//     }
// });

module.exports = router;