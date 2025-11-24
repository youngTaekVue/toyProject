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


// --- A. 서버에서 API 키 설정 가져오기 (이전 코드와 동일) ---
async function fetchMapConfig() {
    const apiUrl = 'http://localhost:3000/mapkey/getKakaoKey';

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


// --- B. 서버의 JSON 파일 데이터를 가져오기 (이전 코드와 동일) ---
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
        script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false&libraries=clusterer`;

        script.onload = () => {
            kakao.maps.load(() => {
                const container = document.getElementById('map');

                const firstData = allStoreData.find(item => item.lat && item.lng && item.status === 'SUCCESS');
                const centerLat = 37.566826;
                const centerLng = 126.9786567;

                const options = {
                    center: new kakao.maps.LatLng(centerLat, centerLng),
                    level: 2
                };

                map = new kakao.maps.Map(container, options);
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

// --- E. 디바운스 함수 (이전 코드와 동일) ---
function debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}


// --- F. 지도 영역 내 데이터 필터링 (이전 코드와 동일) ---
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
            content: `<div style="padding:5px;font-size:12px;">${item.name}<br>(${item.road_address})</div>`
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

// --- H. 카드 목록 업데이트 함수 (이전 코드와 동일) ---
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
        //card.dataset.id = item.id;

        card.innerHTML = `
            <h3>${item.name}</h3>
            <p>📍 ${item.address}</p>
            <p>도로명: ${item.road_address || '정보 없음'}</p>
        `;

        card.addEventListener('click', () => {
            moveToMarker(item.id);
            highlightCard(item.id);
        });

        cardListContainer.appendChild(card);
    });

    console.log(`✅ 카드 목록을 ${data.length}개로 업데이트했습니다.`);
}

// --- I. 마커/카드 상호작용 함수 (이전 코드와 동일) ---
function highlightCard(id) {
    if (activeCardElement) {
        activeCardElement.classList.remove('active');
    }

    console.log(highlightCard)

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

function moveToMarker(id) {
    const markerInfo = markerMap.get(id);

    if (map && markerInfo) {
        const position = markerInfo.marker.getPosition();

        map.panTo(position);

        kakao.maps.event.trigger(markerInfo.marker, 'click');
    }
}

/**
 * 🌐 주소를 서버의 /geocode 엔드포인트로 전송하고,
 * 받은 좌표를 이용해 지도에 마커를 표시하고 지도를 이동시킵니다.
 */
// async function geocodeAndDisplayMarker() {
//     // 💡 입력 필드가 'addressInput'이라는 ID를 가진다고 가정합니다.
//     const addressInput = document.getElementById('addressInput');
//     const address = addressInput ? addressInput.value : null;
//
//     if (!address) {
//         alert("주소를 입력해 주세요.");
//         return;
//     }
//     if (!currentMap) {
//         alert("지도가 아직 로드되지 않았습니다.");
//         return;
//     }
//
//     const geocodeApiUrl = 'http://localhost:3000/api/locations'; // 서버의 주소 변환 엔드포인트
//
//     try {
//         // 1. 서버의 /geocode POST 엔드포인트 호출
//         const response = await fetch(geocodeApiUrl, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             // 🚨 주소를 JSON Body에 담아 전송
//             body: JSON.stringify({ address: address })
//         });
//
//         if (!response.ok) {
//             const errorData = await response.json();
//             alert(`주소 변환 실패: ${errorData.error || response.statusText}`);
//             console.error('Geocoding Error:', errorData);
//             return;
//         }
//
//         // 2. 서버에서 받은 좌표 데이터 파싱
//         const coordinates = await response.json();
//         const lat = coordinates.lat; // 위도
//         const lng = coordinates.lng; // 경도
//         const moveLatLon = new kakao.maps.LatLng(lat, lng);
//
//         // 3. 마커 표시 및 지도 이동
//
//         // 기존 마커가 있다면 제거
//         if (currentMarker) {
//             currentMarker.setMap(null);
//         }
//
//         // 새 마커 생성
//         currentMarker = new kakao.maps.Marker({
//             map: currentMap,
//             position: moveLatLon,
//             title: coordinates.address_name || address // 주소명으로 마커 타이틀 설정
//         });
//
//         // 지도의 중심을 결과 좌표로 이동
//         currentMap.panTo(moveLatLon);
//
//         console.log(`마커 표시 완료! [${coordinates.address_name}]`);
//
//     } catch (error) {
//         console.error('주소 변환 및 마커 표시 중 오류 발생:', error);
//         alert('주소를 좌표로 변환하는 데 실패했습니다. 서버 로그를 확인하세요.');
//     }
// }

// ⭐ 애플리케이션 시작 ⭐
initMapAndData();
