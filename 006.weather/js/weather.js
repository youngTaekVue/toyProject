let myData;
const weatherInfoDiv = document.getElementById('weather-info');
let item_Container = document.getElementById("item_Container");

// 초기값 (서울 기준 위경도)
let defaultLocation = [37.5666, 126.9784];

// 서버에서 rising.json 파일을 비동기적으로 가져와 파싱합니다.
async function fetchDataAndProcess() {
    try {
        const response = await fetch('/file/rising.json');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        myData = await response.json();
        return myData;
    } catch (error) {
        console.error('데이터 로드 실패:', error);
    }
}

// 1. 초단기실황 (현재 날씨)
function getUltraSrtNcstData(location) {
    let apiName = "getUltraSrtNcst";
    const { baseDate, baseTime } = getBaseTimeForNcst();
    getApiCall(apiName, location, baseDate, baseTime);
}

// 2. 단기예보 (주간/일간 예보)
function getUltraSrtFcstData(location) {
    let apiName = "getVilageFcst";
    const { baseDate, baseTime } = getBaseTimeForFcst();
    getApiCall(apiName, location, baseDate, baseTime);
}

// 공통 API 호출 함수
async function getApiCall(name, lodata, baseDate, baseTime) {
    console.log(`[API Request] ${name} | lat: ${lodata[0]}, lon: ${lodata[1]} | date: ${baseDate}, time: ${baseTime}`);
    const apiUrl = 'http://localhost:3000/weather/dataList';

    const dataToSend = {
        name: name,
        numOfRows: '1052',
        pageNo: '1',
        dataType: 'JSON',
        baseDate: baseDate,
        baseTime: baseTime,
        lat: lodata[0], // 위경도 그대로 전송 (서버에서 변환)
        lon: lodata[1]
    };

    try {
        let response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dataToSend)
        });

        if (!response.ok) throw new Error(`API 요청 실패: ${response.status}`);

        const data = await response.json();
        if (data.response && data.response.header.resultCode === '00') {
            const items = data.response.body.items.item;
            if (name === "getUltraSrtNcst") {
                getUltraSrtNcstWeatherData(items);
            } else if (name === "getVilageFcst") {
                getVilageFcstWeatherData(items);
            }
        } else {
            const msg = data.response ? data.response.header.resultMsg : "Unknown Error";
            console.error("API Error:", msg);
        }
    } catch (error) {
        console.error('API 호출 중 오류:', error);
    }
}

// --- 데이터 처리 및 화면 렌더링 ---

function getUltraSrtNcstWeatherData(data) {
    for (const item of data) {
        if (item.category === 'T1H') setGradientByTemperature(parseFloat(item.obsrValue));
        if (item.category === 'PTY') {
            const [iconUrl, condition] = displayCurrentWeatherIcon(item.obsrValue);
            $("#tempIcon").attr("src", iconUrl);
        }
        if (item.category === 'REH') $("#txtREH").text(item.obsrValue + " %");
        if (item.category === 'RN1') $("#txtRN1").text(item.obsrValue + " mm");
        if (item.category === 'WSD') $("#txtWSD").text(item.obsrValue + " m/s");
    }
}

function setGradientByTemperature(temperature) {
    let color = temperature >= 28 ? '#ED4C4C' :
        temperature >= 23 ? '#F38D4F' :
            temperature >= 20 ? '#FDB551' :
                temperature >= 17 ? '#F6D35B' :
                    temperature >= 12 ? '#93BB4F' :
                        temperature >= 9 ? '#84AB99' :
                            temperature >= 5 ? '#5C949E' : '#55749A';

    const gradient = `linear-gradient(to top, #FFFFFF 0%, ${color} 90%)`;
    $("#txtT1H").css({ 'background': gradient, '-webkit-background-clip': 'text', '-webkit-text-fill-color': 'transparent' });
    $("#txtT1H").text(temperature + "°C");
}

function getVilageFcstWeatherData(data) {
    let weeklyForecastData = {};
    data.forEach(item => {
        if (!weeklyForecastData[item.fcstDate]) weeklyForecastData[item.fcstDate] = {};
        if (!weeklyForecastData[item.fcstDate][item.fcstTime]) weeklyForecastData[item.fcstDate][item.fcstTime] = {};
        weeklyForecastData[item.fcstDate][item.fcstTime][item.category] = item.fcstValue;
    });

    let allAverages = calculateDailyAverages(weeklyForecastData);
    createElements(allAverages);
}

