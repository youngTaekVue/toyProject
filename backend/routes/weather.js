const express = require("express");
const router = express.Router();
const request = require('request');
const apiKey =  process.env.NATIONAL_DATA_KEY;
require("dotenv").config();


router.post('/dataList', function (req, res) {
    const receivedData = req.body;
    if (receivedData != null) {
        let name = receivedData.name;
        let numOfRows = receivedData.numOfRows;
        let pageNo = receivedData.pageNo;
        let dataType = receivedData.dataType;
        let base_Date = receivedData.baseDate;
        let base_time = receivedData.baseTime;
        let nx = receivedData.nx;
        let ny = receivedData.ny;
        let api_base_url = `https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/${name}?serviceKey=${apiKey}&numOfRows=1052&pageNo=1&dataType=JSON&base_date=${base_Date}&base_time=${base_time}&nx=${nx}&ny=${ny}`;

        const options = {
            url: api_base_url
        };

        request.get(options, function (error, response, body) {
            //console.log('수신된 응답 본문:', body); // <--- 이 부분으로 실제 응답 확인
            if (error) {
                console.error('API 호출 중 네트워크 에러:', error);
                return res.status(500).send('네트워크 오류가 발생했습니다.');
            }

            if (response.statusCode !== 200) {
                console.error('API 응답 실패:', response.statusCode, body);
                return res.status(response.statusCode).send('외부 API 호출에 실패했습니다.');
            }

            try {
                const result = JSON.parse(body);
                res.status(200).json(result);
            } catch (e) {
                console.error('JSON 파싱 에러:', e);
                res.status(500).send('데이터 처리 중 오류가 발생했습니다.');
            }
        });
    }
});

module.exports = router;