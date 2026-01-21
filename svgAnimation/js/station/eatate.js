// --- 전역 변수 설정 ---
let map = null;
const markerMap = new Map();
let activeCardElement = null;
let allStoreData = [];
let clusterer = null;
let currentSelectedMarker = null; // 현재 선택된 마커 추적
let currentInfoWindow = null; // 현재 열린 인포윈도우 추적
let currentStationId = null; // 현재 상세 화면에 표시 중인 정류장 ID

// 마커 이미지 변수 (초기화는 SDK 로드 후 수행)
let markerImage = null;
let selectedMarkerImage = null;

// -------------------------------------------------------------
// ⭐ 통합 함수: 지도 로드, 데이터 로드, 마커 표시, 카드 생성 순차 처리
// -------------------------------------------------------------
async function initMapAndData() {
    const mapConfig = await fetchKakaMapConfig();
    if (!mapConfig) return;

    allStoreData = [];
    document.getElementById('loading-message').style.display = 'none';
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
                // ⭐ SDK 로드 후 이미지 객체 생성 ⭐
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

                // ⭐ 지도 이동/줌 이벤트 리스너 (수정됨) ⭐
                const updateDelayed = debounce(async () => {
                    // 마커가 선택되어 있어도 데이터 로드는 계속 진행합니다.
                    await loadAndDisplayStationsAroundCenter();
                }, 500);

                kakao.maps.event.addListener(map, 'dragend', updateDelayed);
                kakao.maps.event.addListener(map, 'zoom_changed', updateDelayed);

                // ⭐ 지도 클릭 이벤트: 모든 선택 해제 ⭐
                kakao.maps.event.addListener(map, 'click', function() {
                    deselectAll();
                });

                // Geolocation 처리
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

                resolve();
            });
        };
        document.head.appendChild(script);
    });
}

// ⭐ 모든 선택 상태를 해제하는 함수 ⭐
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
    // 상세 화면 닫기
    closeDetailView();
}

