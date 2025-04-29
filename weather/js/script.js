let myData;
const weatherInfoDiv = document.getElementById('weather-info');
const apiKey = '';
let nx = 59;
let ny = 126;

// 현재 날짜와 시간
const now = new Date();
const year = now.getFullYear();
const month = String(now.getMonth() + 1).padStart(2, '0');
const day = String(now.getDate()).padStart(2, '0');
const hours = String(now.getHours()).padStart(2, '0');
const minutes = String(now.getMinutes()).padStart(2, '0');
let {baseDate, baseTime} = getBaseTime();
let apiName = "";

// 서버에서 rising.json 파일을 비동기적으로 가져와 파싱합니다.
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

// 기상청 초단기실황조회 API를 호출하여 날씨 정보를 가져옵니다.
// 날씨 정보 API 호출 함수
function getUltraSrtNcstData() {
    let apiName = "getUltraSrtNcst";
    getApiCall(apiName);
}

function getUltraSrtFcstData(apiUrl) {
    let apiName = "getVilageFcst";
    getReBaseTime();

    getApiCall(apiName);
}

function getApiCall(param) {
    const apiUrl = `https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/${param}?serviceKey=${apiKey}&numOfRows=1000&pageNo=1&dataType=JSON&base_date=${baseDate}&base_time=${baseTime}&nx=${nx}&ny=${ny}`;
    let allAverages;
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            if (data.response.header.resultCode === '00') {
                // 응답 성공 시 items 배열에서 날씨 정보를 추출하여 화면에 표시
                const items = data.response.body.items.item;
                if (param === "getUltraSrtNcst") {
                    getUltraSrtNcstWeatherData(items, param);
                } else if (param === "getVilageFcst") {
                    let weeklyForecastData = {};
                    items.forEach(item => {
                        const fcstDate = item.fcstDate;
                        const fcstTime = item.fcstTime;
                        if (!weeklyForecastData[fcstDate]) {
                            weeklyForecastData[fcstDate] = {};
                        }
                        if (!weeklyForecastData[fcstDate][fcstTime]) {
                            weeklyForecastData[fcstDate][fcstTime] = {};
                        }
                        weeklyForecastData[fcstDate][fcstTime][item.category] = item.fcstValue;
                    });
                    console.log(`${baseDate} ${baseTime} 예보 데이터 저장 완료`);
                    allAverages = calculateDailyAverages(weeklyForecastData);

                    //getUltraSrtNcstWeatherData(allAverages, param);
                    //getVilageFcstWeatherData(allAverages, param);
                }

            } else {
                // 응답 실패 시 에러 메시지 표시
                weatherInfoDiv.innerHTML = `<p>날씨 정보를 불러오는 데 실패했습니다: ${data.response.header.resultMsg}</p>`;
            }
        })
        .catch(error => {
            // 네트워크 오류 등 예외 발생 시 에러 메시지 표시
            weatherInfoDiv.innerHTML = `<p>오류가 발생했습니다: ${error}</p>`;
        });
}

// 초단기실황조회 API 응답 데이터에서 필요한 날씨 정보를 추출하여 화면에 표시합니다.
function getUltraSrtNcstWeatherData(data, param) {
    for (const item of data) {
        // 1시간 기온 (T1H)
        if (item.category === 'T1H') {
            $("#txtT1H").text(item.obsrValue + "°C"); // jQuery를 사용하여 텍스트 설정
        }
        // 강수 형태 (PTY)
        if (item.category === 'PTY') {
            const ptyCode = item.obsrValue;
            displayCurrentWeatherIcon(ptyCode, param);
        }
        // 습도 (REH)
        if (item.category === 'REH') {
            $("#txtREH").text(item.obsrValue + " %"); // jQuery를 사용하여 텍스트 설정
        }
        // 1시간 강수량 (RN1)
        if (item.category === 'RN1') {
            $("#txtRN1").text(item.obsrValue + " mm"); // jQuery를 사용하여 텍스트 설정
        }
        // 풍속 (WSD)
        if (item.category === 'WSD') {
            $("#txtWSD").text(item.obsrValue + " m/s"); // jQuery를 사용하여 텍스트 설정
        }
    }
}

