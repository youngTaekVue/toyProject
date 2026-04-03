const express = require('express');
const router = express.Router();
const mysql = require('mysql2/promise');
require('dotenv').config(); // .env 파일의 환경 변수를 로드

// 데이터베이스 연결 풀 생성
const pool = mysql.createPool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,


    database: process.env.DB_DATABASE,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});


router.get('/userInfo', async (req, res) => {
    let connection;
    try {
        // 쿼리 파라미터에서 userId 가져오기 (예: /userInfo?userId=some_user)
        const { userId } = req.query;
        
        // 1. DB 커넥션 풀에서 커넥션 가져오기
        connection = await pool.getConnection();
        console.log('✅ 데이터베이스에 성공적으로 연결되었습니다.');

        // 2. 쿼리 실행 (userId가 있을 경우 필터링 추가)
        let query = 'SELECT id, userId, userNm, content, insertDate FROM userInfo';
        let params = [];

        if (userId) {
            query += ' WHERE userId = ?';
            params.push(userId);
        }

        const [rows] = await connection.execute(query, params);
        console.log('✅ 쿼리를 성공적으로 실행했습니다.');

        // 3. 응답 결과 전송
        res.status(200).json(rows);

    } catch (error) {
        console.error('❌ 데이터베이스 작업 중 오류가 발생했습니다:', error);
        res.status(500).json({
            message: '데이터베이스 작업 중 오류가 발생했습니다.',
            error: error.message
        });
    } finally {
        // 4. 커넥션 반환
        if (connection) {
            connection.release();
            console.log('✅ 데이터베이스 커넥션을 반환했습니다.');
        }
    }
});

module.exports = router;
