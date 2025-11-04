// common.js
const express = require('express');
const router = express.Router();
const axios = require('axios');
// const fs = require('fs');      // CSV 파일 읽기 로직 제거를 위해 주석 처리
// const csv = require('csv-parser'); // CSV 파서 로직 제거를 위해 주석 처리

// 🚨 환경 변수 정의
const KAKAO_REST_API_KEY = process.env.KAKAO_KEY;

// -------------------------------------------------------------
// ⭐ MODIFIED: GET /lottery-locations : 샘플 주소 5개를 좌표로 변환
// -------------------------------------------------------------
router.get('/lottery-locations', async (req, res) => {

    const KAKAO_API_URL = 'https://dapi.kakao.com/v2/local/search/address.json';

    // 1. 샘플 데이터 정의 (CSV의 각 행 역할을 합니다)
    const vendorItems = [
        { 상호명: "하나복권복", 우편번호: "06130", 도로명주소: "서울 영등포구 여의나루로 42-2", 지번주소: "서울 영등포구 여의도동 3" },
        { 상호명: "무지개슈퍼", 우편번호: "34031", 도로명주소: "서울 영등포구 영등포로 379-1", 지번주소: "서울 영등포구 신길동 97-82" },
        { 상호명: "운수대통", 우편번호: "50275", 도로명주소: "경기 수원시 권선구 매실로 73", 지번주소: "경기 수원시 권선구 호매실동 87-2"}
    ];

    // 💡 주소 필드 우선순위 정의 (샘플 데이터의 필드명에 맞춤)
    const ADDRESS_FIELD_NAME = '도로명주소';

    // 주소 필드를 추출하고 유효하지 않은 값 필터링
    const addresses = vendorItems
        .map(item => item[ADDRESS_FIELD_NAME])
        .filter(a => a && a.trim() !== '');

    console.log(`테스트를 위해 ${addresses.length}개의 샘플 주소를 추출했습니다.`);


    // --- B. 일괄 Geocoding 처리 (2차 API 호출: Kakao API) ---
    if (!KAKAO_REST_API_KEY) {
        return res.status(500).json({ error: "Server configuration error: Kakao REST API key missing." });
    }

    const finalResults = [];
    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

    for (const [index, address] of addresses.entries()) {
        await delay(100); // 속도 제한 회피를 위한 지연 (유지)

        try {
            const geoResponse = await axios.get(KAKAO_API_URL, {
                headers: {
                    'Authorization': `KakaoAK ${KAKAO_REST_API_KEY}`
                },
                params: { query: address }
            });

            const documents = geoResponse.data.documents;
            const result = documents.length > 0 ? documents[0] : null;

            // 원본 데이터는 배열 인덱스로 가져올 수 있습니다 (순서가 유지되므로)
            const originalVendorData = vendorItems[index];

            if (result) {
                finalResults.push({
                    ...originalVendorData,
                    input_address: address,
                    lat: parseFloat(result.y),
                    lng: parseFloat(result.x),
                    geocoding_status: 'SUCCESS'
                });
            } else {
                finalResults.push({
                    ...originalVendorData,
                    input_address: address,
                    geocoding_status: 'NOT_FOUND',
                });
            }

        } catch (geoError) {
            console.error(`Geocoding failed for ${address}:`, geoError.message);
            finalResults.push({
                ...vendorItems[index],
                input_address: address,
                geocoding_status: 'API_ERROR',
                geocoding_message: geoError.response?.data?.msg || geoError.message
            });
        }
    }

    // --- C. 최종 결과 클라이언트에게 응답 ---
    res.status(200).json(finalResults);
});

module.exports = router;