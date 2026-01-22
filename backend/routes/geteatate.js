// configRouter.js
const express = require('express');
const router = express.Router();
const axios = require('axios'); // axios는 이미 정의되어 있으므로 그대로 사용

// 🚨 환경 변수 정의 (카카오 REST API 키 추가)
const SERVICE_DE_KEY = process.env.NATIONAL_Decoding_KEY;
const SERVICE_EN_KEY = process.env.NATIONAL_Encoding_KEY;


//=============================
// -------------- buslocationservice 경기도_정류소 조회 --------------
router.get('/getBusStationListv2', async (req, res) => {
    // 💡 API URL 수정 (LAWD_CD와 DEAL_YMD 사용): 정확한 엔드포인트 확인 필요
    const url = 'https://apis.data.go.kr/6410000/busstationservice/v2/getBusStationListv2';
    try {
        const response = await axios.get(url, {
            params: {
                serviceKey: SERVICE_DE_KEY, // Decoding Key 사용 권장 (axios가 자동 인코딩)
                keyword: '22026',
                format: 'json'
            }
        });
        res.status(200).json(response.data.response.msgBody.busStationList);
    } catch (e) {
        console.error('경기도_정류소 조회 호출 또는 처리 중 오류:', e.message);
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});


// -------------- buslocationservice 경기도버스_위치정보 조회 --------------
router.get('/getBusLocationListv2', async (req, res) => {

    // 💡 API URL 수정 (LAWD_CD와 DEAL_YMD 사용): 정확한 엔드포인트 확인 필요
    const url = 'https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalListv2';
    try {
        const response = await axios.get(url, {
            params: {
                serviceKey: SERVICE_DE_KEY,
                routeId: '201000093',
                format: 'json'
            }
        });
        res.status(200).json(response.data.response.msgBody.busLocationList);
    } catch (e) {
        console.error('경기도버스_위치정보 조회 호출 또는 처리 중 오류:', e.message);
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});

// -------------- getBusArrivalListv2 경기도_버스도착정보 조회 --------------
router.get('/getBusArrivalListv2', async (req, res) => {
    const param = req.query.stationId === undefined ? '' : req.query.stationId;
    // 💡 API URL 수정 (LAWD_CD와 DEAL_YMD 사용): 정확한 엔드포인트 확인 필요
    const url = 'https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalListv2';
    try {
        const response = await axios.get(url, {
            params: {
                serviceKey: SERVICE_DE_KEY,
                stationId: param,
                format: 'json'
            }
        });
        res.status(200).json(response.data.response.msgBody.busArrivalList);
    } catch (e) {
        console.error('경기도_버스도착정보 조회 호출 또는 처리 중 오류:', e.message);
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});

// -------------- getBusStationAroundListv2 경기도_버스도착정보 조회 --------------
router.get('/getBusStationAroundListv2', async (req, res) => {
    const px = req.query.x === undefined ? '' : req.query.x;
    const py = req.query.y === undefined ? '' : req.query.y;

    // 서비스 키와 URL이 올바른지 다시 한 번 확인하세요.
    // busstationservice (정류소 정보)가 맞는지 확인 필요
    const url = 'https://apis.data.go.kr/6410000/busstationservice/v2/getBusStationAroundListv2';

    try {
        const response = await axios.get(url, {
            params: {
                serviceKey: SERVICE_DE_KEY,
                x: px,
                y: py,
                format: 'json'
            }
        });

        // ⭐ 안전한 데이터 접근 및 빈 배열 처리 ⭐
        // 1. response.data가 있는지 확인
        // 2. response.msgBody가 있는지 확인
        // 3. busStationAroundList가 있는지 확인
        // 하나라도 없으면 undefined가 되고, 최종적으로 [] (빈 배열)을 반환
        const stationList = response.data?.response?.msgBody?.busStationAroundList || [];

        // 데이터가 단일 객체로 오는 경우 배열로 감싸주기 (가끔 공공데이터 API 특성상 발생)
        const resultList = Array.isArray(stationList) ? stationList : [stationList];

        // 빈 배열이어도 200 OK로 응답 (클라이언트에서 처리하기 쉬움)
        res.status(200).json(resultList);

    } catch (e) {
        console.error('경기도_버스정류소정보 조회 호출 또는 처리 중 오류:', e.message);
        // API 호출 자체가 실패했을 때만 500 에러 반환
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});
// -------------- getStationByPos 서울_버스정류소정보 조회 (ws.bus.go.kr) --------------
router.get('/getStationByPos', async (req, res) => {
    // 파라미터 처리 로직 수정 (tmX가 없으면 x를 사용하도록)
    const ptmX = req.query.tmX || req.query.x || '';
    const ptmY = req.query.tmY || req.query.y || '';

    const url = 'http://ws.bus.go.kr/api/rest/stationinfo/getStationByPos';
    try {
        const response = await axios.get(url, {
            params: {
                serviceKey: SERVICE_DE_KEY, // 서울시 API도 Decoding Key 사용
                tmX: ptmX,
                tmY: ptmY,
                radius: '100',
                resultType: 'json'
            }
        });
        console.log(response);
        //const stationList = response.data?.response?.msgBody?.busStationAroundList || [];
        // const resultList = Array.isArray(stationList) ? stationList : [stationList];
        // res.status(200).json(resultList);

    } catch (e) {
        console.error('경기도_버스정류소정보 조회 호출 또는 처리 중 오류:', e.message);
        // API 호출 자체가 실패했을 때만 500 에러 반환
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});
// =============================

// -------------- getBusStationListByKeyword 경기도_정류소 조회 (키워드 검색) --------------
// 기존 getBusStationListv2와 경로가 겹쳐서 이름 변경
router.get('/getBusStationListByKeyword', async (req, res) => {
    // 💡 API URL 수정 (LAWD_CD와 DEAL_YMD 사용): 정확한 엔드포인트 확인 필요
    const url = 'https://apis.data.go.kr/6410000/busstationservice/v2/getBusStationListv2';
    try {
        const response = await axios.get(url, {
            params: {
                serviceKey: SERVICE_DE_KEY,
                keyword: '삼익',
                format: 'json'
            }
        });
        res.status(200).json(response.data.response.msgBody.busStationList);
    } catch (e) {
        console.error('서울_정류소 조회 호출 또는 처리 중 오류:', e.message);
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});

module.exports = router;