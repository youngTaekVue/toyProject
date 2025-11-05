// -------------------------------------------------------------
// ⭐ 통합 함수: 지도 로드, 데이터 로드, 마커 표시를 순차적으로 처리
// -------------------------------------------------------------
async function initMapAndData() {

    // 1. 서버에서 카카오맵 API 키 가져오기
    const mapConfig = await fetchMapConfig();
    if (!mapConfig) return;

    // 2. Geocoding 결과 JSON 파일 데이터 가져오기
    const locationData = await fetchLocationData();
    if (!locationData || locationData.length === 0) {
        console.warn('표시할 Geocoding 데이터가 없습니다.');
        return;
    }

    // 3. 카카오맵 SDK 동적 로드 및 초기화
    await loadKakaoMapSDK(mapConfig, locationData); // mapConfig 객체 전달
}


// --- A. 서버에서 API 키 설정 가져오기 (수정됨) ---
async function fetchMapConfig() {
    const apiUrl = 'http://localhost:3000/mapkey/getkey'; // 서버 라우터 경로

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            console.error(`HTTP Error: ${response.status} - ${response.statusText}`);
            const errorBody = await response.text();
            throw new Error(`Failed to fetch config. Server response: ${errorBody}`);
        }
        // ⭐ 수정: response.json() 호출 ⭐
        const config = await response.json();
        return config;

    } catch (error) {
        console.error('❌ API 키 설정을 가져오는 데 실패했습니다:', error.message);
        return null;
    }
}


// --- B. 서버의 JSON 파일 데이터를 가져오기 (동일) ---
async function fetchLocationData() {
    const tradeUrl = 'http://localhost:3000/files/geocoding.json';

    try {
        const response = await fetch(tradeUrl);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`서버 요청 실패: ${response.status} ${response.statusText} - ${errorText}`);
        }
        const locationData = await response.json();
        console.log('✅ Geocoding 데이터 수신 완료:', locationData.length, '개');
        return locationData;

    } catch (error) {
        console.error('❌ Geocoding 데이터를 가져오는 데 실패했습니다:', error.message);
        return null;
    }
}


// --- C. 카카오맵 SDK 로드 및 지도/마커 표시 (수정됨) ---
async function loadKakaoMapSDK(mapConfig, data) { // mapConfig 객체를 인수로 받음

    // ⭐ 수정: mapConfig 객체에서 kakaoMapAppKey 추출 ⭐
    const apiKey = mapConfig.kakaoMapAppKey;
    if (!apiKey) {
        console.error("카카오맵 API Key가 config 객체에 없습니다.");
        return;
    }

    return new Promise((resolve) => {
        const script = document.createElement('script');
        // apiKey 변수를 사용하여 SDK 로드 URL 생성
        script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false`;

        script.onload = () => {
            kakao.maps.load(() => {
                const container = document.getElementById('map');

                // 데이터의 첫 번째 위치를 지도의 중심으로 설정
                const centerLat = data[0]?.lat || 37.566826;
                const centerLng = data[0]?.lng || 126.9786567;

                const options = {
                    center: new kakao.maps.LatLng(centerLat, centerLng),
                    level: 7
                };
                const map = new kakao.maps.Map(container, options);
                console.log('✅ 카카오맵 초기화 완료!');

                // ⭐ 마커 표시 로직 실행 ⭐
                displayMarkers(map, data);

                resolve();
            });
        };
        document.head.appendChild(script);
    });
}


// --- D. 마커 표시 함수 (동일) ---
function displayMarkers(map, data) {
    let bounds = new kakao.maps.LatLngBounds();

    data.forEach(item => {
        // 좌표값이 유효하고, Geocoding이 성공한 항목만 표시
        if (item.lat && item.lng && item.geocoding_status === 'SUCCESS') {
            const position = new kakao.maps.LatLng(item.lat, item.lng);

            // ... (마커 생성 및 인포윈도우 로직) ...
            const marker = new kakao.maps.Marker({
                map: map,
                position: position,
                title: item.상호명
            });

            const infowindow = new kakao.maps.InfoWindow({
                content: `<div style="padding:5px;font-size:12px;">${item.상호명}<br>(${item.도로명주소})</div>`
            });

            kakao.maps.event.addListener(marker, 'click', function() {
                infowindow.open(map, marker);
            });

            bounds.extend(position);
        }
    });

    if (!bounds.isEmpty()) {
        map.setBounds(bounds);
    }

    console.log(`✅ 지도에 ${data.filter(i => i.geocoding_status === 'SUCCESS').length}개의 마커를 표시했습니다.`);
}


// ⭐ 애플리케이션 시작 ⭐
initMapAndData();