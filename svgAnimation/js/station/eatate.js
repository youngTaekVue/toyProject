// --- 전역 변수 설정 ---
let map = null;
const markerMap = new Map();
let activeCardElement = null;
let allStoreData = [];
let clusterer = null;
let currentSelectedMarker = null;
let currentInfoWindow = null;
let currentStationId = null; // API 호출에 사용될 실제 정류장 ID (접두사 없음)
let currentStationUniqueId = null; // UI 상태 관리에 사용될 고유 ID (접두사 포함)

let markerImage = null;
let selectedMarkerImage = null;

let favoriteRoutes = JSON.parse(localStorage.getItem('favoriteRoutes')) || [];

// -------------------------------------------------------------
// ⭐ 통합 함수
// -------------------------------------------------------------
async function initMapAndData() {
    const mapConfig = await fetchKakaMapConfig();
    if (!mapConfig) return;

    allStoreData = [];
    document.getElementById('loading-message').style.display = 'none';
    await loadKakaoMapSDK(mapConfig);
}

// --- C. 카카오맵 SDK 로드 ---
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
                markerImage = new kakao.maps.MarkerImage('/images/markers.png', new kakao.maps.Size(15, 25));
                selectedMarkerImage = new kakao.maps.MarkerImage('/images/marker_selected.png', new kakao.maps.Size(15, 25));

                const container = document.getElementById('map');
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

                const updateDelayed = debounce(async () => {
                    await loadAndDisplayStationsAroundCenter();
                }, 500);

                kakao.maps.event.addListener(map, 'dragend', updateDelayed);
                kakao.maps.event.addListener(map, 'zoom_changed', updateDelayed);

                kakao.maps.event.addListener(map, 'click', function() {
                    deselectAll();
                });

                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(async (position) => {
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        const locPosition = new kakao.maps.LatLng(lat, lng);

                        displayMyLocationMarker(locPosition);
                        map.setCenter(locPosition);
                        map.setLevel(4, { animate: true });
                        await loadAndDisplayStationsAroundCenter();

                    }, async (err) => {
                        console.warn('Geolocation error: ' + err.message);
                        await loadAndDisplayStationsAroundCenter();
                    });
                } else {
                    console.warn('Geolocation is not supported by this browser.');
                    loadAndDisplayStationsAroundCenter();
                }

                const lastStationId = localStorage.getItem('lastStationId');
                const lastStationName = localStorage.getItem('lastStationName');
                const lastStationUniqueId = localStorage.getItem('lastStationUniqueId'); // ⭐ 추가: uniqueId도 저장

                if (lastStationId && lastStationName && lastStationUniqueId) {
                    setTimeout(() => {
                        // ⭐ openDetailView에 uniqueId도 전달 ⭐
                        openDetailView(lastStationId, lastStationName, lastStationUniqueId);
                    }, 300);
                }

                resolve();
            });
        };
        document.head.appendChild(script);
    });
}

function deselectAll() {
    if (currentSelectedMarker) {
        currentSelectedMarker.setImage(markerImage);
        currentSelectedMarker = null;
    }
    if (activeCardElement) {
        activeCardElement.classList.remove('active');
        activeCardElement = null;
    }
    if (currentInfoWindow) {
        currentInfoWindow.close();
        currentInfoWindow = null;
    }
    closeDetailView();
}

