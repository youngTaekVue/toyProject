//let arrRising;

// fetch('/file/rising.json')
//     .then(response => {
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
//         return response.json();
//     })
//     .then(data => {
//         arrRising = data;
//         console.log(data); // JSON 데이터 사용
//     })
//     .catch(error => {
//         console.error('JSON 파일 로드 실패:', error);
//     });

let myData;

async function fetchDataAndProcess() {

    try {
        const response = await fetch('/file/rising.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        myData = await response.json();
        return myData;
    } catch (error) {
        console.error('데이터 로드 실패:', error);
    }
}

fetchDataAndProcess();

function getBaseTime() {
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const currentDate = formatDate(now); // 날짜 포맷 함수 (YYYYMMDD)

    let baseHour = currentHour;
    let baseMinute = "30";
    let baseDate = currentDate;

    if (currentMinute < 30) {
        if (currentHour === 0) {
            // 자정 이전 시간으로 설정, 날짜도 하루 전으로
            const yesterday = new Date(now);
            yesterday.setDate(now.getDate() - 1);
            baseDate = formatDate(yesterday);
            baseHour = 23;
        } else {
            baseHour -= 1;
        }
    }

    const baseHourStr = baseHour.toString().padStart(2, '0');
    const baseTimeStr = baseHourStr + baseMinute;

    return {baseDate: baseDate, baseTime: baseTimeStr};
}

function formatDate(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}${month}${day}`;
}


const weatherInfoDiv = document.getElementById('weather-info');
const apiKey = ''; // 여기에 발급받은 API 키를 입력하세요.
const nx = 60; // 예시: 서울 지역의 nx 좌표
const ny = 127; // 예시: 서울 지역의 ny 좌표

const now = new Date();
const year = now.getFullYear();
const month = String(now.getMonth() + 1).padStart(2, '0');
const day = String(now.getDate()).padStart(2, '0');
const hours = String(now.getHours()).padStart(2, '0');
const minutes = String(now.getMinutes()).padStart(2, '0');

// API 호출 시 base_time 설정 (매 시각 30분 간격)
const {baseDate, baseTime} = getBaseTime();
const apiUrl = `https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst?serviceKey=${apiKey}&numOfRows=10&pageNo=1&dataType=JSON&base_date=${baseDate}&base_time=${baseTime}&nx=${nx}&ny=${ny}`;


fetch(apiUrl)
    .then(response => response.json())
    .then(data => {
        if (data.response.header.resultCode === '00') {
            const items = data.response.body.items.item;
            displayUltraSrtFcst(items);
        } else {
            weatherInfoDiv.innerHTML = `<p>날씨 정보를 불러오는 데 실패했습니다: ${data.response.header.resultMsg}</p>`;
        }
    })
    .catch(error => {
        weatherInfoDiv.innerHTML = `<p>오류가 발생했습니다: ${error}</p>`;
    });

function displayUltraSrtFcst(items) {
    weatherInfoDiv.innerHTML = '';
    const relevantData = {};
    fetchDataAndProcess()
    if (myData) {
        console.log(items);
        items.forEach(item => {
            // const category = item.category;
            // const value = item.fcstValue;
            const category = item.category;
            const value = item.obsrValue;



            switch (category) {
                case 'T1H': // 기온
                    relevantData.T1H = value + '°C';

                    $("#saobtemperature").text(value + '°C');

                    break;
                case 'RN1': // 1시간 강수량
                    relevantData.RN1 = value + 'mm';
                    break;
                case 'SKY': // 하늘 상태 (0: 맑음, 1: 구름많음, 2: 흐림)
                    console.log(value);
                    let skyStatus = '';

                    const sType = myData
                        .filter(friend => friend.type === "SKY")
                        .filter(friend => friend.value === value);
                    console.log(sType);

                    if (value === '1') skyStatus = '맑음';
                    else if (value === '3') skyStatus = '구름많음';
                    else if (value === '4') skyStatus = '흐림';
                    relevantData.SKY = skyStatus;
                    break;
                case 'PTY': // 강수 형태 (0: 없음, 1: 비, 2: 비/눈, 3: 눈, 4: 소나기)
                    let precipitationType = '';
                    // const pType = myData.filter((friend) => {
                    //     return friend.type === "PTY";
                    // })
                    //
                    // const pType1 = pType.filter((friend) => {
                    //     return friend.value === value;
                    // })
                    const pType = myData
                        .filter(friend => friend.type === "PTY")
                        .filter(friend => friend.value === value);

                    console.log(pType);
                    // pType.forEach(item =>{
                    //    // console.log(item);
                    //     if(item.value === value){
                    //         console.log(item.content);
                    //      //   console.log(item.content);
                    //     }
                    // })

                    if (value === '0') precipitationType = '없음';
                    else if (value === '1') precipitationType = '비';
                    else if (value === '2') precipitationType = '비/눈';
                    else if (value === '3') precipitationType = '눈';
                    else if (value === '4') precipitationType = '소나기';
                    relevantData.PTY = precipitationType;

                    // if (ptyCode === '1') { // 비
                    //     iconPath = 'images/rain.png';
                    // } else if (ptyCode === '2') { // 비/눈
                    //     iconPath = 'images/rain_snow.png';
                    // } else if (ptyCode === '3') { // 눈
                    //     iconPath = 'images/snow.png';
                    // } else if (ptyCode === '4') { // 소나기
                    //     iconPath = 'images/shower.png';
                    // } else { // 강수 없음
                    //     if (skyCode === '1') { // 맑음
                    //         const currentHour = new Date().getHours();
                    //         iconPath = (currentHour >= 6 && currentHour < 18) ? 'images/sun.png' : 'images/moon.png';
                    //     } else if (skyCode === '2') { // 구름 조금
                    //         const currentHour = new Date().getHours();
                    //         iconPath = (currentHour >= 6 && currentHour < 18) ? 'images/partly_cloudy_day.png' : 'images/partly_cloudy_night.png';
                    //     } else if (skyCode === '3') { // 구름 많음
                    //         iconPath = 'images/cloudy.png';
                    //     } else if (skyCode === '4') { // 흐림
                    //         iconPath = 'images/overcast.png';
                    //     }
                    // }

                    break;
                case 'VEC': // 풍향 (0~359)
                    relevantData.VEC = value + '°';
                    break;
                case 'WSD': // 풍속 (m/s)
                    relevantData.WSD = value + 'm/s';
                    break;
                // 필요한 다른 정보도 추가할 수 있습니다.
            }
        });
    }
    if (relevantData.T1H) weatherInfoDiv.innerHTML += `<p>기온: ${relevantData.T1H}</p>`;
    if (relevantData.RN1) weatherInfoDiv.innerHTML += `<p>1시간 강수량: ${relevantData.RN1}</p>`;
    if (relevantData.SKY) weatherInfoDiv.innerHTML += `<p>하늘 상태: ${relevantData.SKY}</p>`;
    if (relevantData.PTY) weatherInfoDiv.innerHTML += `<p>강수 형태: ${relevantData.PTY}</p>`;
    if (relevantData.VEC) weatherInfoDiv.innerHTML += `<p>풍향: ${relevantData.VEC}</p>`;
    if (relevantData.WSD) weatherInfoDiv.innerHTML += `<p>풍속: ${relevantData.WSD}</p>`;

    if (Object.keys(relevantData).length === 0) {
        weatherInfoDiv.innerHTML = '<p>표시할 날씨 정보가 없습니다.</p>';
    }
}


