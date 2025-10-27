let myData;
const weatherInfoDiv = document.getElementById('weather-info');
let nx = 59;
let ny = 120;
let defaultLocation = [nx, ny];
// 현재 날짜와 시간
const now = new Date();
const year = now.getFullYear();
const month = String(now.getMonth() + 1).padStart(2, '0');
const day = String(now.getDate()).padStart(2, '0');
const hours = String(now.getHours()).padStart(2, '0');
const minutes = String(now.getMinutes()).padStart(2, '0');
let {baseDate, baseTime} = getBaseTime();
let apiName = "";
let item_Container = document.getElementById("item_Container");


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
function getUltraSrtNcstData(location) {
    let apiName = "getUltraSrtNcst";
    //console.log("defaultLocation.nx : " + defaultLocation[0] + ", location.ny : " + defaultLocation[1]);
    getApiCall(apiName, location);
}

function getUltraSrtFcstData(location) {
    let apiName = "getVilageFcst";
    getReBaseTime();
    getApiCall(apiName, location);
}


async function getApiCall(name, lodata) {
    let allAverages;
    const apiUrl = ' http://localhost:3000/weather/search';
    const dataToSend = {
        name: name,
        numOfRows: '1052',
        pageNo: '1',
        dataType: 'JSON',
        baseDate : baseDate,
        baseTime : baseTime,
        nx: lodata[0],
        ny: lodata[1],
    };

    let response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // JSON 형식으로 보낼 때 필수
        },
        body: JSON.stringify(dataToSend) // 객체를 JSON 문자열로 변환
    });

    if (!response.ok) {
        throw new Error(`API 요청 실패: ${response.status}`);
    }

    const data = await response.json();
    console.log('API 호출 성공, 데이터:', data);
    if (data.response.header.resultCode === '00') {
        // 응답 성공 시 items 배열에서 날씨 정보를 추출하여 화면에 표시
        const items = data.response.body.items.item;
        if (name === "getUltraSrtNcst") {
            getUltraSrtNcstWeatherData(items, name);
        } else if (name === "getVilageFcst") {
            getVilageFcstWeatherData(items, name);
        }
    } else {
        // 응답 실패 시 에러 메시지 표시
        weatherInfoDiv.innerHTML = `<p>날씨 정보를 불러오는 데 실패했습니다: ${data.response.header.resultMsg}</p>`;
    }
}