// ⭐ 중심 좌표 기준 데이터 로드 및 마커 업데이트 (서울 + 경기 병합 및 중복 처리 강화) ⭐
async function loadAndDisplayStationsAroundCenter() {
    if (!map) return;
    const center = map.getCenter();
    const lat = center.getLat();
    const lng = center.getLng();

    try {
        // 1. 경기도 & 서울 API 동시 호출
        const [gyeonggiData, seoulData] = await Promise.all([
            getBusStationAroundListv2(lat, lng),
            getStationByPos(lat, lng)
        ]);

        let mergedData = [];

        // 2. 경기도 데이터 매핑
        if (gyeonggiData && Array.isArray(gyeonggiData)) {
            const mappedGyeonggi = gyeonggiData.map(item => ({
                ...item,
                uniqueId: 'GG_' + item.stationId, // ⭐ 고유 ID 생성 ⭐
                apiStationId: item.stationId, // ⭐ API 호출용 ID 저장 ⭐
                WGS84_LAT: item.y, 
                WGS84_LOGT: item.x,
                name: item.stationName, 
                STTN_NM_INFO: item.stationName,
                source: 'gyeonggi'
            }));
            mergedData = [...mappedGyeonggi];
        }

        // 3. 서울 데이터 매핑
        if (seoulData && Array.isArray(seoulData)) {
            const mappedSeoul = seoulData.map(item => ({
                ...item,
                // ⭐ 서울은 arsId를 우선 사용, 없으면 stationId 폴백 ⭐
                uniqueId: 'SL_' + (item.arsId || item.stationId), // ⭐ 고유 ID 생성 ⭐
                apiStationId: item.arsId || item.stationId, // ⭐ API 호출용 ID 저장 ⭐
                WGS84_LAT: item.gpsY, 
                WGS84_LOGT: item.gpsX,
                name: item.stationNm, 
                STTN_NM_INFO: item.stationNm,
                source: 'seoul'
            }));
            mergedData = [...mergedData, ...mappedSeoul];
        }
console.log(mergedData)
        // 4. 중복 제거 및 기존 데이터 병합
        if (mergedData.length > 0) {
            // 기존 데이터의 uniqueId 집합
            const existingUniqueIds = new Set(allStoreData.map(d => d.uniqueId));
            
            // 새로 받아온 데이터 중 uniqueId 기준으로 중복되지 않는 것만 필터링
            const newItems = mergedData.filter(d => !existingUniqueIds.has(d.uniqueId));
            
            if (newItems.length > 0) {
                allStoreData = [...allStoreData, ...newItems];
            }
        }

    } catch (error) {
        console.error('❌ 주변 정류장 데이터 로드 실패:', error);
    }
    updateMarkersAndCards(map);
}

function displayMyLocationMarker(locPosition) {
    const imageSize = new kakao.maps.Size(24, 35);
    const myLocationImage = new kakao.maps.MarkerImage("https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png", imageSize); 
    new kakao.maps.Marker({ map: map, position: locPosition, title: "내 위치", image: myLocationImage });
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
    return allStoreData.filter(item => {
        const lat = parseFloat(item.WGS84_LAT);
        const lng = parseFloat(item.WGS84_LOGT);
        if (!isNaN(lat) && !isNaN(lng)) {
            return bounds.contain(new kakao.maps.LatLng(lat, lng));
        }
        return false;
    });
}

// ⭐ 마커와 카드 목록 업데이트 (uniqueId 사용) ⭐
function updateMarkersAndCards(currentMap) {
    clusterer.clear();
    const visibleData = filterDataInBounds(currentMap);
    
    const markersToAdd = [];
    visibleData.forEach(item => {
        const uniqueId = item.uniqueId; // ⭐ uniqueId 사용 ⭐
        let marker, infowindow;
        
        if (markerMap.has(uniqueId)) {
            const storedItem = markerMap.get(uniqueId);
            marker = storedItem.marker;
            infowindow = storedItem.infowindow;
            
            if (currentStationUniqueId !== uniqueId) { // ⭐ currentStationUniqueId와 비교 ⭐
                 marker.setImage(markerImage);
            } else {
                 marker.setImage(selectedMarkerImage);
            }

        } else {
            const position = new kakao.maps.LatLng(parseFloat(item.WGS84_LAT), parseFloat(item.WGS84_LOGT));
            marker = new kakao.maps.Marker({ position, title: item.name, image: markerImage });
            infowindow = new kakao.maps.InfoWindow({
                content: `<div style="padding:5px;font-size:12px;">${item.name || item.STTN_NM_INFO}</div>`,
                removable: true
            });
            markerMap.set(uniqueId, { marker, data: item, infowindow }); // ⭐ uniqueId로 저장 ⭐

            kakao.maps.event.addListener(marker, 'click', function () {
                selectItem(uniqueId); // ⭐ uniqueId 전달 ⭐
                currentMap.panTo(position);
            });
        }
        markersToAdd.push(marker);
    });

    clusterer.addMarkers(markersToAdd);
    updateStoreCards(visibleData);
    
    if (currentStationUniqueId) { // ⭐ currentStationUniqueId 사용 ⭐
        highlightCard(currentStationUniqueId);
    }
}

