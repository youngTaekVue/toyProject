const express = require('express');
const router = express.Router();
const axios = require('axios'); // axios를 사용하여 HTTP 요청을 보냅니다.

// Python Flask API의 기본 URL
const PYTHON_API_BASE_URL = 'http://localhost:5000';

// GET /python/transactions
router.get('/transactions', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_API_BASE_URL}/transactions`);
        res.json(response.data);
    } catch (error) {
        console.error('Error calling Python API /transactions (GET):', error.message);
        res.status(error.response?.status || 500).json({ error: error.message });
    }
});

// POST /python/transactions
router.post('/transactions', async (req, res) => {
    try {
        const response = await axios.post(`${PYTHON_API_BASE_URL}/transactions`, req.body);
        res.status(response.status).json(response.data);
    } catch (error) {
        console.error('Error calling Python API /transactions (POST):', error.message);
        res.status(error.response?.status || 500).json({ error: error.message });
    }
});

// GET /python/categories
router.get('/categories', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_API_BASE_URL}/categories`);
        res.json(response.data);
    } catch (error) {
        console.error('Error calling Python API /categories (GET):', error.message);
        res.status(error.response?.status || 500).json({ error: error.message });
    }
});

// POST /python/financial_status
router.post('/financial_status', async (req, res) => {
    try {
        const response = await axios.post(`${PYTHON_API_BASE_URL}/financial_status`, req.body);
        res.status(response.status).json(response.data);
    } catch (error) {
        console.error('Error calling Python API /financial_status (POST):', error.message);
        res.status(error.response?.status || 500).json({ error: error.message });
    }
});

module.exports = router;
