const KAKAO_REST_API_KEY = process.env.KAKAO_REST_KEY;
const express = require('express');
const router = express.Router();
const fs = require('fs/promises'); 
const { createReadStream } = require('fs'); 
const csv = require('csv-parser');
const iconv = require('iconv-lite');

const keyMap = {
    '번호': 'no',
    '도로명주소': 'road_address',
    '지번주소': 'address',
    '상호': 'name',
};

const CSV_FILE_PATH = './public/files/lotto.csv'; 

const readCsvToJson = (filePath) => {
    const results = [];

    return new Promise((resolve, reject) => {
        const readStream = createReadStream(filePath)
            .pipe(iconv.decodeStream('euc-kr')); 

        readStream
            .pipe(csv({}))
            .on('data', (data) => {
                results.push(data);
            })
            .on('end', () => {
                console.log(`✅ CSV 파일에서 ${results.length}개의 항목을 성공적으로 읽었습니다.`);
                resolve(results);
            })
            .on('error', (error) => {
                console.error(`❌ readCsvToJson 오류:`, error.message);
                reject(error);
            });
    });
};

function translateKeys(originalObject, map) {
    return Object.keys(originalObject).reduce((acc, currentKey) => {
        const newKey = map[currentKey] || currentKey;
        acc[newKey] = originalObject[currentKey];
        return acc;
    }, {});
}

module.exports = router;
