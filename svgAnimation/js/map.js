// --- 전역 변수 설정 ---
// 지도를 저장할 변수
let map = null;
// 마커 객체와 해당 데이터(id)를 매핑하여 저장
const markerMap = new Map();
// 현재 선택된 카드를 추적
let activeCardElement = null;


// -------------------------------------------------------------
// ⭐ 통합 함수: 지도 로드, 데이터 로드, 마커 표시, 카드 생성 순차 처리
// -------------------------------------------------------------
async function initMapAndData() {

    // 1. 서버에서 카카오맵 API 키 가져오기
    const mapConfig = await fetchMapConfig();
    if (!mapConfig) return;

    // 2. Geocoding 결과 JSON 파일 데이터 가져오기
    const locationData = await fetchLocationData();
    if (!locationData || locationData.length === 0) {
        console.warn('표시할 Geocoding 데이터가 없습니다.');
        document.getElementById('loading-message').textContent = '표시할 데이터가 없습니다.';
        return;
    }
    document.getElementById('loading-message').style.display = 'none';

    // 3. 카카오맵 SDK 동적 로드 및 지도 초기화
    await loadKakaoMapSDK(mapConfig, locationData);

    // 4. 지도 초기화 후, 카드 목록 생성 (새로 추가된 로직)
    if (map) {
        createStoreCards(locationData);
    }
}


// --- A. 서버에서 API 키 설정 가져오기 (제공된 코드와 동일) ---
async function fetchMapConfig() {
    const apiUrl = 'http://localhost:3000/mapkey/getkey'; // 서버 라우터 경로

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


// --- B. 서버의 JSON 파일 데이터를 가져오기 (제공된 코드와 동일) ---
async function fetchLocationData() {
    const tradeUrl = 'http://localhost:3000/files/geocoding.json';

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





// --- C. 카카오맵 SDK 로드 및 지도/마커 표시 (글로벌 map 변수 저장 및 마커 로직 수정) ---
async function loadKakaoMapSDK(mapConfig, data) {
    const apiKey = mapConfig.kakaoMapAppKey;
    if (!apiKey) {
        console.error("카카오맵 API Key가 config 객체에 없습니다.");
        return;
    }

    return new Promise((resolve) => {
        const script = document.createElement('script');

        script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false&libraries=clusterer`;




        script.onload = () => {
            kakao.maps.load(() => {
                const container = document.getElementById('map');


                const centerLat = data[0]?.lat || 37.566826;
                const centerLng = data[0]?.lng || 126.9786567;

                const options = {
                    center: new kakao.maps.LatLng(centerLat, centerLng),
                    level: 3 // 적절한 초기 줌 레벨 설정
                };

                // ⭐ 전역 map 변수에 지도 객체 저장 ⭐
                map = new kakao.maps.Map(container, options);
                console.log('✅ 카카오맵 초기화 완료!');

                // 마커 표시 로직 실행
                displayMarkers(map, data);

                resolve();
            });
        };
        document.head.appendChild(script);
    });
}


// --- D. 마커 표시 함수 (클러스터러 적용 및 markerMap 업데이트) ---
function displayMarkers(currentMap, data) {
    let bounds = new kakao.maps.LatLngBounds();
    const markers = [];
    var imageSize = new kakao.maps.Size(35, 35);
    // 실제 이미지 경로로 수정하세요
    var imageUrl = '/images/markers.png';
    var image = new kakao.maps.MarkerImage(imageUrl, imageSize);

    // markerMap 초기화
    markerMap.clear();

    data.forEach(item => {
        // 유효한 항목만 처리
        if (item.lat && item.lng && item.status === 'SUCCESS') {
            const position = new kakao.maps.LatLng(item.lat, item.lng);


            const marker = new kakao.maps.Marker({
                position: position,
                title: item.name,
                image: image
            });
            console.log(item);
            // ⭐ markerMap에 마커와 데이터를 연결하여 저장 ⭐
            // item.id가 유니크한 키라고 가정
            markerMap.set(item.id, { marker: marker, data: item });

            // 인포윈도우 생성
            const infowindow = new kakao.maps.InfoWindow({
                content: `<div style="padding:5px;font-size:12px;">${item.name}<br>(${item.road_address})</div>`
            });

            // 마커 클릭 시 인포윈도우 표시 및 카드 활성화
            kakao.maps.event.addListener(marker, 'click', function () {
                infowindow.open(currentMap, marker);
                // 해당 마커에 연결된 카드를 활성화
                highlightCard(item.id);
                // 지도의 중심으로 이동
                currentMap.panTo(position);
            });


            markers.push(marker);
            bounds.extend(position);
        }
    });

    // 마커 클러스터러 생성 및 마커 추가
    const clusterer = new kakao.maps.MarkerClusterer({
        map: currentMap,
        averageCenter: true,
        minLevel: 6,
        markers: markers
    });





    // if (!bounds.isEmpty()) {
    //     currentMap.setBounds(bounds);
    // }

    console.log(`✅ 클러스터러를 사용하여 지도에 ${markers.length}개의 마커를 표시했습니다.`);
}





// -------------------------------------------------------------
// ⭐ 카드 목록 생성 및 이벤트 처리 (새로 추가된 로직)
// -------------------------------------------------------------

function createStoreCards(data) {
    const cardListContainer = document.getElementById('card-list');

    data.forEach(item => {
        // 마커가 표시된 항목만 카드로 생성 (status=SUCCESS 가정)
        if (item.lat && item.lng && item.status === 'SUCCESS') {
            const card = document.createElement('div');
            card.className = 'store-card';
            // ⭐ data-id 속성에 고유 ID 저장 (마커와 연결을 위해 중요) ⭐
            card.dataset.id = item.id;

            // 카드 내용 구성
            card.innerHTML = `
                <h3>${item.name}</h3>
                <p>📍 ${item.address}</p>
                <p>도로명: ${item.road_address || '정보 없음'}</p>
            `;

            // 카드 클릭 이벤트 리스너 추가
            card.addEventListener('click', () => {
                // 1. 지도 이동 및 마커 활성화
                moveToMarker(item.id);
                // 2. 카드 활성화 상태 업데이트
                highlightCard(item.id);
            });

            cardListContainer.appendChild(card);
        }
    });
}


/**
 * 특정 ID의 카드로 스크롤 이동하고 활성화 클래스를 적용합니다.
 * @param {string | number} id - 판매점의 고유 ID
 */
function highlightCard(id) {
    // 이전 활성화 카드 비활성화
    if (activeCardElement) {
        activeCardElement.classList.remove('active');
    }

    // 새 카드 찾기 및 활성화
    const newActiveCard = document.querySelector(`.store-card[data-id="${id}"]`);
    if (newActiveCard) {
        newActiveCard.classList.add('active');
        activeCardElement = newActiveCard;

        // 카드 목록 스크롤을 해당 카드가 보이도록 이동
        newActiveCard.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });
    }
}

/**
 * 특정 ID의 마커 위치로 지도를 이동시키고 마커를 클릭합니다.
 * @param {string | number} id - 판매점의 고유 ID
 */
function moveToMarker(id) {
    const markerInfo = markerMap.get(id);

    if (map && markerInfo) {
        const position = markerInfo.marker.getPosition();

        // 지도를 해당 마커 위치로 이동
        map.panTo(position);

        // 마커 클릭 이벤트 강제 실행 (인포윈도우 표시)
        kakao.maps.event.trigger(markerInfo.marker, 'click');
    }
}


// ⭐ 애플리케이션 시작 ⭐
initMapAndData();
