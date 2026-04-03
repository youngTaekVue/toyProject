// --- 전역 변수 설정 ---
// 지도를 저장할 변수
let map = null;
const markerMap = new Map();
let activeCardElement = null;
let allStoreData = [];
let clusterer = null; // ⭐ 클러스터러 객체 전역 변수 추가 ⭐

// -------------------------------------------------------------
// ⭐ 통합 함수: 지도 로드, 데이터 로드, 마커 표시, 카드 생성 순차 처리
// -------------------------------------------------------------
async function initMapAndData() {
    // 1. 서버에서 카카오맵 API 키 가져오기
    const mapConfig = await fetchKakaoMapConfig();
    if (!mapConfig) return;

    // 2. Geocoding 결과 JSON 파일 데이터 가져오기
    const locationData = await fetchLocationData();
    if (!locationData || locationData.length === 0) {
        console.warn('표시할 Geocoding 데이터가 없습니다.');
        document.getElementById('loading-message').textContent = '표시할 데이터가 없습니다.';
        return;
    }
    document.getElementById('loading-message').style.display = 'none';

    // ⭐ 전체 데이터를 전역 변수에 저장
    allStoreData = locationData;

    // 3. 카카오맵 SDK 동적 로드 및 지도 초기화
    await loadKakaoMapSDK(mapConfig);

    // 4. 지도 초기화 후, 초기 마커 및 카드 목록 생성
    if (map) {
        // 최초 로드 시, 필터링된 데이터로 마커와 카드 목록을 업데이트합니다.
        updateMarkersAndCards(map);
    }
}

// --- B. 서버의 JSON 파일 데이터를 가져오기 ---
async function fetchLocationData() {
    const tradeUrl = 'http://localhost:3000/files/geocoding_lotto.json';
    console.log(tradeUrl)
    try {
        const response = await fetch(tradeUrl);

        if (!response.ok) {
            throw new Error(`서버 요청 실패: ${response.status} ${response.statusText}`);
        }
        const locationData = await response.json();
        console.log(locationData)
        console.log('✅ Geocoding 데이터 수신 완료:', locationData.length, '개');
        return locationData;

    } catch (error) {
        console.error('❌ Geocoding 데이터를 가져오는 데 실패했습니다:', error.message);
        return null;
    }
}

