// 🚨 환경 변수 정의
const KAKAO_REST_API_KEY = process.env.KAKAO_REST_KEY;
const express = require('express');
const router = express.Router();
const axios = require('axios');
const fs = require('fs/promises'); // 비동기 파일 처리를 위해 fs/promises 사용
const {createReadStream} = require('fs'); // 스트림 처리를 위해 fs에서 createReadStream 사용
const csv = require('csv-parser'); // ⭐ 새로 추가된 CSV 파서

const CSV_FILE_PATH = './files/sample.csv'; // ⭐ CSV 파일 경로 정의

/**
 * CSV 파일을 읽어서 JSON 객체 배열로 변환하는 함수
 * @param {string} filePath - CSV 파일 경로
 * @returns {Promise<Array<Object>>} - JSON 객체 배열
 */
const readCsvToJson = (filePath) => {
    const results = [];

    // Promise를 사용하여 비동기 스트림 처리가 완료될 때까지 기다립니다.
    return new Promise((resolve, reject) => {
        createReadStream(filePath) // CSV 파일을 읽기 위한 스트림 생성
            .pipe(csv({
                // CSV 헤더를 명시적으로 지정하여 예상치 못한 헤더 변경에 대비하거나,
                // 파일의 첫 행을 헤더로 사용하려면 이 부분을 제거합니다.
                // headers: ['번호', '상호', '도로명주소', '지번주소']
            }))
            .on('data', (data) => {
                // csv-parser는 기본적으로 첫 행의 헤더를 키(Key)로 사용하여 객체를 생성합니다.
                // CSV에 '번호', '상호', '도로명주소', '지번주소' 헤더가 있다고 가정합니다.
                results.push(data);
            })
            .on('end', () => {
                console.log(`✅ CSV 파일에서 ${results.length}개의 항목을 성공적으로 읽었습니다.`);
                resolve(results);
            })
            .on('error', (error) => {
                console.error(`❌ CSV 파일 읽기 중 오류 발생:`, error.message);
                reject(error);
            });
    });
};

// 판매점의 주소를 받아 kakao Geocoding API를 통해 좌표를 받아온다.
router.get('/lottery-locations', async (req, res) => {

    const KAKAO_API_URL = 'https://dapi.kakao.com/v2/local/search/address.json';
    const ADDRESS_FIELD_NAME = '도로명주소'; // 사용할 주소 필드 이름

    let vendorItems = [];
    try {
        // 1. ⭐ CSV 파일 읽기 및 JSON으로 변환 ⭐
        vendorItems = await readCsvToJson(CSV_FILE_PATH);
    } catch (e) {
        return res.status(500).json({error: "Failed to read or parse CSV file.", detail: e.message});
    }

    const addresses = vendorItems
        .map(item => item[ADDRESS_FIELD_NAME])
        .filter(a => a && a.trim() !== '');

    console.log(`Geocoding을 위해 ${addresses.length}개의 주소를 추출했습니다.`);

    // --- B. 일괄 Geocoding 처리 (Kakao API 호출 및 결과 취합) ---
    if (!KAKAO_REST_API_KEY) {
        return res.status(500).json({error: "Server configuration error: Kakao REST API key missing."});
    }

    const finalResults = [];
    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

    for (const [index, address] of addresses.entries()) {
        await delay(100); // API 부하를 줄이기 위해 지연
        try {
            const geoResponse = await axios.get(KAKAO_API_URL, {
                headers: {'Authorization': `KakaoAK ${KAKAO_REST_API_KEY}`},
                params: {query: address}
            });

            const documents = geoResponse.data.documents;
            const result = documents.length > 0 ? documents[0] : null;
            const originalVendorData = vendorItems[index];

            finalResults.push({
                ...originalVendorData,
                input_address: address,
                lat: parseFloat(result.y),
                lng: parseFloat(result.x)
            });

            if (result) {
                finalResults.push({status: 'SUCCESS'});
            } else {
                finalResults.push({status: 'NOT_FOUND'});
            }

        } catch (geoError) {
            console.error(`Geocoding failed for ${address}:`, geoError.message);
            finalResults.push({
                ...vendorItems[index],
                input_address: address,
                status: 'API_ERROR',
                message: geoError.response?.data?.msg || geoError.message
            });
        }
    }

    // --- C. 최종 결과 클라이언트에게 응답 및 파일 저장 ---
    const outputFilePath = './files/geocoding.json';
    try {
        const jsonContent = JSON.stringify(finalResults, null, 2);
        // fs/promises의 writeFile 사용
        await fs.writeFile(outputFilePath, jsonContent, 'utf8');

        console.log(`✅ Geocoding 결과가 ${outputFilePath} 파일에 저장되었습니다.`);

    } catch (fileError) {
        console.error(`❌ JSON 파일 저장 중 오류 발생:`, fileError.message);
    }

    res.status(200).json(finalResults);
});

module.exports = router;