// 강수 형태 코드에 따라 날씨 아이콘 URL을 반환합니다.
function displayCurrentWeatherIcon(ptyCode, param) {
    let iconUrl = '';

    switch (ptyCode) {
        case '0': // 강수 없음
            iconUrl = 'images/sunny.svg'; // 예시: 맑음 아이콘
            break;
        case '1': // 비
            iconUrl = 'images/rain.svg';
            break;
        case '2': // 비/눈
            iconUrl = 'images/sleet.svg';
            break;
        case '3': // 눈
            iconUrl = 'images/snow.svg';
            break;
        case '4': // 소나기
            iconUrl = 'images/shower.svg';
            break;
        case '5': // 빗방울
            iconUrl = 'images/drizzle.svg';
            break;
        case '6': // 진눈깨비
            iconUrl = 'images/light_sleet.svg';
            break;
        case '7': // 눈날림
            iconUrl = 'images/flurries.svg';
            break;
        default:
            iconUrl = 'images/unknown.png'; // 예외 처리
            break;
    }
    // 해당 ID의 이미지 요소의 src 속성을 변경하여 아이콘을 표시합니다.
    if (param === "getUltraSrtNcst") {
        document.getElementById("tempIcon").src = iconUrl;
    } else if (param === "getUltraSrtFcst") {
        console.log(iconUrl);
    }
}

// 현재 시간을 기준으로 API 호출에 사용할 base_date와 base_time을 생성합니다.
// base_time은 매 시각 30분 간격으로 설정됩니다.
function getBaseTime() {
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const currentDate = formatDate(now); // 날짜를 YYYYMMDD 형식으로 변환

    let baseHour = currentHour;
    let baseMinute = "30";
    let baseDate = currentDate;

    // 현재 분이 30분 미만이면 한 시간 전의 30분을 base_time으로 설정
    if (currentMinute < 30) {
        if (currentHour === 0) {
            // 자정 이전이면 날짜를 하루 전으로, 시간을 23시로 설정
            const yesterday = new Date(now);
            yesterday.setDate(now.getDate() - 1);
            baseDate = formatDate(yesterday);
            baseHour = 23;
        } else {
            baseHour -= 1;
        }
    }
    // 시간을 두 자리 문자열로 포맷 (예: 09, 23)
    const baseHourStr = baseHour.toString().padStart(2, '0');
    const baseTimeStr = baseHourStr + baseMinute;

    return {baseDate: baseDate, baseTime: baseTimeStr};
}

// Date 객체를 YYYYMMDD 형식의 문자열로 변환합니다.
function formatDate(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}${month}${day}`;
}

function getReBaseTime() {
    const now = new Date();
    const hours = now.getHours();
    baseTime;

    switch (true) {
        case hours < 2:
            baseTime = "2300";
            break;
        case hours < 5:
            baseTime = "0200";
            break;
        case hours < 8:
            baseTime = "0500";
            break;
        case hours < 11:
            baseTime = "0800";
            break;
        case hours < 14:
            baseTime = "1100";
            break;
        case hours < 17:
            baseTime = "1400";
            break;
        case hours < 20:
            baseTime = "1700";
            break;
        case hours < 23:
            baseTime = "2000";
            break;
        default:
            baseTime = "2300";
            break;
    }
    return baseTime;
}

function calculateDailyAverages(weeklyData) {
    const dailyAverages = {};
    for (const date in weeklyData) {
        const dailyTotals = {};
        const dailyCounts = {};

        for (const time in weeklyData[date]) {
            const forecast = weeklyData[date][time];

            for (const category in forecast) {
                const value = forecast[category];
                if (/^-?\d+(\.\d+)?$/.test(value)) {
                    if (!dailyTotals[category]) {
                        dailyTotals[category] = 0;
                        dailyCounts[category] = 0;
                    }
                    dailyTotals[category] += parseFloat(value);
                    dailyCounts[category]++;
                }
            }
        }
        dailyAverages[date] = {};
        for (const category in dailyTotals) {
            if (dailyCounts[category] > 0) {
                dailyAverages[date][category] = dailyTotals[category] / dailyCounts[category];
            } else {
                dailyAverages[date][category] = null;
            }
        }
    }
    return dailyAverages;
}


getUltraSrtNcstData()
getUltraSrtFcstData();