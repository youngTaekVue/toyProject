const express = require('express');
const router = express.Router();
const axios = require('axios');

const SERVICE_DE_KEY = process.env.NATIONAL_Decoding_KEY;

// 경기도 정류소 조회
router.get('/stationList', async (req, res) => {
    const url = 'https://apis.data.go.kr/6410000/busstationservice/v2/getBusStationListv2';
    const { keyword = '22026' } = req.query;
    try {
        const response = await axios.get(url, {
            params: {
                serviceKey: SERVICE_DE_KEY,
                keyword,
                format: 'json'
            }
        });
        res.status(200).json(response.data?.response?.msgBody?.busStationList || []);
    } catch (e) {
        console.error('경기도 정류소 조회 오류:', e.message);
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});

// 경기도 버스 위치 정보 조회
router.get('/locationList', async (req, res) => {
    const url = 'https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalListv2';
    const { routeId = '201000093' } = req.query;
    try {
        const response = await axios.get(url, {
            params: {
                serviceKey: SERVICE_DE_KEY,
                routeId,
                format: 'json'
            }
        });
        res.status(200).json(response.data?.response?.msgBody?.busLocationList || []);
    } catch (e) {
        console.error('경기도 버스 위치 정보 조회 오류:', e.message);
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});

// 경기도 버스 도착 정보 조회
router.get('/arrivalList', async (req, res) => {
    const url = 'https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalListv2';
    const { stationId = '' } = req.query;
    try {
        const response = await axios.get(url, {
            params: {
                serviceKey: SERVICE_DE_KEY,
                stationId,
                format: 'json'
            }
        });
        res.status(200).json(response.data?.response?.msgBody?.busArrivalList || []);
    } catch (e) {
        console.error('경기도 버스 도착 정보 조회 오류:', e.message);
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});

// 주변 버스 정류소 조회
router.get('/aroundStationList', async (req, res) => {
    const url = 'https://apis.data.go.kr/6410000/busstationservice/v2/getBusStationAroundListv2';
    const { x = '', y = '' } = req.query;
    try {
        const response = await axios.get(url, {
            params: {
                serviceKey: SERVICE_DE_KEY,
                x,
                y,
                format: 'json'
            }
        });
        const stationList = response.data?.response?.msgBody?.busStationAroundList || [];
        res.status(200).json(Array.isArray(stationList) ? stationList : [stationList]);
    } catch (e) {
        console.error('주변 버스 정류소 조회 오류:', e.message);
        res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
    }
});

module.exports = router;