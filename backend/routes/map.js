const express = require('express');
const axios = require('axios');
const dotenv = require('dotenv');

// Express Router 객체 생성
const router = express.Router();

// 환경 변수 로드 (Node.js 실행 환경에 .env 파일이 있어야 합니다)
dotenv.config();

// 1. 서버에 저장된 로또 당첨 데이터 (데이터베이스를 대신하는 임시 배열)
const lotteryStores = [
    { name: "서울 로또 명당", address: "서울특별시 강남구 테헤란로 132", firstPlaceCount: 5, secondPlaceCount: 12 },
    { name: "부산 대박집", address: "부산광역시 해운대구 마린시티3로 1", firstPlaceCount: 10, secondPlaceCount: 25 },
    { name: "제주도 행운점", address: "제주특별자치도 제주시 첨단로 242", firstPlaceCount: 2, secondPlaceCount: 7 },
    { name: "대구 럭키가이", address: "대구광역시 수성구 동대구로 370", firstPlaceCount: 7, secondPlaceCount: 18 }
    // ... 실제 로또 데이터를 추가하세요.
];

// 2. 주소를 좌표로 변환하고 클라이언트에 전달하는 API 엔드포인트
// 최종 경로는 /api/lotto/locations
router.get('/locations', async (req, res) => {
    const geocodedData = [];
    // 📌 .env 파일에 저장된 카카오 REST API Key 사용
    const apiKey = process.env.KAKAO_REST_API_KEY;

    if (!apiKey) {
        console.error("KAKAO_REST_API_KEY가 .env 파일에 설정되지 않았습니다. 카카오 개발자 앱에서 REST API 키를 확인하세요.");
        return res.status(500).json({ error: "Kakao REST API Key not configured." });
    }

    // 모든 지점에 대해 순차적으로 지오코딩 수행
    for (const store of lotteryStores) {
        try {
            // 📌 카카오 로컬 REST API 호출 (서버에서 안전하게 키 사용)
            const response = await axios.get('https://dapi.kakao.com/v2/local/search/address.json', {
                params: {
                    query: store.address
                },
                headers: {
                    // 카카오 REST API는 'KakaoAK {REST_API_KEY}' 형식의 Authorization 헤더를 사용합니다.
                    Authorization: `KakaoAK ${apiKey}`
                }
            });

            // 카카오 로컬 API는 documents 배열에 결과를 반환합니다.
            if (response.data.documents && response.data.documents.length > 0) {
                const result = response.data.documents[0];

                // 카카오 로컬 API는 x(경도/lng)와 y(위도/lat)를 반환합니다.
                geocodedData.push({
                    ...store,
                    lat: parseFloat(result.y), // 위도
                    lng: parseFloat(result.x)  // 경도
                });
            } else {
                console.error(`지오코딩 실패: ${store.address}. 결과가 없습니다.`);
            }
        } catch (error) {
            // 외부 API 통신 오류 처리
            console.error('카카오 API 통신 오류:', error.message);
            // 카카오 API 응답 오류가 발생했을 경우 상세 정보 출력 (예: 인증 실패)
            if (error.response) {
                console.error("카카오 API 응답 상태:", error.response.status, "오류 메시지:", error.response.data);
            }
        }
    }

    // 최종 가공된 데이터를 클라이언트에 JSON 형태로 응답
    res.json(geocodedData);
});

module.exports = router;
