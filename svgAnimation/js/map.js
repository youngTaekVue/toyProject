// 클라이언트 JavaScript (client.js)
async function loadTradeData() { // 함수명 변경 (더 명확하게)

    const tradeUrl = 'http://localhost:3000/mapkey/trade'; // tradeUrl로 변수명 변경

    try {
        // 1. 서버 API 호출 (서버가 키를 사용해 외부 데이터를 가져온 후 반환할 것을 기대)
        const response = await fetch(tradeUrl);

        if (!response.ok) {
            // 서버에서 4xx 또는 5xx 응답이 왔을 경우 처리
            const errorText = await response.text();
            throw new Error(`서버 요청 실패: ${response.status} ${response.statusText} - ${errorText}`);
        }
        // 2. 서버가 반환한 최종 데이터(실거래가 정보)를 JSON으로 파싱
        const tradeData = await response.json();

        console.log('성공적으로 수신된 실거래가 데이터:', tradeData);

        // 3. 맵에 데이터 표시 등의 후속 작업 수행...
        // displayDataOnMap(tradeData);

    } catch (error) {
        console.error('실거래가 데이터를 가져오는 데 실패했습니다:', error);
    }
}


// 클라이언트 JavaScript (client.js)
async function loadKakaoMap() {
    const apiUrl = 'http://localhost:3000/mapkey/getkey';
    try {
        // 1. 서버에서 API 키 요청
        const response = await fetch(apiUrl);

        // HTTP 상태 코드가 200번대가 아니면 에러를 던져 catch 블록으로 이동
        if (!response.ok) {
            console.error(`HTTP Error: ${response.status} - ${response.statusText}`);
            // 서버에서 에러 메시지를 JSON 형태로 보낼 경우, 응답 본문을 읽어볼 수 있습니다.
            const errorBody = await response.text();
            throw new Error(`Failed to fetch config. Server response: ${errorBody}`);
        }

        const config = await response.json();
        const apiKey = config.kakaoMapAppKey;
        if (!apiKey) {
            console.error("API Key is missing.");
            return;
        }

        // 2. 카카오맵 SDK 동적 로드
        const script = document.createElement('script');
        script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false`;


        // 키 값을 URL 쿼리 파라미터로 전달
        // script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&autoload=false`;
        script.onload = () => {
            // 3. 맵 초기화 및 표시
            kakao.maps.load(() => {
                const container = document.getElementById('map');
                const options = {
                    center: new kakao.maps.LatLng(33.450701, 126.570667),
                    level: 3
                };
                const map = new kakao.maps.Map(container, options);
                console.log('카카오맵 로드 완료!');
            });
        };
        document.head.appendChild(script);

    } catch (error) {
        console.error('Failed to fetch config:', error);
    }
}

loadTradeData()
loadKakaoMap();