// --- C. 카카오맵 SDK 로드 및 지도/이벤트 리스너 등록 (클러스터러 라이브러리 포함) ---
async function loadKakaoMapSDK(mapConfig) {
    const apiKey = mapConfig.kakaoMapAppKey;
    if (!apiKey) {
        console.error("카카오맵 API Key가 config 객체에 없습니다.");
        return;
    }

    return new Promise((resolve) => {
        const script = document.createElement('script');
        // ⭐ 클러스터러 라이브러리 다시 포함 ⭐
        script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false&libraries=clusterer`;

        script.onload = () => {
            kakao.maps.load(() => {
                const container = document.getElementById('map');

                const firstData = allStoreData.find(item => item.lat && item.lng && item.status === 'SUCCESS');
                const centerLat = 37.269885;
                const centerLng = 126.956596;

                const options = {
                    center: new kakao.maps.LatLng(centerLat, centerLng),
                    level: 2
                };

                map = new kakao.maps.Map(container, options);
                map.setMaxLevel(7);
                console.log('✅ 카카오맵 초기화 완료!');

                // ⭐ 클러스터러 객체 초기화 (전역 변수 저장) ⭐
                clusterer = new kakao.maps.MarkerClusterer({
                    map: map,
                    averageCenter: true,
                    minLevel: 6, // ⭐ 요청하신 레벨 6 설정 ⭐
                });

                // ⭐ 핵심: 지도 이동/줌 이벤트 리스너 등록 ⭐
                const updateDelayed = debounce(() => updateMarkersAndCards(map), 200);
                kakao.maps.event.addListener(map, 'dragend', updateDelayed);
                kakao.maps.event.addListener(map, 'zoom_changed', updateDelayed);


                resolve();
            });
        };
        document.head.appendChild(script);
    });
}

// --- E. 디바운스 함수 ---
function debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}


// --- F. 지도 영역 내 데이터 필터링 ---
function filterDataInBounds(currentMap) {
    const bounds = currentMap.getBounds();
    const filteredData = [];
    for (const item of allStoreData) {
        if (item.lat && item.lng && item.status === 'SUCCESS') {
            const point = new kakao.maps.LatLng(item.lat, item.lng);

            if (bounds.contain(point)) {
                filteredData.push(item);
            }
        }
    }
    return filteredData;
}


// --- G. 마커와 카드 목록을 지도 영역 기반으로 업데이트 (클러스터러 적용) ---
function updateMarkersAndCards(currentMap) {
    // 1. 기존 클러스터러 마커 모두 제거
    // clusterer.clear()는 이전에 추가된 모든 마커를 제거합니다.
    clusterer.clear();
    markerMap.clear(); // markerMap 초기화 (새로 마커를 생성할 것이므로)

    // 2. 지도 영역 내 데이터 필터링
    const visibleData = filterDataInBounds(currentMap);
    console.log(`🔎 지도 영역 내 판매점: ${visibleData.length}개`);

    // 3. 필터링된 데이터로 마커 생성 및 클러스터러에 추가
    const markersToAdd = [];
    const imageSize = new kakao.maps.Size(35, 35);
    var imageUrl = '/images/markers.png';
    var image = new kakao.maps.MarkerImage(imageUrl, imageSize);

    visibleData.forEach(item => {
        const position = new kakao.maps.LatLng(item.lat, item.lng);
        const marker = new kakao.maps.Marker({
            position: position,
            title: item.name,
            image: image,
            // map: currentMap 설정은 클러스터러가 대신 처리합니다.
        });

        // markerMap에 저장 및 인포윈도우/클릭 이벤트 등록
        markerMap.set(item.id, { marker: marker, data: item });
        markersToAdd.push(marker); // 클러스터러에 추가할 배열에 저장

        // 인포윈도우 생성
        const infowindow = new kakao.maps.InfoWindow({
            content: `<div style="padding:5px;">내용입니다.</div><div style="padding:5px;font-size:12px;">${item.name}<br>(${item.road_address})<button onclick="closeInfowindow(${item.no})">닫기</button></div>`
        });

        // 마커 클릭 시 인포윈도우 표시 및 카드 활성화
        kakao.maps.event.addListener(marker, 'click', function () {
            infowindow.open(currentMap, marker);
            highlightCard(item.id);
            currentMap.panTo(position);
        });
    });

    // ⭐ 필터링된 마커들만 클러스터러에 추가합니다. ⭐
    clusterer.addMarkers(markersToAdd);

    // 4. 필터링된 데이터로 카드 목록 업데이트
    updateStoreCards(visibleData);
}
function closeInfowindow(param) {
    console.log(param);
    // 닫고자 하는 인포윈도우 객체의 .close() 메서드를 호출합니다.
    // ID를 사용하여 저장된 인포윈도우 객체를 가져옵니다.
    const targetInfowindow = infowindowMap.get(param);

    if (targetInfowindow) {
        targetInfowindow.close();
        infowindowMap.delete(param); // 닫은 후 맵에서 제거
    }
}
// --- H. 카드 목록 업데이트 함수 (수정됨: 카드 클릭 이벤트 등록) ---
function updateStoreCards(data) {
    const cardListContainer = document.getElementById('card-list');

    // 1. 기존 카드 목록 제거
    cardListContainer.innerHTML = '';

    // 2. 활성화 상태 초기화
    activeCardElement = null;

    // 3. 필터링된 데이터로 카드 목록 재생성
    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'store-card';
        card.dataset.lat = item.lat;
        card.dataset.lng = item.lng;
        card.dataset.id = item.no; // ⭐ ID 설정 (하이라이팅에 필요) ⭐

        card.innerHTML = `
            <h3>${item.name}</h3>
            <p>📍 ${item.address}</p>
            <p>도로명: ${item.road_address || '정보 없음'}</p>
        `;

        // ⭐ 카드 클릭 이벤트: 좌표로 이동 및 마커 활성화 ⭐
        card.addEventListener('click', () => {
            moveToCoords(item.lat, item.lng, item.id);
        });

        cardListContainer.appendChild(card);
    });

    console.log(`✅ 카드 목록을 ${data.length}개로 업데이트했습니다.`);
}

// --- I. 마커/카드 상호작용 함수 (새로운 함수 추가) ---

// ⭐ 새로 추가된 함수: 좌표로 이동 및 마커/카드 활성화 ⭐
function moveToCoords(lat, lng, id) {
    const position = new kakao.maps.LatLng(lat, lng);
    if (map) {
        // 1. 지도 중심을 해당 좌표로 부드럽게 이동
        map.panTo(position);

        // // 2. 해당 ID의 마커가 있다면 클릭 이벤트 발생 (인포윈도우 표시)
        // const markerInfo = markerMap.get(id);
        // if (markerInfo) {
        //     // 마커 클릭 이벤트를 강제로 발생시켜 인포윈도우를 엽니다.
        //     kakao.maps.event.trigger(markerInfo.marker, 'click');
        // }

        // 3. 카드 하이라이팅 및 스크롤
        highlightCard(id);
    }
}


function highlightCard(id) {
    if (activeCardElement) {
        activeCardElement.classList.remove('active');
    }

    const newActiveCard = document.querySelector(`.store-card[data-id="${id}"]`);
    if (newActiveCard) {
        newActiveCard.classList.add('active');
        activeCardElement = newActiveCard;

        newActiveCard.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });
    }
}

// ⭐ 애플리케이션 시작 ⭐
initMapAndData();