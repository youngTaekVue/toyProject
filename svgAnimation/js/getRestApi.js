
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

// --- d. 내 주변 정류장 정보 조회 (경기도) ---
async function getBusStationAroundListv2(lat, lng) {
    const tradeUrl = `http://localhost:3000/eatate/getBusStationAroundListv2?x=${lng}&y=${lat}`;
    try {
        const response = await fetch(tradeUrl);
        if (!response.ok) {
            throw new Error(`서버 요청 실패: ${response.status} ${response.statusText}`);
        }
        const locationData = await response.json();
        return locationData;

    } catch (error) {
        console.error('❌ 주변 정류장 데이터를 가져오는 데 실패했습니다:', error.message);
        return null;
    }
}

// --- e. 서울시 좌표기반 정류소 조회 ---
async function getStationByPos(lat, lng) {
    // 서울시 API는 tmX, tmY 좌표계를 사용할 수도 있으나, 
    // 최근 API는 WGS84(gpsX, gpsY)를 지원하는 경우가 많음.
    // 여기서는 백엔드에서 좌표 변환이나 적절한 파라미터 처리를 한다고 가정하고 lat, lng를 보냄.
    const tradeUrl = `http://localhost:3000/eatate/getStationByPos?tmX=${lng}&tmY=${lat}`;
    try {
        const response = await fetch(tradeUrl);
        if (!response.ok) {
            throw new Error(`서버 요청 실패: ${response.status} ${response.statusText}`);
        }
        const locationData = await response.json();
        return locationData;

    } catch (error) {
        console.error('❌ 서울시 주변 정류장 데이터를 가져오는 데 실패했습니다:', error.message);
        return null;
    }
}
