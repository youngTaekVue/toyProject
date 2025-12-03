// configRouter.js
const express = require('express');
const router = express.Router();
const axios = require('axios'); // axios는 이미 정의되어 있으므로 그대로 사용

// 🚨 환경 변수 정의 (카카오 REST API 키 추가)
const SERVICE_KEY = process.env.NATIONAL_Decoding_KEY;
const SERVICE_KEY2 = process.env.NATIONAL_Encoding_KEY;


// -------------- buslocationservice 경기도_정류소 조회 조회 --------------
router.get('/getBusStationListv2', async (req, res) => {
    // 💡 API URL 수정 (LAWD_CD와 DEAL_YMD 사용): 정확한 엔드포인트 확인 필요
    let api_base_url = `https://apis.data.go.kr/6410000/busstationservice/v2/getBusStationListv2?serviceKey=${SERVICE_KEY2}&keyword=12&format=json`;
    try {
        const response = await axios.get(api_base_url);
        console.log(response)
        res.status(200).json(response.data.response.msgBody.busStationList);
    } catch (e) {
        console.error('경기도_정류소 조회 호출 또는 처리 중 오류:', e.message);
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});


// -------------- buslocationservice 경기도버스_위치정보 조회 --------------
router.get('/getBusLocationListv2', async (req, res) => {
    // 💡 API URL 수정 (LAWD_CD와 DEAL_YMD 사용): 정확한 엔드포인트 확인 필요
    let api_base_url = `https://apis.data.go.kr/6410000/buslocationservice/v2/getBusLocationListv2?serviceKey=${SERVICE_KEY}&routeId=232000099&format=json`;
    try {
        const response = await axios.get(api_base_url);
        res.status(200).json(response.data.response.msgBody.busLocationList);
    } catch (e) {
        console.error('경기도버스_위치정보 조회 호출 또는 처리 중 오류:', e.message);
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});

module.exports = router;