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
    const mapConfig = await fetchKakaMapConfig();
    if (!mapConfig) return;

    // 2. 초기 데이터 로드 제거 (요청사항 반영)
    // fetchBusSationData() 및 getSeoulBusStationListv2() 호출 제거
    // 초기에는 빈 배열로 시작하고, 지도 로드 후 위치 기반으로 데이터를 채웁니다.
    allStoreData = [];

    document.getElementById('loading-message').style.display = 'none';

    // 3. 카카오맵 SDK 동적 로드 및 지도 초기화
    await loadKakaoMapSDK(mapConfig);
}

// --- C. 카카오맵 SDK 로드 및 지도/이벤트 리스너 등록 (수정됨) ---
async function loadKakaoMapSDK(mapConfig) {
    const apiKey = mapConfig.kakaoMapAppKey;

    if (!apiKey) {
        console.error("카카오맵 API Key가 config 객체에 없습니다.");
        return;
    }

    return new Promise((resolve) => {

        const script = document.createElement('script');
        script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false&libraries=clusterer`;

        script.onload = () => {
            kakao.maps.load(() => {
                const container = document.getElementById('map');
                // 기본 좌표 (수원역 부근 예시)
                const defaultCenterLat = 37.269885;
                const defaultCenterLng = 126.956596;
                const defaultLevel = 2;

                const options = {
                    center: new kakao.maps.LatLng(defaultCenterLat, defaultCenterLng),
                    level: defaultLevel
                };

                map = new kakao.maps.Map(container, options);
                map.setMaxLevel(7);
                console.log('✅ 카카오맵 초기화 완료!');

                clusterer = new kakao.maps.MarkerClusterer({
                    map: map,
                    averageCenter: true,
                    minLevel: 6,
                });

                // ⭐ 지도 이동/줌 이벤트 리스너 등록 ⭐
                // 지도 이동이 멈추면(dragend) 중심 좌표를 기준으로 주변 정류장 데이터를 다시 불러옵니다.
                const updateDelayed = debounce(async () => {
                    await loadAndDisplayStationsAroundCenter();
                }, 500); 

                kakao.maps.event.addListener(map, 'dragend', updateDelayed);
                kakao.maps.event.addListener(map, 'zoom_changed', updateDelayed);

                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(async (position) => {
                        // 성공: 현재 위치로 지도 이동
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        const locPosition = new kakao.maps.LatLng(lat, lng);

                        displayMyLocationMarker(locPosition);
                        map.setCenter(locPosition);
                        map.setLevel(4, { animate: true });

                        // 현재 위치 기준으로 데이터 로드 및 표시
                        await loadAndDisplayStationsAroundCenter();

                    }, (err) => {
                        // 실패: 기본 위치 사용
                        console.warn('Geolocation error: ' + err.message);
                        const defaultPosition = new kakao.maps.LatLng(defaultCenterLat, defaultCenterLng);
                        map.setCenter(defaultPosition);
                        map.setLevel(defaultLevel);
                        
                        // 기본 위치 기준으로 데이터 로드 및 표시
                        loadAndDisplayStationsAroundCenter();
                    });
                } else {
                    // Geolocation 미지원
                    console.warn('Geolocation is not supported by this browser.');
                    loadAndDisplayStationsAroundCenter();
                }

                resolve();
            });
        };
        document.head.appendChild(script);
    });
}

// ⭐ 중심 좌표 기준 데이터 로드 및 마커 업데이트 공통 함수 ⭐
async function loadAndDisplayStationsAroundCenter() {
    if (!map) return;

    const center = map.getCenter();
    const lat = center.getLat();
    const lng = center.getLng();

    console.log(center)

    // 중심 좌표 기준으로 주변 정류장 데이터 가져오기
    const aroundStations = await getBusStationAroundListv2(lat, lng);
    
    if (aroundStations && Array.isArray(aroundStations) && aroundStations.length > 0) {
        const mappedAroundData = aroundStations.map(item => ({
            ...item,
            WGS84_LAT: item.y, // API 응답 필드 확인 (y가 위도)
            WGS84_LOGT: item.x, // API 응답 필드 확인 (x가 경도)
            name: item.stationName,
            STTN_ID: item.stationId,
            STTN_NM_INFO: item.stationName
        }));
        
        // 중복 제거 후 데이터 병합
        const existingIds = new Set(allStoreData.map(d => d.STTN_ID || d.id));
        const newItems = mappedAroundData.filter(d => !existingIds.has(d.STTN_ID));
        
        if (newItems.length > 0) {
            allStoreData = [...allStoreData, ...newItems];
            console.log(`✅ ${newItems.length}개의 새로운 정류장 데이터를 추가했습니다.`);
        }
    }

    // 마커 및 카드 업데이트
    updateMarkersAndCards(map);
}

function displayMyLocationMarker(locPosition) {
    const imageSize = new kakao.maps.Size(24, 35);
    const markerImage = new kakao.maps.MarkerImage("https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png", imageSize); 
    
    new kakao.maps.Marker({
        map: map,
        position: locPosition,
        title: "내 위치",
        image: markerImage
    });
}

function debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}

function filterDataInBounds(currentMap) {
    const bounds = currentMap.getBounds();
    const filteredData = [];
    for (const item of allStoreData) {
        const lat = parseFloat(item.WGS84_LAT);
        const lng = parseFloat(item.WGS84_LOGT);

        if (!isNaN(lat) && !isNaN(lng)) {
            const point = new kakao.maps.LatLng(lat, lng);
            if (bounds.contain(point)) {
                filteredData.push(item);
            }
        }
    }
    return filteredData;
}

function updateMarkersAndCards(currentMap) {
    clusterer.clear();
    markerMap.clear();

    const visibleData = filterDataInBounds(currentMap);
    console.log(`🔎 지도 영역 내 정류장: ${visibleData.length}개`);
    
    const markersToAdd = [];
    const imageSize = new kakao.maps.Size(15, 25);
    const imageUrl = '/images/markers.png';
    const image = new kakao.maps.MarkerImage(imageUrl, imageSize);

    visibleData.forEach(item => {
        const position = new kakao.maps.LatLng(parseFloat(item.WGS84_LAT), parseFloat(item.WGS84_LOGT));
        const marker = new kakao.maps.Marker({
            position: position,
            title: item.name,
            image: image,
        });

        const id = item.STTN_ID || item.id;
        markerMap.set(id, { marker: marker, data: item });
        markersToAdd.push(marker);

        const infowindow = new kakao.maps.InfoWindow({
            content: `<div style="padding:5px;font-size:12px;">${item.name || item.STTN_NM_INFO}<br>(${item.road_address || '주소 없음'})</div>`,
            removable: true
        });

        kakao.maps.event.addListener(marker, 'click', function () {
            infowindow.open(currentMap, marker);
            highlightCard(id);
            currentMap.panTo(position);
        });
    });

    clusterer.addMarkers(markersToAdd);
    updateStoreCards(visibleData);
}

function updateStoreCards(data) {
    const cardListContainer = document.getElementById('card-list');
    cardListContainer.innerHTML = '';
    activeCardElement = null;

    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'store-card';
        const id = item.STTN_ID || item.id;
        card.dataset.id = id;

        card.innerHTML = `
            <h3>${item.STTN_NM_INFO || item.name}</h3>
            <p>📍 ${item.CNTR_CARTRK_DIV || ''}${item.JURISD_INST_NM || ''}</p>
            <p>정류장번호: ${id || '정보 없음'}</p>
        `;

        card.addEventListener('click', () => {
            moveToCoords(item.WGS84_LAT, item.WGS84_LOGT, id);
        });

        cardListContainer.appendChild(card);
    });

    if (data.length === 0) {
        cardListContainer.innerHTML = '<p class="text-center text-muted mt-4">지도 영역에 정류장이 없습니다.</p>';
    }
}

function moveToCoords(lat, lng, id) {
    const position = new kakao.maps.LatLng(parseFloat(lat), parseFloat(lng));
    if (map) {
        map.panTo(position);
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