// 초단기실황조회 API 응답 데이터에서 필요한 날씨 정보를 추출하여 화면에 표시합니다.
function getUltraSrtNcstWeatherData(data, param) {
    for (const item of data) {
        // 1시간 기온 (T1H)
        if (item.category === 'T1H') {
            setGradientByTemperature(item.obsrValue)
        }
        // 강수 형태 (PTY)
        if (item.category === 'PTY') {
            const ptyCode = item.obsrValue;
            $("#tempIcon").attr("src", displayCurrentWeatherIcon(ptyCode)[0]);
            $('.icon').attr('fill', '#ED4C4C');
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

function setGradientByTemperature(temperature) {
    let color;
    let icon = $('#tempIcon');
    switch (true) {
        case temperature >= 28:
            color = '#ED4C4C'; // 붉은색
            //$('#tempIcon').attr('fill', '#ED4C4C');

            break;
        case temperature >= 23:
            color = '#F38D4F'; // 주황색
            break;
        case temperature >= 20:
            color = '#FDB551'; // 노란색
            break;
        case temperature >= 17:
            color = '#F6D35B'; // 연한 노란색
            break;
        case temperature >= 12:
            color = '#93BB4F'; // 초록색
            break;
        case temperature >= 9:
            color = '#84AB99'; // 연한 초록색
            break;
        case temperature >= 5:
            color = '#5C949E'; // 청록색
            break;
        default:
            // 5도 미만
            color = '#55749A'; // 파란색
            break;
    }

    const gradient = `linear-gradient(to top, #FFFFFF 0%, ${color} 90%)`;
    // HTML body에 그라디언트 적용
    // 여러 접두사를 포함하는 객체로 설정
    $("#txtT1H").css({
        'background': gradient,
        '-webkit-background-clip': 'text',
        '-webkit-text-fill-color': 'transparent'
    });
    $("#txtT1H").text(temperature + "°C"); // jQuery를 사용하여 텍스트 설정
}


function getVilageFcstWeatherData(data, param) {
    let weeklyForecastData = {};

    data.forEach(item => {
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
    //console.log(`${baseDate} ${baseTime} 예보 데이터 저장 완료`);
    allAverages = calculateDailyAverages(weeklyForecastData);
    let arrAver1 = [];
    arrAver1.push(allAverages)
    arrAver1.forEach(item => {
        createElemnt(item)
    });
}

function createElemnt(item) {
    //console.log(item);

    let dailyMinMaxTemps = {};
    // item 객체 내의 각 날짜(예: "20250630")를 순회합니다.
    for (const date in item) {
        // 해당 속성이 item 객체 자체의 속성인지 확인 (상속된 속성 방지)
        if (item.hasOwnProperty(date)) {

            let day_week = getDayOfWeekFromYYYYMMDD(date);

            const dailyAverageData = item[date]; // 해당 날짜의 평균 날씨 데이터 객체입니다.

            //console.log(`--- 날짜: ${date} ---`);
            let str_tmp = "";
            let str_tmx = "";
            let str_tmn = "";
            let precipitationProbability = "";
            let ptyCode = "";
            let humidity = "";
            let skyCode = "";
            let windSpeed = "";
            let windDirection = "";
            let waveHeight = "";
            let iconUrl = "";
            let condition = "";

            if (baseDate == date) {
                continue;
            }

            // 1. **기온 (TMP) 추출**
            if (dailyAverageData.hasOwnProperty('TMP')) {
                str_tmp = parseFloat(dailyAverageData.TMP).toFixed(1);
            }

            if (dailyAverageData.hasOwnProperty('TMX')) {
                str_tmx = parseFloat(dailyAverageData.TMX).toFixed(1);
                console.log('str_tmx : ' + str_tmx);
            }

            if (dailyAverageData.hasOwnProperty('TMN') != null) {
                str_tmn = parseFloat(dailyAverageData.TMN).toFixed(1);
                console.log('str_tmn : ' + str_tmn);
            }


            // 2. **강수확률 (POP) 추출**
            if (dailyAverageData.hasOwnProperty('POP')) {
                precipitationProbability = parseFloat(dailyAverageData.POP).toFixed(1);
                //console.log(`  강수확률 (POP): ${precipitationProbability}%`);
                // HTML 요소에 적용: $(`#weather-container-${date} .txtPOP`).text(`${precipitationProbability}%`);
            }

            // 3. **강수 형태 (PTY) 추출 및 변환**
            // PTY는 코드이므로 반올림 후 변환 함수 사용
            if (dailyAverageData.hasOwnProperty('PTY')) {
                ptyCode = Math.round(parseFloat(dailyAverageData.PTY)).toString();
                iconUrl = displayCurrentWeatherIcon(ptyCode)[0];
                condition = displayCurrentWeatherIcon(ptyCode)[1];
            }

            // 강수 형태 (PTY)
            // if (item.category === 'PTY') {
            //     const ptyCode = item.obsrValue;
            //     displayCurrentWeatherIcon(ptyCode, param);
            // }

            // 4. **습도 (REH) 추출**
            if (dailyAverageData.hasOwnProperty('REH')) {
                humidity = parseFloat(dailyAverageData.REH).toFixed(1);
                // console.log(`  습도 (REH): ${humidity}%`);
            }

            // 5. **하늘 상태 (SKY) 추출 및 변환**
            // SKY는 코드이므로 반올림 후 변환 함수 사용
            if (dailyAverageData.hasOwnProperty('SKY')) {
                skyCode = Math.round(parseFloat(dailyAverageData.SKY));
                // console.log(`  하늘 상태 (SKY 코드): ${skyCode}`);
            }

            // 6. **풍속 (WSD) 추출**
            if (dailyAverageData.hasOwnProperty('WSD')) {
                windSpeed = parseFloat(dailyAverageData.WSD).toFixed(1);
                // console.log(`  풍속 (WSD): ${windSpeed} m/s`);
            }

            // 7. **풍향 (VEC) 추출**
            // VEC는 각도이므로 반올림 후 사용
            if (dailyAverageData.hasOwnProperty('VEC')) {
                windDirection = parseFloat(dailyAverageData.VEC).toFixed(0);
                //console.log(`  풍향 (VEC): ${windDirection}°`);
            }

            // 8. **파고 (WAV) 추출**
            // WAV는 특수 값(-999) 처리
            if (dailyAverageData.hasOwnProperty('WAV')) {
                waveHeight = parseFloat(dailyAverageData.WAV);
                if (waveHeight !== -999) {
                    //  console.log(`  파고 (WAV): ${waveHeight.toFixed(1)} m`);
                    // HTML 요소에 적용: $(`#weather-container-${date} .txtWAV`).text(`${waveHeight.toFixed(1)} m`);
                } else {
                    //  console.log(`  파고 (WAV): 정보 없음`);
                    // HTML 요소에 적용: $(`#weather-container-${date} .txtWAV`).text(`정보 없음`);
                }
            }

            // UUU (동서바람성분), VVV (남북바람성분) 등은 필요에 따라 추출 및 활용
            if (dailyAverageData.hasOwnProperty('UUU')) {
                const uuu = parseFloat(dailyAverageData.UUU).toFixed(2);
                //console.log(`  동서바람성분 (UUU): ${uuu}`);
            }
            if (dailyAverageData.hasOwnProperty('VVV')) {
                const vvv = parseFloat(dailyAverageData.VVV).toFixed(2);
                //  console.log(`  남북바람성분 (VVV): ${vvv}`);
            }

            const itemDiv = document.createElement('div');
            const col12Contain = document.createElement('div');
            const conDayweek = document.createElement('div');
            const conIcon = document.createElement('div');
            const conWeather = document.createElement('div');
            const conTempe = document.createElement('div');
            const spanTmpTmx = document.createElement('span');
            const spanTmx = document.createElement('span');

            itemDiv.classList.add('weather-item', 'row');
            itemDiv.id = 'item_' + date;


            // <span class="day"> 요소 생성 및 추가
            //const daySpan = document.createElement('span');
            conDayweek.classList.add('day', 'col-3', 'text-center');
            conDayweek.textContent = day_week;
            itemDiv.appendChild(conDayweek);
            item_Container.appendChild(itemDiv);

            // // <img> 요소 생성 및 추가
            const iconImg = document.createElement('img');
            iconImg.src = iconUrl;
            iconImg.alt = condition; // alt 속성도 날씨 상태로 설정하는 것이 좋습니다.
            //iconImg.classList.add('weather-icon');
            conIcon.classList.add('icon', 'col-3', 'text-center');
            conIcon.appendChild(iconImg);
            itemDiv.appendChild(conIcon);

            // <span class="condition"> 요소 생성 및 추가
            // const conditionSpan = document.createElement('span');
            conWeather.classList.add('condition', 'col-3', 'text-center');
            conWeather.textContent = condition;
            itemDiv.appendChild(conWeather);

            //const tempCotainSpan = document.createElement('span');
            conTempe.classList.add('tempCotainSpan', 'col-3', 'text-center');
            itemDiv.appendChild(conTempe);

            // <span class="temperature"> 요소 생성 및 추가
            //const tempSpan = document.createElement('span');
            spanTmpTmx.classList.add('tmptmx');
            spanTmpTmx.textContent = str_tmx !== "" ? str_tmn + "° / " + str_tmx + "°" : " - ";
            conTempe.appendChild(spanTmpTmx);

        }
    }
}


// 강수 형태 코드에 따라 날씨 아이콘 URL을 반환합니다.
function displayCurrentWeatherIcon(ptyCode) {
    let iconUrl = '';
    let condition = '';

    switch (ptyCode) {
        case '0': // 강수 없음
            iconUrl = 'images/sunny.svg'; // 예시: 맑음 아이콘
            condition = 'Sunny';
            break;
        case '1': // 비
            iconUrl = 'images/rain.svg';
            condition = 'Rain';
            break;
        case '2': // 비/눈
            iconUrl = 'images/sleet.svg';
            condition = 'Sleet';
            break;
        case '3': // 눈
            iconUrl = 'images/snow.svg';
            condition = 'Snow';
            break;
        case '4': // 소나기
            iconUrl = 'images/shower.svg';
            condition = 'Shower';
            break;
        case '5': // 빗방울
            iconUrl = 'images/drizzle.svg';
            condition = 'Drizzle';
            break;
        case '6': // 진눈깨비
            iconUrl = 'images/light_sleet.svg';
            condition = 'Light_sleet';
            break;
        case '7': // 눈날림
            iconUrl = 'images/flurries.svg';
            condition = 'Flurries';
            break;
        default:
            iconUrl = 'images/unknown.png'; // 예외 처리
            condition = 'Unknown';
            break;
    }

    return [iconUrl, condition];
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

function getDayOfWeekFromYYYYMMDD(yyyymmdd) {
    // YYYY, MM, DD 추출
    const year = parseInt(yyyymmdd.substring(0, 4));
    const month = parseInt(yyyymmdd.substring(4, 6)) - 1; // 월은 0부터 시작하므로 1을 빼줍니다.
    const day = parseInt(yyyymmdd.substring(6, 8));

    // Date 객체 생성
    const date = new Date(year, month, day);
    // 요일 배열
    const days = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];
    // 요일 반환
    return days[date.getDay()];
}

/**
 * 모든 날씨 데이터를 가져오는 메인 함수
 */
function fetchWeatherData(location) {
    //item_Container.removeChild()
    // 자식 요소가 있는 동안 계속 제거합니다.
    while (item_Container.firstChild) {
        item_Container.removeChild(item_Container.firstChild);
    }
    console.log("Fetching current weather data...");
    getUltraSrtNcstData(location); // 초단기 실황 데이터 가져오기

    console.log("Fetching forecast data...");
    console.log(location);
    getUltraSrtFcstData(location); // 단기 예보 데이터 가져오기

}

// 초기 로드 시 날씨 정보 가져오기
$(document).ready(function () { // jQuery ready 함수를 사용하여 DOM 로드 후 실행
    fetchWeatherData(defaultLocation);
});