// ⭐ 정류장 카드 업데이트 (uniqueId 사용) ⭐
function updateStoreCards(data) {
    const cardListContainer = document.getElementById('card-list');
    cardListContainer.innerHTML = '';
    activeCardElement = null;

    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'store-card nes-container is-rounded';
        const uniqueId = item.uniqueId; // ⭐ uniqueId 사용 ⭐
        card.dataset.id = uniqueId; // ⭐ uniqueId 사용 ⭐
        
        card.innerHTML = `
            <h3>${item.STTN_NM_INFO || item.name}</h3>
            <p>${item.CNTR_CARTRK_DIV || ''}${item.JURISD_INST_NM || ''}</p>
            <p>ID: ${item.apiStationId || '정보 없음'}</p> <!-- ⭐ 사용자에게는 apiStationId 표시 ⭐ -->
        `;
        
        card.addEventListener('click', () => selectItem(uniqueId)); // ⭐ uniqueId 전달 ⭐
        cardListContainer.appendChild(card);
    });

    if (data.length === 0) {
        cardListContainer.innerHTML = `
            <div style="text-align: center; margin-top: 2rem;">
                <i class="nes-icon close is-large"></i>
                <p class="mt-3">정류장이 없습니다.</p>
            </div>
        `;
    }
}

// ⭐ 아이템(마커/카드) 선택 로직 공통 함수 (uniqueId 사용) ⭐
function selectItem(uniqueId) {
    if (!markerMap.has(uniqueId)) return;

    const { marker, data, infowindow } = markerMap.get(uniqueId);

    deselectAll();

    marker.setImage(selectedMarkerImage);
    infowindow.open(map, marker);
    highlightCard(uniqueId); // ⭐ uniqueId 전달 ⭐

    currentSelectedMarker = marker;
    currentInfoWindow = infowindow;
    currentStationUniqueId = uniqueId; // ⭐ uniqueId 저장 ⭐

    // ⭐ openDetailView에는 apiStationId와 name 전달 ⭐
    openDetailView(data.apiStationId, data.name || data.STTN_NM_INFO, uniqueId);
}

function moveToCoords(lat, lng, id) { // 이 함수는 현재 사용되지 않음
    const position = new kakao.maps.LatLng(parseFloat(lat), parseFloat(lng));
    if (map) {
        map.panTo(position);
        highlightCard(id);
    }
}

