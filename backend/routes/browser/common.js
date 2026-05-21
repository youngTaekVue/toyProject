const KAKAO_REST_API_KEY = process.env.KAKAO_REST_KEY;
const express = require('express');
const router = express.Router();
const axios = require('axios');
const fs = require('fs/promises'); // 비동기 파일 처리를 위해 fs/promises 사용
const { createReadStream } = require('fs'); // 스트림 처리를 위해 fs에서 createReadStream 사용
const path = require('path'); // ⭐ 경로 처리를 위해 path 모듈 추가
const csv = require('csv-parser');
const iconv = require('iconv-lite');

const keyMap = {
    '번호': 'no',
    '도로명주소': 'road_address',
    '지번주소': 'address',
    '상호': 'name',
};


// 🚨 경로 수정: 라우터 파일이 routes 폴더 안에 있다고 가정하고,
const CSV_FILE_PATH = './public/files/lotto.csv'; // ⭐ CSV 파일 경로 정의

// 판매점의 주소를 받아 kakao Geocoding API를 통해 좌표를 받아온다.
// router.get('/locations', async (req, res) => {
//
//     const KAKAO_API_URL = 'https://dapi.kakao.com/v2/local/search/address.json';
//     const ADDRESS_FIELD_NAME = '도로명주소'; // 사용할 주소 필드 이름
//
//     let vendorItems = [];
//     try {
//         // 1. CSV 파일 읽기 및 JSON으로 변환 (EUC-KR 처리 함수 호출)
//         vendorItems = await readCsvToJson(CSV_FILE_PATH);
//     } catch (e) {
//         // 에러 로깅 개선
//         console.error("❌ CSV 파일 처리 실패:", e);
//         return res.status(500).json({ error: "Failed to read or parse CSV file.", detail: e.message });
//     }
//
//     // ... (중략: 주소 추출 및 Geocoding 로직은 그대로 유지) ...
//     const addresses = vendorItems
//         .map(item => item[ADDRESS_FIELD_NAME])
//         .filter(a => a && a.trim() !== '');
//     console.log(`Geocoding을 위해 ${addresses.length}개의 주소를 추출했습니다.`);
//
//     // --- B. 일괄 Geocoding 처리 (Kakao API 호출 및 결과 취합) ---
//     if (!KAKAO_REST_API_KEY) {
//         return res.status(500).json({ error: "Server configuration error: Kakao REST API key missing." });
//     }
//
//     const finalResults = [];
//     const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
//
//     for (const [index, address] of addresses.entries()) {
//         await delay(100); // API 부하를 줄이기 위해 지연
//         try {
//             const geoResponse = await axios.get(KAKAO_API_URL, {
//                 headers: { 'Authorization': `KakaoAK ${KAKAO_REST_API_KEY}` },
//                 params: { query: address }
//             });
//
//             const documents = geoResponse.data.documents;
//             const result = documents.length > 0 ? documents[0] : null;
//
//             // 1. 원본 데이터 가져오기
//             const originalVendorData = vendorItems[index];
//
//             // 2. 💡 keyMap을 사용하여 필드명 변환
//             const translatedVendorData = translateKeys(originalVendorData, keyMap);
//
//             // console.log(translatedVendorData.no); // '번호' 대신 'no' 사용 가능
//
//             const itemResult = {
//                 ...translatedVendorData, // 💡 변환된 데이터 사용
//                 lat: result ? parseFloat(result.y) : null,
//                 lng: result ? parseFloat(result.x) : null,
//                 status: result ? 'SUCCESS' : 'NOT_FOUND',
//             };
//             console.log(itemResult);
//             finalResults.push(itemResult);
//
//         } catch (geoError) {
//             console.error(`Geocoding failed for ${address}:`, geoError.message);
//
//             // 💡 오류 발생 시에도 원본 데이터에 변환 적용하여 최종 결과에 추가
//             finalResults.push({
//                 ...translateKeys(vendorItems[index], keyMap),
//                 status: 'API_ERROR',
//                 message: geoError.response?.data?.msg || geoError.message
//             });
//         }
//     }
//
//     // --- C. 최종 결과 클라이언트에게 응답 및 파일 저장 (EUC-KR 유지) ---
//     const outputFilePath = './public/files/geocoding_lotto.json'; // ⭐ json 파일 경로 정의
//     try {
//         const jsonContent = JSON.stringify(finalResults, null, 2);
//
//         // 1. JSON 문자열을 euc-kr 버퍼로 변환합니다.
//         const eucKrBuffer = iconv.encode(jsonContent, 'utf-8');
//
//         // 2. 버퍼를 파일에 씁니다. (인코딩 인수를 생략하여 버퍼 그대로 저장)
//         await fs.writeFile(outputFilePath, eucKrBuffer);
//         console.log(`✅ Geocoding 결과가 ${outputFilePath} 파일에 EUC-KR로 저장되었습니다.`);
//
//     } catch (fileError) {
//         console.error(`❌ JSON 파일 저장 중 오류 발생:`, fileError.message);
//     }
//
//     res.status(200).json(finalResults);
// });


/**
 * CSV 파일을 읽어서 JSON 객체 배열로 변환하는 함수
 * @param {string} filePath - CSV 파일 경로
 * @returns {Promise<Array<Object>>} - JSON 객체 배열
 */
const readCsvToJson = (filePath) => {
    const results = [];

    return new Promise((resolve, reject) => {
        // 1. ⭐ EUC-KR 디코딩 스트림 추가 (가장 중요한 수정) ⭐
        const readStream = createReadStream(filePath)
            .pipe(iconv.decodeStream('euc-kr')); // euc-kr -> UTF-8로 변환

        readStream
            .pipe(csv({
                // headers: ['번호', '상호', '도로명주소', '지번주소']
            }))
            .on('data', (data) => {
                // csv-parser는 이제 UTF-8로 변환된 데이터를 받으므로 한글이 깨지지 않습니다.
                results.push(data);
            })
            .on('end', () => {
                console.log(`✅ CSV 파일에서 ${results.length}개의 항목을 성공적으로 읽었습니다.`);
                resolve(results);
            })
            .on('error', (error) => {
                // 스트림 파이프라인에서 발생하는 모든 에러를 처리합니다.
                console.error(`❌ readCsvToJson 오류:`, error.message);
                reject(error);
            });
    });
};


/**
 * 객체의 필드명(Key)을 keyMap에 따라 변환합니다.
 * @param {Object} originalObject - 변환할 원본 객체
 * @param {Object} map - { oldKey: newKey } 형태의 매핑 객체
 * @returns {Object} 필드명이 변환된 새로운 객체
 */
function translateKeys(originalObject, map) {
    return Object.keys(originalObject).reduce((acc, currentKey) => {
        // 매핑에 있으면 새 키를 사용하고, 없으면 기존 키를 그대로 사용
        const newKey = map[currentKey] || currentKey;
        acc[newKey] = originalObject[currentKey];
        return acc;
    }, {});
}


module.exports = router;