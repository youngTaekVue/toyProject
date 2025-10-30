const apiUrl = 'http://localhost:3000/mapkey/getkey';
const mpaUrl = 'http://localhost:3000/mapkey/trade';



// 클라이언트 JavaScript (client.js)
async function loadMap() {
    try {
        // 1. 서버에서 API 키 요청
        const response = await fetch(mpaUrl);
        const config = await response.json();
console.log(config);
    } catch (error) {
        console.error('Failed to fetch config:', error);
    }
}




// 클라이언트 JavaScript (client.js)
async function loadKakaoMap() {
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
loadMap()
loadKakaoMap();