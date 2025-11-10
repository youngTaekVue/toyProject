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
        script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false&libraries=clusterer`;

        script.onload = () => {
            kakao.maps.load(() => {
                const container = document.getElementById('map');

                // 데이터의 첫 번째 위치를 지도의 중심으로 설정
                const centerLat = data[0]?.lat || 37.566826;
                const centerLng = data[0]?.lng || 126.9786567;

                const options = {
                    center: new kakao.maps.LatLng(centerLat, centerLng)
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


// --- D. 마커 표시 함수 (클러스터러 적용) ---
// --- D. 마커 표시 함수 (클러스터러 적용) ---
function displayMarkers(map, data) {
    let bounds = new kakao.maps.LatLngBounds();
    const markers = []; // 1. 모든 유효한 마커 객체를 담을 배열을 선언합니다.

    data.forEach(item => {
        // 좌표값이 유효하고, Geocoding이 성공한 항목만 처리
        if (item.lat && item.lng && item.status === 'SUCCESS') {
            const position = new kakao.maps.LatLng(item.lat, item.lng);

            // 2. 마커 생성 시 map 속성을 제거합니다.
            const marker = new kakao.maps.Marker({
                position: position,
                title: item.name
            });

            // 인포윈도우 및 이벤트 로직 (개별 마커에 연결)
            const infowindow = new kakao.maps.InfoWindow({
                content: `<div style="padding:5px;font-size:12px;">${item.name}<br>(${item.road_address})</div>`
            });

            // 마커 클릭 시 인포윈도우 표시
            kakao.maps.event.addListener(marker, 'click', function () {
                infowindow.open(map, marker);
            });

            // 3. 생성된 마커를 배열에 추가합니다.
            markers.push(marker);
            bounds.extend(position);
        }
    });

    // 4. 반복문 종료 후, 마커 클러스터러를 생성 및 마커를 추가합니다.
    const clusterer = new kakao.maps.MarkerClusterer({
        map: map,
        averageCenter: true,
        minLevel: 2, // 💡 8,000개에 적합하도록 minLevel을 6으로 조정 (레벨 5부터 개별 마커 표시)
        markers: markers // 💡 클러스터러 생성 시 마커 배열을 추가
    });

      clusterer.addMarkers(markers);
     clusterer.removeMarker(markers);


    if (!bounds.isEmpty()) {
        map.setBounds(bounds);
    }

    console.log(`✅ 클러스터러를 사용하여 지도에 ${markers.length}개의 마커를 표시했습니다.`);
}

// --- A. 서버에서 API 키 설정 가져오기 (수정됨) ---
async function format() {
    const apiUrl = 'http://localhost:3000/api/locations'; // 서버 라우터 경로

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


// ⭐ 애플리케이션 시작 ⭐
initMapAndData();
//format();