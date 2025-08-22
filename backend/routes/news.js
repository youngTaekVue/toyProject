const express = require("express");
const router = express.Router();
const request = require('request');
require("dotenv").config();



// 1. Naver API Client ID와 Client Secret을 여기에 입력하세요.
const client_id = process.env.clientId;
const client_secret = process.env.clientSecret;

router.get('/search', function (req, res) {
  const api_base_url = 'https://openapi.naver.com/v1/search/news';

  let params = {
    query: req.query.query || '오늘날씨', // URL 쿼리 파라미터에서 query 값을 가져옵니다.
    display: 10,
    start: 1,
    sort: 'date'
  };

  const queryString = new URLSearchParams(params).toString();
  const api_url = `${api_base_url}?${queryString}`;

  const options = {
    url: api_url,
    headers: {
      'X-Naver-Client-Id': client_id,
      'X-Naver-Client-Secret': client_secret
    }
  };

  request.get(options, function (error, response, body) {
    if (error) {
      console.error('API 호출 중 네트워크 에러:', error);
      return res.status(500).send('네트워크 오류가 발생했습니다.');
    }

    if (response.statusCode !== 200) {
      console.error('Naver API 응답 실패:', response.statusCode, body);
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
});

module.exports = router;