function highlightCard(uniqueId) { // ⭐ uniqueId 사용 ⭐
    const newActiveCard = document.querySelector(`.store-card[data-id="${uniqueId}"]`);
    if (newActiveCard) {
        newActiveCard.classList.add('active');
        activeCardElement = newActiveCard;
        if (!currentStationUniqueId) { // ⭐ currentStationUniqueId 사용 ⭐
             newActiveCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }
}

// -------------------------------------------------------------
// ⭐ 상세 화면 (버스 도착 정보) 관련 함수 ⭐
// -------------------------------------------------------------

// ⭐ openDetailView 함수 시그니처 변경 (uniqueId 추가) ⭐
async function openDetailView(apiStationId, stationName, uniqueId) {
    currentStationId = apiStationId; // API 호출용 ID
    currentStationUniqueId = uniqueId; // UI 상태 관리용 ID
    
    // ⭐ 마지막 상태 저장 (uniqueId도 함께 저장) ⭐
    localStorage.setItem('lastStationId', apiStationId);
    localStorage.setItem('lastStationName', stationName);
    localStorage.setItem('lastStationUniqueId', uniqueId);

    const detailView = document.getElementById('detail-view');
    const stationNameEl = document.getElementById('detail-station-name');
    const stationIdEl = document.getElementById('detail-station-id');
    const arrivalListEl = document.getElementById('arrival-list');

    stationNameEl.textContent = stationName;
    stationIdEl.textContent = apiStationId; // ⭐ 사용자에게는 apiStationId 표시 ⭐
    
    arrivalListEl.innerHTML = `
        <div style="text-align: center; margin-top: 2rem;">
            <i class="nes-octocat animate"></i>
            <p class="mt-3">로딩중...</p>
        </div>
    `;
    
    detailView.classList.add('show');

    await loadArrivalData(apiStationId);
}

async function refreshArrivalInfo() {
    if (!currentStationId) return;

    const btnRefresh = document.getElementById('btn-refresh');
    
    const originalText = btnRefresh.innerText;
    btnRefresh.innerText = '...';
    btnRefresh.classList.remove('is-warning');
    btnRefresh.classList.add('is-disabled');
    btnRefresh.disabled = true;

    await loadArrivalData(currentStationId);

    setTimeout(() => {
        btnRefresh.innerText = originalText;
        btnRefresh.classList.remove('is-disabled');
        btnRefresh.classList.add('is-warning');
        btnRefresh.disabled = false;
    }, 500);
}

async function loadArrivalData(stationId) { // 이 함수는 apiStationId를 받음
    const arrivalListEl = document.getElementById('arrival-list');
    try {
        const arrivalData = await getBusArrivalListv2({ stationId: stationId });
        renderArrivalList(arrivalData);
    } catch (error) {
        console.error("버스 도착 정보 로드 실패:", error);
        arrivalListEl.innerHTML = `
            <div style="text-align: center; margin-top: 2rem;">
                <p class="nes-text is-error">정보 로드 실패!</p>
            </div>
        `;
    }
}

function closeDetailView() {
    const detailView = document.getElementById('detail-view');
    detailView.classList.remove('show');
    currentStationId = null;
    currentStationUniqueId = null; // ⭐ uniqueId도 초기화 ⭐
    
    localStorage.removeItem('lastStationId');
    localStorage.removeItem('lastStationName');
    localStorage.removeItem('lastStationUniqueId'); // ⭐ uniqueId도 삭제 ⭐
}

function toggleFavorite(routeId) {
    const id = String(routeId);
    
    if (favoriteRoutes.includes(id)) {
        favoriteRoutes = favoriteRoutes.filter(r => r !== id);
    } else {
        favoriteRoutes.push(id);
    }
    
    localStorage.setItem('favoriteRoutes', JSON.stringify(favoriteRoutes));
    
    if (currentStationId) {
        loadArrivalData(currentStationId);
    }
}

function renderArrivalList(data) {
    const arrivalListEl = document.getElementById('arrival-list');
    arrivalListEl.innerHTML = '';

    const busTypeColors = {
        '11': '#ef4444', '12': '#3b82f6', '13': '#22c55e', '14': '#a855f7',
        '15': '#8b5cf6', '16': '#ef4444', '20': '#f59e0b', '21': '#ef4444',
        '22': '#3b82f6', '23': '#22c55e', '30': '#f59e0b', '41': '#3b82f6',
        '42': '#3b82f6', '43': '#3b82f6', '51': '#0ea5e9', '52': '#0ea5e9',
        '53': '#0ea5e9', 'default': '#64748b'
    };

    let list = [];
    if (Array.isArray(data)) {
        list = data;
    } else if (data && data.busArrivalList) {
        list = data.busArrivalList;
    } else if (data && Array.isArray(data.busArrivalList)) {
         list = data.busArrivalList;
    }

    if (list && !Array.isArray(list) && typeof list === 'object') {
        list = [list];
    }

    if (!list || list.length === 0) {
        arrivalListEl.innerHTML = `
            <div style="text-align: center; margin-top: 2rem;">
                <p>도착 버스 없음</p>
            </div>
        `;
        return;
    }

    list.sort((a, b) => {
        const isFavA = favoriteRoutes.includes(String(a.routeId));
        const isFavB = favoriteRoutes.includes(String(b.routeId));
        if (isFavA && !isFavB) return -1;
        if (!isFavA && isFavB) return 1;
        return 0;
    });

    list.forEach(bus => {
        const busNo = bus.routeName || '번호없음';
        const predictTime1 = bus.predictTime1 ? `${bus.predictTime1}분` : '정보없음';
        const locationNo1 = bus.locationNo1 ? `${bus.locationNo1}전` : '';
        const remainSeat = bus.remainSeatCnt1 ? `${bus.remainSeatCnt1}석` : '';
        const destName = bus.routeDestName ? `${bus.routeDestName} 방면` : '';
        const routeId = bus.routeId;
        
        const routeTypeCd = String(bus.routeTypeCd); 
        const borderColor = busTypeColors[routeTypeCd] || busTypeColors['default'];
        
        const isFavorite = favoriteRoutes.includes(String(routeId));
        const starIconClass = isFavorite ? 'nes-icon star is-small' : 'nes-icon star is-empty is-small';
        
        const item = document.createElement('div');
        item.className = 'arrival-card nes-container is-rounded';
        if (isFavorite) {
            item.style.backgroundColor = '#fffbeb';
        }
        
        item.innerHTML = `
            <div style="display: flex; align-items: center;">
                <button class="btn-favorite ${isFavorite ? 'active' : ''}" onclick="toggleFavorite('${routeId}')">
                    <i class="${starIconClass}"></i>
                </button>
                <div>
                    <div class="bus-badge" style="background-color: ${borderColor};">${busNo}</div>
                    <div class="bus-dest" style="font-size: 0.7rem;">${destName}</div>
                </div>
            </div>
            <div style="text-align: right;">
                <div class="arrival-time">${predictTime1}</div>
                <div style="font-size: 0.7rem;">${locationNo1} ${remainSeat}</div>
            </div>
        `;
        arrivalListEl.appendChild(item);
    });
}

window.closeDetailView = closeDetailView;
window.refreshArrivalInfo = refreshArrivalInfo;
window.toggleFavorite = toggleFavorite;

initMapAndData();
