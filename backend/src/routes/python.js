const express = require('express');
const router = express.Router();
const { parse } = require('csv-parser');
const iconv = require('iconv-lite');
const { Readable } = require('stream');

// 공유 데이터베이스 연결 풀 가져오기 (src/config/db.js)
const { getDbPool } = require('../config/db');

// Helper function to format Date objects to 'YYYY-MM-DD HH:MM:SS'
const formatDbDate = (dateObj) => {
    const year = dateObj.getFullYear();
    const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
    const day = dateObj.getDate().toString().padStart(2, '0');
    const hours = dateObj.getHours().toString().padStart(2, '0');
    const minutes = dateObj.getMinutes().toString().padStart(2, '0');
    const seconds = dateObj.getSeconds().toString().padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

// Placeholder for auto_classify logic
const autoClassify = (description, originalType, mappingRules) => {
    const content = description.toLowerCase().trim();
    let category = '미분류';
    let subCategory = '미분분류';
    let type = originalType;

    const financialKws = ['카드대금', '결제대금', '보험', '이자', '적금', '송금', '이체', '대출', '상환', '현금서비스'];
    if (financialKws.some(kw => content.includes(kw))) {
        return { category: '금융/이체', subCategory: '자동분류', type: '이체' };
    }

    for (const rule of mappingRules) {
        const kw = rule.merchant ? String(rule.merchant).toLowerCase().trim() : '';
        if (kw && content.includes(kw)) {
            category = rule.category ? String(rule.category).trim() : '미분류';
            subCategory = rule.sub_category ? String(rule.sub_category).trim() : '미분류';
            if (['이체', '자산이동', '금융/이체'].includes(category)) {
                type = '이체';
            }
            return { category, subCategory, type };
        }
    }
    return { category, subCategory, type };
};

// --- API Endpoints ---

// GET all transactions
router.get('/transactions', async (req, res) => {
    console.log('GET /transactions: Attempting to fetch all transactions.');
    let connection;
    try {
        connection = await getDbPool().getConnection();
        const [rows] = await connection.execute("SELECT * FROM transactions");
        console.log(`GET /transactions: Successfully fetched ${rows.length} transactions.`);
        res.json(rows);
    } catch (error) {
        console.error("GET /transactions Error fetching transactions:", error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

// POST new transactions
router.post('/transactions', async (req, res) => {
    console.log('POST /transactions: Attempting to add new transactions.');
    const newTransactions = req.body; 
    if (!newTransactions || !Array.isArray(newTransactions) || newTransactions.length === 0) {
        console.warn('POST /transactions: No transaction data provided or invalid format.');
        return res.status(400).json({ error: "No transaction data provided or invalid format." });
    }

    let connection;
    try {
        connection = await getDbPool().getConnection();
        await connection.beginTransaction();

        const [existingRows] = await connection.execute("SELECT transaction_date, amount, description, transaction_type FROM transactions");
        const existingTransactions = new Set(existingRows.map(r => {
            const dbDate = formatDbDate(r.transaction_date);
            return `${dbDate}|${r.amount}|${r.description.trim()}|${r.transaction_type}`;
        }));

        let savedCount = 0;
        for (const transaction of newTransactions) {
            const transactionDate = new Date(transaction.transaction_date);
            const amount = parseInt(transaction.amount);
            const description = String(transaction.description).trim();
            const transactionType = String(transaction.transaction_type);
            const paymentMethod = String(transaction.payment_method || '');

            const newTransactionDateFormatted = formatDbDate(transactionDate);
            const transactionKey = `${newTransactionDateFormatted}|${amount}|${description}|${transactionType}`;

            if (!existingTransactions.has(transactionKey)) {
                await connection.execute(
                    "INSERT INTO transactions (transaction_date, transaction_type, description, amount, payment_method) VALUES (?, ?, ?, ?, ?)",
                    [transactionDate, transactionType, description, amount, paymentMethod]
                );
                savedCount++;
            }
        }

        await connection.commit();
        console.log(`POST /transactions: Successfully added ${savedCount} new transactions.`);
        res.status(201).json({ message: `Successfully added ${savedCount} transactions.` });
    } catch (error) {
        if (connection) {
            await connection.rollback();
            console.error("POST /transactions: Transaction rolled back due to error.");
        }
        console.error("POST /transactions Error adding transactions:", error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

// GET category mapping rules
router.get('/categories', async (req, res) => {
    console.log('GET /categories: Attempting to fetch category mapping rules.');
    let connection;
    try {
        connection = await getDbPool().getConnection();
        const [rows] = await connection.execute("SELECT id, merchant, category, sub_category FROM category ORDER BY category, merchant");
        res.json(rows);
    } catch (error) {
        console.error("GET /categories Error fetching categories:", error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

// POST new category rule
router.post('/categories', async (req, res) => {
    console.log('POST /categories: Attempting to add a new category rule.');
    const { merchant, category, sub_category } = req.body;
    if (!merchant || !category) {
        console.warn('POST /categories: Merchant and category are required for adding a rule.');
        return res.status(400).json({ error: "Merchant and category are required." });
    }

    let connection;
    try {
        connection = await getDbPool().getConnection();
        const [result] = await connection.execute(
            "INSERT INTO category (merchant, category, sub_category) VALUES (?, ?, ?)",
            [merchant, category, sub_category || null]
        );
        res.status(201).json({ id: result.insertId, message: "Category rule added successfully." });
    } catch (error) {
        console.error("Error adding category rule:", error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

// PUT update category rule
router.put('/categories/:id', async (req, res) => {
    const { id } = req.params;
    console.log(`PUT /categories/${id}: Attempting to update category rule.`);
    const { merchant, category, sub_category } = req.body;
    if (!merchant || !category) {
        console.warn(`PUT /categories/${id}: Merchant and category are required for updating a rule.`);
        return res.status(400).json({ error: "Merchant and category are required." });
    }

    let connection;
    try {
        connection = await getDbPool().getConnection();
        const [result] = await connection.execute(
            "UPDATE category SET merchant=?, category=?, sub_category=? WHERE id=?",
            [merchant, category, sub_category || null, id]
        );
        if (result.affectedRows === 0) {
            console.warn(`PUT /categories/${id}: Category rule with ID ${id} not found.`);
            return res.status(404).json({ error: "Category rule not found." });
        }
        res.json({ message: "Category rule updated successfully." });
    } catch (error) {
        console.error(`PUT /categories/${id} Error updating category rule:`, error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

// DELETE category rule
router.delete('/categories/:id', async (req, res) => {
    const { id } = req.params;
    console.log(`DELETE /categories/${id}: Attempting to delete category rule.`);
    let connection;
    try {
        connection = await getDbPool().getConnection();
        const [result] = await connection.execute(
            "DELETE FROM category WHERE id=?",
            [id]
        );
        if (result.affectedRows === 0) {
            console.warn(`DELETE /categories/${id}: Category rule with ID ${id} not found.`);
            return res.status(404).json({ error: "Category rule not found." });
        }
        res.json({ message: "Category rule deleted successfully." });
    } catch (error) {
        console.error(`DELETE /categories/${id} Error deleting category rule:`, error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

// POST financial status records
router.post('/financial_status', async (req, res) => {
    console.log('POST /financial_status: Attempting to add new financial records.');
    const financialRecords = req.body; 
    if (!financialRecords || !Array.isArray(financialRecords) || financialRecords.length === 0) {
        console.warn('POST /financial_status: No financial data provided or invalid format.');
        return res.status(400).json({ error: "No financial data provided or invalid format." });
    }

    let connection;
    try {
        connection = await getDbPool().getConnection();
        await connection.beginTransaction();

        const [maxSnapshotIdRows] = await connection.execute("SELECT COALESCE(MAX(snapshot_id), 0) AS max_id FROM financial");
        const nextSnapshotId = maxSnapshotIdRows[0].max_id + 1;

        let savedCount = 0;
        for (const record of financialRecords) {
            const { item_name, category, institution, amount, note } = record;
            if (item_name && amount !== undefined) {
                await connection.execute(
                    "INSERT INTO financial (item_name, category, institution, amount, note, snapshot_id, uploaded_at) VALUES (?, ?, ?, ?, ?, ?, NOW())",
                    [item_name, category || '', institution || '', amount, note || '', nextSnapshotId]
                );
                savedCount++;
            }
        }

        await connection.commit();
        console.log(`POST /financial_status: Successfully added ${savedCount} financial records with snapshot_id ${nextSnapshotId}.`);
        res.status(201).json({ message: `Successfully added ${savedCount} financial records with snapshot_id ${nextSnapshotId}.` });
    } catch (error) {
        if (connection) {
            await connection.rollback();
            console.error("POST /financial_status: Transaction rolled back due to error.");
        }
        console.error("POST /financial_status Error adding financial records:", error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

// GET financial data (latest snapshot)
router.get('/financial_status/latest', async (req, res) => {
    console.log('GET /financial_status/latest: Attempting to fetch latest financial status.');
    let connection;
    try {
        connection = await getDbPool().getConnection();
        const [maxSnapshotIdRows] = await connection.execute("SELECT COALESCE(MAX(snapshot_id), 0) AS max_id FROM financial");
        const latestSnapshotId = maxSnapshotIdRows[0].max_id;

        if (latestSnapshotId === 0) {
            console.log('GET /financial_status/latest: No financial data found.');
            return res.json([]); 
        }

        const [rows] = await connection.execute(
            "SELECT item_name, category, institution, amount, note FROM financial WHERE snapshot_id = ?",
            [latestSnapshotId]
        );
        console.log(`GET /financial_status/latest: Successfully fetched ${rows.length} records for snapshot ID ${latestSnapshotId}.`);
        res.json(rows);
    } catch (error) {
        console.error("GET /financial_status/latest Error fetching latest financial status:", error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

// GET distinct snapshot IDs for financial history
router.get('/financial_status/snapshots', async (req, res) => {
    console.log('GET /financial_status/snapshots: Attempting to fetch distinct financial snapshot IDs.');
    let connection;
    try {
        connection = await getDbPool().getConnection();
        const [rows] = await connection.execute(
            "SELECT DISTINCT snapshot_id FROM financial WHERE snapshot_id IS NOT NULL ORDER BY snapshot_id DESC LIMIT 20"
        );
        const snapshotIds = rows.map(row => row.snapshot_id);
        console.log(`GET /financial_status/snapshots: Successfully fetched ${snapshotIds.length} snapshot IDs.`);
        res.json(snapshotIds);
    } catch (error) {
        console.error("GET /financial_status/snapshots Error fetching financial snapshots:", error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

// GET current and previous financial rows for delta calculation
router.get('/financial_status/compare', async (req, res) => {
    console.log('GET /financial_status/compare: Attempting to fetch financial data for comparison.');
    let connection;
    try {
        connection = await getDbPool().getConnection();
        const [snapshotIdsRows] = await connection.execute(
            "SELECT DISTINCT snapshot_id FROM financial WHERE snapshot_id IS NOT NULL ORDER BY snapshot_id DESC LIMIT 2"
        );
        const snapshotIds = snapshotIdsRows.map(row => row.snapshot_id);

        let currentRows = [];
        let previousRows = [];

        if (snapshotIds.length > 0) {
            const [curr] = await connection.execute(
                "SELECT item_name, category, institution, amount, note FROM financial WHERE snapshot_id = ?",
                [snapshotIds[0]]
            );
            currentRows = curr;
            console.log(`GET /financial_status/compare: Fetched ${currentRows.length} current records for snapshot ID ${snapshotIds[0]}.`);
        }

        if (snapshotIds.length > 1) {
            const [prev] = await connection.execute(
                "SELECT item_name, category, institution, amount, note FROM financial WHERE snapshot_id = ?",
                [snapshotIds[1]]
            );
            previousRows = prev;
            console.log(`GET /financial_status/compare: Fetched ${previousRows.length} previous records for snapshot ID ${snapshotIds[1]}.`);
        }

        console.log('GET /financial_status/compare: Successfully fetched financial data for comparison.');
        res.json({ current: currentRows, previous: previousRows });
    } catch (error) {
        console.error("GET /financial_status/compare Error fetching financial data for comparison:", error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

// GET financial data for Treemap visualization
router.get('/financial_treemap_data', async (req, res) => {
    console.log('GET /financial_treemap_data: Attempting to fetch financial data for treemap.');
    let connection;
    try {
        connection = await getDbPool().getConnection();
        const [maxSnapshotIdRows] = await connection.execute("SELECT COALESCE(MAX(snapshot_id), 0) AS max_id FROM financial");
        const latestSnapshotId = maxSnapshotIdRows[0].max_id;

        if (latestSnapshotId === 0) {
            console.log('GET /financial_treemap_data: No financial data found for treemap.');
            return res.json([]);
        }

        const [rawRows] = await connection.execute(
            "SELECT item_name, category, institution, amount FROM financial WHERE snapshot_id = ?",
            [latestSnapshotId]
        );

        const treemapDataMap = new Map(); 

        rawRows.forEach(row => {
            const mainCategory = row.category; 
            const subCategory = row.institution || '기타'; 
            const itemName = row.item_name;
            let amount = row.amount;

            const isDebt = mainCategory.includes('부채') || mainCategory.includes('대출') || mainCategory.includes('카드');
            if (isDebt) {
                amount = -Math.abs(amount); 
            } else {
                amount = Math.abs(amount); 
            }

            if (!treemapDataMap.has(mainCategory)) {
                treemapDataMap.set(mainCategory, {
                    x: mainCategory,
                    y: 0, 
                    children: [] 
                });
            }
            const mainCatNode = treemapDataMap.get(mainCategory);

            mainCatNode.children.push({
                x: `${itemName} (${subCategory})`, 
                y: amount
            });
        });

        const finalTreemapData = [];
        for (const [mainCat, mainCatNode] of treemapDataMap.entries()) {
            finalTreemapData.push({
                x: mainCatNode.x,
                y: mainCatNode.y, 
                children: mainCatNode.children
            });
        }
        
        console.log(`GET /financial_treemap_data: Successfully prepared treemap data with ${finalTreemapData.length} top-level categories.`);
        res.json(finalTreemapData);

    } catch (error) {
        console.error("GET /financial_treemap_data Error fetching or processing treemap data:", error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

// GET financial history for trends chart
router.get('/financial_status/history', async (req, res) => {
    console.log('GET /financial_status/history: Attempting to fetch financial history for trends.');
    let connection;
    try {
        connection = await getDbPool().getConnection();
        const query = `
            SELECT 
                snapshot_id,
                DATE_FORMAT(MIN(uploaded_at), '%Y-%m-%d') AS date,
                SUM(CASE WHEN category LIKE '%부채%' OR category LIKE '%대출%' OR category LIKE '%카드%' THEN 0 ELSE ABS(amount) END) AS total_assets,
                SUM(CASE WHEN category LIKE '%부채%' OR category LIKE '%대출%' OR category LIKE '%카드%' THEN ABS(amount) ELSE 0 END) AS total_liabilities,
                SUM(CASE WHEN category LIKE '%부채%' OR category LIKE '%대출%' OR category LIKE '%카드%' THEN -ABS(amount) ELSE ABS(amount) END) AS net_assets
            FROM financial
            WHERE snapshot_id IS NOT NULL
            GROUP BY snapshot_id
            ORDER BY snapshot_id ASC
        `;
        const [rows] = await connection.execute(query);
        console.log(`GET /financial_status/history: Successfully fetched ${rows.length} snapshots.`);
        res.json(rows);
    } catch (error) {
        console.error("GET /financial_status/history Error fetching financial history:", error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

// GET all financial snapshot items raw history
router.get('/financial_status/history/all', async (req, res) => {
    console.log('GET /financial_status/history/all: Fetching all historical snapshot records.');
    let connection;
    try {
        connection = await getDbPool().getConnection();
        const query = `
            SELECT 
                snapshot_id,
                DATE_FORMAT(uploaded_at, '%Y-%m-%d') AS date,
                item_name,
                category,
                institution,
                amount
            FROM financial
            WHERE snapshot_id IS NOT NULL
            ORDER BY snapshot_id ASC
        `;
        const [rows] = await connection.execute(query);
        console.log(`GET /financial_status/history/all: Fetched ${rows.length} records.`);
        res.json(rows);
    } catch (error) {
        console.error("GET /financial_status/history/all Error fetching historical records:", error);
        res.status(500).json({ error: error.message });
    } finally {
        if (connection) connection.release();
    }
});

module.exports = router;
