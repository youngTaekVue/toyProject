// configRouter.js
const express = require('express');
const router = express.Router();
const request = require('request');
const axios = require('axios');
const key_num = process.env.KAKAO_MAP_KEY;
const SERVICE_KEY = process.env.REALESTATE;
const API_URL = 'https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev';

require("dotenv").config();



/**
 * GET /api/config
 * 클라이언트가 카카오맵 API 키를 요청하는 엔드포인트입니다.
 */
// mapkeyRouter.js (API 키 응답 라우터)

router.get('/getkey', (req, res) => {
    const apiKey = key_num;

    if (!apiKey) {
        // ... (오류 처리)
        return res.status(500).json({ error: "Key missing." });
    }

    // ⭐⭐ 캐시 방지 헤더 추가 ⭐⭐
    res.set({
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'Surrogate-Control': 'no-store'
    });

    // 최종 JSON 응답
    res.status(200).json({
        kakaoMapAppKey: apiKey
    });
});

router.get('/trade', async (req, res) => {

    // 💡 API URL 수정 (LAWD_CD와 DEAL_YMD 사용): 정확한 엔드포인트 확인 필요
    let api_base_url = `https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev?serviceKey=${SERVICE_KEY}&numOfRows=1000&pageNo=1&LAWD_CD=41113&DEAL_YMD=202503`;

    try {
        const response = await axios.get(api_base_url);

        console.log(response.data.response.body.items);
        //const result = JSON.parse(body); // 👈 여기서 에러 발생 가능성 높음
        res.status(200).json(response.data.response.body.items);
    } catch (e) {
        console.error('JSON 파싱 에러:', e);
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});

module.exports = router;