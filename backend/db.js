const mysql = require('mysql2/promise');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables from .env file
dotenv.config({ path: path.resolve(__dirname, '../.env') });

const dbConfig = {
    host: process.env.DB_ACCOUNT_HOST || 'localhost',
    port: process.env.DB_PORT ? parseInt(process.env.DB_PORT) : 3306,
    user: process.env.DB_ACCOUNT_USER,
    password: process.env.DB_ACCOUNT_PASSWORD,
    database: process.env.DB_ACCOUNT_NAME,
    charset: 'utf8mb4',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
};

let pool;

async function initDbPool() {
    if (pool) {
        console.warn("Database pool already initialized.");
        return;
    }
    try {
        pool = mysql.createPool(dbConfig);
        await pool.getConnection(); // Test connection
        console.log("Shared database connection pool created and tested successfully.");
    } catch (error) {
        console.error("Failed to initialize shared database pool:", error);
        process.exit(1); // Exit if DB connection fails
    }
}

function getDbPool() {
    if (!pool) {
        throw new Error("Database pool not initialized. Call initDbPool() first.");
    }
    return pool;
}

module.exports = {
    initDbPool,
    getDbPool
};
