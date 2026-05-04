const express = require("express");
const router = express.Router();
const axios = require('axios');
require("dotenv").config();

const SERVICE_KEY = process.env.NATIONAL_Encoding_KEY;
const { dfs_xy_conv } = require('../utils/geoConverter');

router.post('/dataList', async function (req, res) {
    const receivedData = req.body;

    if (receivedData != null) {
        const { name, baseDate: base_Date, baseTime: base_time, lat, lon } = receivedData;

        // "toXY" 코드를 명시적으로 전달하여 위경도를 격자 좌표로 변환
        const grid = dfs_xy_conv("toXY", lat, lon);
        const { x: nx, y: ny } = grid;

        const api_base_url = `https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/${name}`;
        const params = {
            serviceKey: SERVICE_KEY,
            numOfRows: 1052,
            pageNo: 1,
            dataType: 'JSON',
            base_date: base_Date,
            base_time: base_time,
            nx: nx,
            ny: ny
        };

        try {
            const response = await axios.get(api_base_url, { params });
            res.status(200).json(response.data);
        } catch (error) {
            if (error.response) {
                // 서버가 응답을 반환했지만 상태 코드가 2xx 범위를 벗어남
                console.error('API 응답 실패:', error.response.status, error.response.data);
                res.status(error.response.status).send('외부 API 호출에 실패했습니다.');
            } else if (error.request) {
                // 요청이 전송되었지만 응답을 받지 못함
                console.error('API 호출 중 네트워크 에러:', error.request);
                res.status(500).send('네트워크 오류가 발생했습니다.');
            } else {
                // 요청을 설정하는 중에 에러가 발생함
                console.error('API 요청 설정 에러:', error.message);
                res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
            }
        }
    }
});

module.exports = router;