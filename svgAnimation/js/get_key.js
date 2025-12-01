
// --- A. 서버에서 API Google키 설정 가져오기 ---
async function fetchGoogleMapConfig() {
    const apiUrl = 'http://localhost:3000/mapkey/getGMapKey';
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            console.error(`HTTP Error: ${response.status}`);
            throw new Error(`Failed to fetch config.`);
        }
        const config = await response.json();
        return config;
    } catch (error) {
        console.error('❌ API 키 설정을 가져오는 데 실패했습니다:', error.message);
        return null;
    }
}

// --- A. 서버에서 API Kakao키 설정 가져오기 ---
async function fetchKakaMapConfig() {
    const apiUrl = 'http://localhost:3000/mapkey/getKakaoKey';

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            console.error(`HTTP Error: ${response.status}`);
            throw new Error(`Failed to fetch config.`);
        }
        const config = await response.json();
        return config;

    } catch (error) {
        console.error('❌ API 키 설정을 가져오는 데 실패했습니다:', error.message);
        return null;
    }
}
