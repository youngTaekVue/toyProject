// --- 전역 변수 설정 ---
let map = null;
const markerMap = new Map();
let activeCardElement = null;
let allStoreData = [];
let clusterer = null;
let currentSelectedMarker = null;
let currentInfoWindow = null;
let currentStationId = null;
let currentStationUniqueId = null;

let markerImage = null;
let selectedMarkerImage = null;

let favoriteRoutes = JSON.parse(localStorage.getItem('favoriteRoutes')) || [];

// -------------------------------------------------------------
// ⭐ 통합 함수
// -------------------------------------------------------------
async function initMapAndData() {
    console.log("1. initMapAndData 시작");
    const mapConfig = await fetchKakaoMapConfig();
    console.log("2. mapConfig 수신:", mapConfig);
    
    if (!mapConfig) {
        console.error("❌ mapConfig를 불러오지 못했습니다.");
        return;
    }

    allStoreData = [];
    document.getElementById('loading-message').style.display = 'none';
    
    console.log("3. loadKakaoMapSDK 호출");
    await loadKakaoMapSDK(mapConfig);
    console.log("10. initMapAndData 완료");
}

// --- C. 카카오맵 SDK 로드 (로깅 및 에러 처리 강화) ---
async function loadKakaoMapSDK(mapConfig) {
    // ⭐ 서버 응답 구조에 따라 키 추출 (필요시 .key 등으로 수정) ⭐
    const apiKey = mapConfig.kakaoMapAppKey || mapConfig.key || mapConfig.apiKey;
    
    console.log("4. 추출된 API Key:", apiKey);

    if (!apiKey) {
        console.error("❌ 카카오맵 API Key가 config 객체에 없습니다. 필드명을 확인하세요.");
        return;
    }

    return new Promise((resolve, reject) => {
        console.log("5. Promise 진입 및 스크립트 생성");
        const script = document.createElement('script');
        script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false&libraries=clusterer`;
        
        script.onload = () => {
            console.log("6. Kakao SDK 스크립트 로드 완료 (onload)");
            if (typeof kakao === 'undefined' || !kakao.maps) {
                console.error("❌ kakao.maps 객체가 정의되지 않았습니다.");
                reject(new Error("Kakao maps undefined"));
                return;
            }

            kakao.maps.load(() => {
                console.log("7. kakao.maps.load() 콜백 실행");
                
                // 마커 이미지 생성
                markerImage = new kakao.maps.MarkerImage('/images/markers.png', new kakao.maps.Size(15, 25));
                selectedMarkerImage = new kakao.maps.MarkerImage('/images/marker_selected.png', new kakao.maps.Size(15, 25));

                const container = document.getElementById('map');
                if (!container) {
                    console.error("❌ ID가 'map'인 엘리먼트를 찾을 수 없습니다.");
                    reject(new Error("Map container not found"));
                    return;
                }

                const defaultCenterLat = 37.269885;
                const defaultCenterLng = 126.956596;
                const defaultLevel = 2;

                const options = {
                    center: new kakao.maps.LatLng(defaultCenterLat, defaultCenterLng),
                    level: defaultLevel
                };

                map = new kakao.maps.Map(container, options);
                map.setMaxLevel(7);
                
                // NES.css 레이아웃 대응을 위한 relayout
                setTimeout(() => {
                    map.relayout();
                    map.setCenter(new kakao.maps.LatLng(defaultCenterLat, defaultCenterLng));
                    console.log("8. 지도 relayout 완료");
                }, 100);

                console.log('✅ 카카오맵 초기화 완료!');

                clusterer = new kakao.maps.MarkerClusterer({
                    map: map,
                    averageCenter: true,
                    minLevel: 6,
                });

                // 이벤트 리스너 등록
                const updateDelayed = debounce(async () => {
                    await loadAndDisplayStationsAroundCenter();
                }, 500);

                kakao.maps.event.addListener(map, 'dragend', updateDelayed);
                kakao.maps.event.addListener(map, 'zoom_changed', updateDelayed);
                kakao.maps.event.addListener(map, 'click', deselectAll);

                // 현재 위치 가져오기
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
                    loadAndDisplayStationsAroundCenter();
                }

                // 상태 복원
                const lastStationId = localStorage.getItem('lastStationId');
                const lastStationName = localStorage.getItem('lastStationName');
                const lastStationUniqueId = localStorage.getItem('lastStationUniqueId');
                if (lastStationId && lastStationName && lastStationUniqueId) {
                    setTimeout(() => {
                        openDetailView(lastStationId, lastStationName, lastStationUniqueId);
                    }, 300);
                }

                console.log("9. resolve() 호출");
                resolve();
            });
        };

        script.onerror = (err) => {
            console.error("❌ Kakao SDK 스크립트 로드 실패! 키가 올바른지, 도메인이 허용되어 있는지 확인하세요.", err);
            reject(err);
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

async function loadAndDisplayStationsAroundCenter() {
    if (!map) return;
    const center = map.getCenter();
    const lat = center.getLat();
    const lng = center.getLng();

    try {
        const [gyeonggiData, seoulData] = await Promise.all([
            getBusStationAroundListv2(lat, lng),
            getStationByPos(lat, lng)
        ]);

        let mergedData = [];

        if (gyeonggiData && Array.isArray(gyeonggiData)) {
            const mappedGyeonggi = gyeonggiData.map(item => ({
                ...item,
                uniqueId: 'GG_' + item.stationId,
                apiStationId: item.stationId,
                WGS84_LAT: item.y, 
                WGS84_LOGT: item.x,
                name: item.stationName, 
                STTN_NM_INFO: item.stationName,
                source: 'gyeonggi'
            }));
            mergedData = [...mappedGyeonggi];
        }

        if (seoulData && Array.isArray(seoulData)) {
            const mappedSeoul = seoulData.map(item => ({
                ...item,
                uniqueId: 'SL_' + (item.arsId || item.stationId),
                apiStationId: item.arsId || item.stationId,
                WGS84_LAT: item.gpsY, 
                WGS84_LOGT: item.gpsX,
                name: item.stationNm, 
                STTN_NM_INFO: item.stationNm,
                source: 'seoul'
            }));
            mergedData = [...mergedData, ...mappedSeoul];
        }

        if (mergedData.length > 0) {
            const existingUniqueIds = new Set(allStoreData.map(d => d.uniqueId));
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

function updateMarkersAndCards(currentMap) {
    clusterer.clear();
    const visibleData = filterDataInBounds(currentMap);
    
    const markersToAdd = [];
    visibleData.forEach(item => {
        const uniqueId = item.uniqueId;
        let marker, infowindow;
        
        if (markerMap.has(uniqueId)) {
            const storedItem = markerMap.get(uniqueId);
            marker = storedItem.marker;
            infowindow = storedItem.infowindow;
            
            if (currentStationUniqueId !== uniqueId) {
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
            markerMap.set(uniqueId, { marker, data: item, infowindow });

            kakao.maps.event.addListener(marker, 'click', function () {
                selectItem(uniqueId);
                currentMap.panTo(position);
            });
        }
        markersToAdd.push(marker);
    });

    clusterer.addMarkers(markersToAdd);
    updateStoreCards(visibleData);
    
    if (currentStationUniqueId) {
        highlightCard(currentStationUniqueId);
    }
}

function updateStoreCards(data) {
    const cardListContainer = document.getElementById('card-list');
    cardListContainer.innerHTML = '';
    activeCardElement = null;

    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'store-card nes-container is-rounded';
        const uniqueId = item.uniqueId;
        card.dataset.id = uniqueId;
        
        card.innerHTML = `
            <h3>${item.STTN_NM_INFO || item.name}</h3>
            <p>출처: ${item.source === 'gyeonggi' ? '경기도' : '서울시'}</p>
            <p>ID: ${item.apiStationId || '정보 없음'}</p>
        `;
        
        card.addEventListener('click', () => selectItem(uniqueId));
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

function selectItem(uniqueId) {
    if (!markerMap.has(uniqueId)) return;

    const { marker, data, infowindow } = markerMap.get(uniqueId);

    deselectAll();

    marker.setImage(selectedMarkerImage);
    infowindow.open(map, marker);
    highlightCard(uniqueId);

    currentSelectedMarker = marker;
    currentInfoWindow = infowindow;
    currentStationUniqueId = uniqueId;

    openDetailView(data.apiStationId, data.name || data.STTN_NM_INFO, uniqueId);
}

function highlightCard(uniqueId) {
    const newActiveCard = document.querySelector(`.store-card[data-id="${uniqueId}"]`);
    if (newActiveCard) {
        newActiveCard.classList.add('active');
        activeCardElement = newActiveCard;
        if (!currentStationUniqueId) {
             newActiveCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }
}

async function openDetailView(apiStationId, stationName, uniqueId) {
    currentStationId = apiStationId;
    currentStationUniqueId = uniqueId;
    
    localStorage.setItem('lastStationId', apiStationId);
    localStorage.setItem('lastStationName', stationName);
    localStorage.setItem('lastStationUniqueId', uniqueId);

    const detailView = document.getElementById('detail-view');
    const stationNameEl = document.getElementById('detail-station-name');
    const stationIdEl = document.getElementById('detail-station-id');
    const arrivalListEl = document.getElementById('arrival-list');

    stationNameEl.textContent = stationName;
    stationIdEl.textContent = apiStationId;
    
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
    btnRefresh.classList.add('is-disabled');
    btnRefresh.disabled = true;

    await loadArrivalData(currentStationId);

    setTimeout(() => {
        btnRefresh.innerText = originalText;
        btnRefresh.classList.remove('is-disabled');
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
        arrivalListEl.innerHTML = `<p class="nes-text is-error">정보 로드 실패!</p>`;
    }
}

function closeDetailView() {
    const detailView = document.getElementById('detail-view');
    detailView.classList.remove('show');
    currentStationId = null;
    currentStationUniqueId = null;
    localStorage.removeItem('lastStationId');
    localStorage.removeItem('lastStationName');
    localStorage.removeItem('lastStationUniqueId');
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
    }

    if (list && !Array.isArray(list) && typeof list === 'object') {
        list = [list];
    }

    if (!list || list.length === 0) {
        arrivalListEl.innerHTML = `<p>도착 버스 없음</p>`;
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
