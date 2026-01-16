
// --- A. 경기도_정류소 조회 데이터를 가져오기 ---
async function getBusStationListv2() {
    const tradeUrl = 'http://localhost:3000/eatate/getBusStationListv2';
    try {
        const response = await fetch(tradeUrl);
        if (!response.ok) {
            throw new Error(`서버 요청 실패: ${response.status} ${response.statusText}`);
        }
        const locationData = await response.json();

        return locationData;

    } catch (error) {
        console.error('❌ Geocoding 데이터를 가져오는 데 실패했습니다:', error.message);
        return null;
    }
}

// --- b. 경기도버스_위치정보 조회 데이터를 가져오기 ---
async function getBusLocationListv2(stationId) {
    console.log(stationId)
    const tradeUrl = `http://localhost:3000/eatate/getBusLocationListv2?stationId=${stationId}`;
    try {
        const response = await fetch(tradeUrl);
        if (!response.ok) {
            throw new Error(`서버 요청 실패: ${response.status} ${response.statusText}`);
        }
        const locationData = await response.json();
        return locationData;

    } catch (error) {
        console.error('❌ Geocoding 데이터를 가져오는 데 실패했습니다:', error.message);
        return null;
    }
}
// --- c. 경기도버스_도착정보 조회 데이터를 가져오기 ---
async function getBusArrivalListv2(item) {
    console.log(item)
    let stationId = item.stationId;
    const tradeUrl = `http://localhost:3000/eatate/getBusArrivalListv2?stationId=${stationId}`;
    try {
        const response = await fetch(tradeUrl);
        if (!response.ok) {
            throw new Error(`서버 요청 실패: ${response.status} ${response.statusText}`);
        }
        const locationData = await response.json();
        console.log(locationData);
        return locationData;

    } catch (error) {
        console.error('❌ Geocoding 데이터를 가져오는 데 실패했습니다:', error.message);
        return null;
    }
}

// --- A. 경기도_정류소 조회 데이터를 가져오기 ---
async function getSeoulBusStationListv2() {
    const tradeUrl = 'http://localhost:3000/eatate/getSeoulBusStationListv2';
    try {
        const response = await fetch(tradeUrl);
        if (!response.ok) {
            throw new Error(`서버 요청 실패: ${response.status} ${response.statusText}`);
        }
        const getSeoulBusData = await response.json();

        return getSeoulBusData;

    } catch (error) {
        console.error('❌ Geocoding 데이터를 가져오는 데 실패했습니다:', error.message);
        return null;
    }
}

// --- B. 서버의 JSON 파일 데이터를 가져오기 ---
async function fetchBusSationData() {
     const tradeUrl = 'http://localhost:3000/files/gyeonggi_bus.json';
    //const tradeUrl = 'http://localhost:3000/files/sample1.json';
    console.log(tradeUrl)
    try {
        const response = await fetch(tradeUrl);

        if (!response.ok) {
            throw new Error(`서버 요청 실패: ${response.status} ${response.statusText}`);
        }
        const locationData = await response.json();
        console.log('✅ Geocoding 데이터 수신 완료:', locationData.length, '개');
        return locationData;

    } catch (error) {
        console.error('❌ Geocoding 데이터를 가져오는 데 실패했습니다:', error.message);
        return null;
    }
}