// ⭐ 중심 좌표 기준 데이터 로드 및 마커 업데이트 공통 함수 ⭐
async function loadAndDisplayStationsAroundCenter() {
    if (!map) return;
    const center = map.getCenter();
    const lat = center.getLat();
    const lng = center.getLng();

    try {
        const aroundStations = await getBusStationAroundListv2(lat, lng);
        if (aroundStations && Array.isArray(aroundStations) && aroundStations.length > 0) {
            const mappedAroundData = aroundStations.map(item => ({
                ...item,
                WGS84_LAT: item.y, WGS84_LOGT: item.x,
                name: item.stationName, STTN_ID: item.stationId,
                STTN_NM_INFO: item.stationName
            }));
            
            const existingIds = new Set(allStoreData.map(d => d.STTN_ID || d.id));
            const newItems = mappedAroundData.filter(d => !existingIds.has(d.STTN_ID));
            
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

// --- G. 마커와 카드 목록 업데이트 (수정됨) ---
function updateMarkersAndCards(currentMap) {
    clusterer.clear();
    const visibleData = filterDataInBounds(currentMap);
    
    const markersToAdd = [];
    visibleData.forEach(item => {
        const id = item.STTN_ID || item.id;
        let marker, infowindow;
        
        if (markerMap.has(id)) {
            const storedItem = markerMap.get(id);
            marker = storedItem.marker;
            infowindow = storedItem.infowindow;
            
            if (currentStationId !== id) {
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
            markerMap.set(id, { marker, data: item, infowindow });

            kakao.maps.event.addListener(marker, 'click', function () {
                selectItem(id);
                currentMap.panTo(position);
            });
        }
        markersToAdd.push(marker);
    });

    clusterer.addMarkers(markersToAdd);
    updateStoreCards(visibleData);
    
    if (currentStationId) {
        highlightCard(currentStationId);
    }
}

// --- H. 카드 목록 업데이트 (디자인 수정됨) ---
function updateStoreCards(data) {
    const cardListContainer = document.getElementById('card-list');
    cardListContainer.innerHTML = '';
    activeCardElement = null;

    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'store-card';
        const id = item.STTN_ID || item.id;
        card.dataset.id = id;
        
        // ⭐ 디자인 개선된 카드 HTML ⭐
        card.innerHTML = `
            <h3>${item.STTN_NM_INFO || item.name}</h3>
            <p><i class="bi bi-geo-alt"></i> ${item.CNTR_CARTRK_DIV || ''}${item.JURISD_INST_NM || ''}</p>
            <p><i class="bi bi-hash"></i> ${id || '정보 없음'}</p>
        `;
        
        card.addEventListener('click', () => selectItem(id));
        cardListContainer.appendChild(card);
    });

    if (data.length === 0) {
        cardListContainer.innerHTML = `
            <div class="text-center text-muted mt-5">
                <i class="bi bi-map fs-1 text-secondary opacity-50"></i>
                <p class="mt-3">지도 영역에 정류장이 없습니다.<br>지도를 이동해보세요.</p>
            </div>
        `;
    }
}

// ⭐ 아이템(마커/카드) 선택 로직 공통 함수 ⭐
function selectItem(id) {
    if (!markerMap.has(id)) return;

    const { marker, data, infowindow } = markerMap.get(id);

    deselectAll();

    marker.setImage(selectedMarkerImage);
    infowindow.open(map, marker);
    highlightCard(id);

    currentSelectedMarker = marker;
    currentInfoWindow = infowindow;

    openDetailView(id, data.name || data.STTN_NM_INFO);
}

function moveToCoords(lat, lng, id) {
    const position = new kakao.maps.LatLng(parseFloat(lat), parseFloat(lng));
    if (map) {
        map.panTo(position);
        highlightCard(id);
    }
}

function highlightCard(id) {
    const newActiveCard = document.querySelector(`.store-card[data-id="${id}"]`);
    if (newActiveCard) {
        newActiveCard.classList.add('active');
        activeCardElement = newActiveCard;
        if (!currentStationId) {
             newActiveCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }
}

// -------------------------------------------------------------
// ⭐ 상세 화면 (버스 도착 정보) 관련 함수 ⭐
// -------------------------------------------------------------

async function openDetailView(stationId, stationName) {
    currentStationId = stationId;

    const detailView = document.getElementById('detail-view');
    const stationNameEl = document.getElementById('detail-station-name');
    const stationIdEl = document.getElementById('detail-station-id');
    const arrivalListEl = document.getElementById('arrival-list');

    stationNameEl.textContent = stationName;
    stationIdEl.textContent = stationId;
    
    // ⭐ 로딩 UI 개선 ⭐
    arrivalListEl.innerHTML = `
        <div class="text-center mt-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-muted small">실시간 도착 정보를 불러오고 있습니다...</p>
        </div>
    `;
    
    detailView.classList.add('show');

    await loadArrivalData(stationId);
}

async function refreshArrivalInfo() {
    if (!currentStationId) return;

    const btnRefresh = document.getElementById('btn-refresh');
    const icon = btnRefresh.querySelector('i');
    
    icon.classList.add('spin-animation');
    btnRefresh.disabled = true;

    await loadArrivalData(currentStationId);

    setTimeout(() => {
        icon.classList.remove('spin-animation');
        btnRefresh.disabled = false;
    }, 500);
}

async function loadArrivalData(stationId) {
    const arrivalListEl = document.getElementById('arrival-list');
    try {
        const arrivalData = await getBusArrivalListv2({ stationId: stationId });
        renderArrivalList(arrivalData);
    } catch (error) {
        console.error("버스 도착 정보 로드 실패:", error);
        arrivalListEl.innerHTML = `
            <div class="text-center mt-5">
                <i class="bi bi-exclamation-circle fs-1 text-danger opacity-50"></i>
                <p class="mt-3 text-danger">정보를 불러오지 못했습니다.<br>잠시 후 다시 시도해주세요.</p>
            </div>
        `;
    }
}

function closeDetailView() {
    const detailView = document.getElementById('detail-view');
    detailView.classList.remove('show');
    currentStationId = null;
}

// ⭐ 도착 정보 렌더링 (색상 매핑 수정됨) ⭐
function renderArrivalList(data) {
    const arrivalListEl = document.getElementById('arrival-list');
    arrivalListEl.innerHTML = '';

    // ⭐ 버스 타입별 색상 정의 (GBIS 코드 기준) ⭐
    const busTypeColors = {
        '11': '#ef4444', // 직행좌석 (빨강)
        '12': '#3b82f6', // 좌석 (파랑)
        '13': '#22c55e', // 일반 (초록)
        '14': '#a855f7', // 광역급행 (보라)
        '15': '#8b5cf6', // 따복 (보라 계열)
        '16': '#ef4444', // 경기순환 (빨강)
        '20': '#f59e0b', // 마을 (노랑/주황) - 일부 지역 코드
        '21': '#ef4444', // 서울 직행 (빨강)
        '22': '#3b82f6', // 서울 좌석 (파랑)
        '23': '#22c55e', // 서울 일반 (초록)
        '30': '#f59e0b', // 마을 (노랑/주황)
        '41': '#3b82f6', // 시외 (파랑)
        '42': '#3b82f6', // 시외 (파랑)
        '43': '#3b82f6', // 시외 (파랑)
        '51': '#0ea5e9', // 공항 (하늘색)
        '52': '#0ea5e9', // 공항 (하늘색)
        '53': '#0ea5e9', // 공항 (하늘색)
        'default': '#64748b' // 기본값 (회색)
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
            <div class="text-center text-muted mt-5">
                <i class="bi bi-clock-history fs-1 opacity-50"></i>
                <p class="mt-3">도착 예정인 버스가 없습니다.</p>
            </div>
        `;
        return;
    }

    list.forEach(bus => {
        const busNo = bus.routeName || '번호없음';
        const predictTime1 = bus.predictTime1 ? `${bus.predictTime1}분` : '정보없음';
        const locationNo1 = bus.locationNo1 ? `${bus.locationNo1}전` : '';
        const remainSeat = bus.remainSeatCnt1 ? `${bus.remainSeatCnt1}석` : '';
        const destName = bus.routeDestName ? `${bus.routeDestName} 방면` : '';
        
        // ⭐ routeTypeCd를 사용하여 동적으로 border-left-color 설정 ⭐
        const routeTypeCd = String(bus.routeTypeCd); 
        const borderColor = busTypeColors[routeTypeCd] || busTypeColors['default'];
        
        const item = document.createElement('div');
        item.className = 'arrival-card';
        item.style.borderLeftColor = borderColor; // 동적 색상 적용
        
        item.innerHTML = `
            <div>
                <div class="bus-number" style="color: ${borderColor}">${busNo}</div>
                <div class="bus-dest">${destName}</div>
            </div>
            <div class="arrival-time-box">
                <div class="arrival-time">${predictTime1}</div>
                <div class="arrival-status">${locationNo1} ${remainSeat}</div>
            </div>
        `;
        arrivalListEl.appendChild(item);
    });
}

window.closeDetailView = closeDetailView;
window.refreshArrivalInfo = refreshArrivalInfo;

initMapAndData();