function createElements(item) {
    const todayFormatted = formatDate(new Date());
    for (const date in item) {
        if (date === todayFormatted) continue;

        let day_week = getDayOfWeekFromYYYYMMDD(date);
        const dailyData = item[date];
        const [iconUrl, condition] = displayCurrentWeatherIcon(Math.round(dailyData.PTY || 0).toString());

        let tmn = dailyData.TMN ? Math.round(dailyData.TMN) : "-";
        let tmx = dailyData.TMX ? Math.round(dailyData.TMX) : "-";

        const html = `
            <div class="weather-item row" id="item_${date}">
                <div class="day col-3 text-center">${day_week}</div>
                <div class="icon col-3 text-center"><img src="${iconUrl}" alt="${condition}"></div>
                <div class="condition col-3 text-center">${condition}</div>
                <div class="tempCotainSpan col-3 text-center">
                    <span class="tmptmx">${tmn}° / ${tmx}°</span>
                </div>
            </div>`;
        item_Container.insertAdjacentHTML('beforeend', html);
    }
}

function displayCurrentWeatherIcon(ptyCode) {
    const icons = {
        '0': ['images/sunny.svg', 'Sunny'],
        '1': ['images/rain.svg', 'Rain'],
        '2': ['images/sleet.svg', 'Sleet'],
        '3': ['images/snow.svg', 'Snow'],
        '4': ['images/shower.svg', 'Shower'],
        '5': ['images/drizzle.svg', 'Drizzle'],
        '6': ['images/light_sleet.svg', 'Light Sleet'],
        '7': ['images/flurries.svg', 'Flurries']
    };
    return icons[ptyCode] || ['images/unknown.png', 'Unknown'];
}

// --- 시간 및 날짜 처리 유틸리티 ---

function getBaseTimeForNcst() {
    const now = new Date();
    let baseHour = now.getHours();
    if (now.getMinutes() < 30) {
        baseHour--;
        if (baseHour < 0) {
            now.setDate(now.getDate() - 1);
            baseHour = 23;
        }
    }
    return { baseDate: formatDate(now), baseTime: String(baseHour).padStart(2, '0') + "30" };
}

function getBaseTimeForFcst() {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const fcstTimes = [2, 5, 8, 11, 14, 17, 20, 23];
    let baseTime = "2300";
    let baseDate = formatDate(now);
    let found = false;

    for (let i = fcstTimes.length - 1; i >= 0; i--) {
        if (hours > fcstTimes[i] || (hours === fcstTimes[i] && minutes >= 10)) {
            baseTime = String(fcstTimes[i]).padStart(2, '0') + "00";
            found = true;
            break;
        }
    }
    if (!found) {
        now.setDate(now.getDate() - 1);
        baseDate = formatDate(now);
        baseTime = "2300";
    }
    return { baseDate, baseTime };
}

function formatDate(date) {
    return date.getFullYear() + String(date.getMonth() + 1).padStart(2, '0') + String(date.getDate()).padStart(2, '0');
}

function calculateDailyAverages(weeklyData) {
    const dailyAverages = {};
    for (const date in weeklyData) {
        const sums = {};
        const counts = {};
        for (const time in weeklyData[date]) {
            for (const category in weeklyData[date][time]) {
                const val = parseFloat(weeklyData[date][time][category]);
                if (!isNaN(val)) {
                    sums[category] = (sums[category] || 0) + val;
                    counts[category] = (counts[category] || 0) + 1;
                }
            }
        }
        dailyAverages[date] = {};
        for (const cat in sums) dailyAverages[date][cat] = sums[cat] / counts[cat];
    }
    return dailyAverages;
}

function getDayOfWeekFromYYYYMMDD(yyyymmdd) {
    const date = new Date(yyyymmdd.substring(0, 4), yyyymmdd.substring(4, 6) - 1, yyyymmdd.substring(6, 8));
    return ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'][date.getDay()];
}

function fetchWeatherData(location) {
    while (item_Container.firstChild) item_Container.removeChild(item_Container.firstChild);
    getUltraSrtNcstData(location);
    getUltraSrtFcstData(location);
}

$(document).ready(() => fetchWeatherData(defaultLocation));