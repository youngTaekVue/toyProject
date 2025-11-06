let administrativeData = {}; // 전역 변수로 지역 데이터 관리
const fileInput = document.getElementById('fileInput');
const provinceSelect = document.getElementById('provinceSelect');
const citySelect = document.getElementById('citySelect');
const districtSelect = document.getElementById('districtSelect');

document.addEventListener('DOMContentLoaded', () => {
    //console.log('DOMContentLoaded');
    fetch('./file/coordinate.csv')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text(); // 텍스트 형태로 응답을 받음
        })
        .then(csvText => {
            // csvText 변수에 CSV 데이터가 문자열로 담겨 있습니다.
            // 이제 이 데이터를 파싱해야 합니다.

            // CSV 데이터를 읽기 위한 워크북 생성 (XLSX.read는 파일 데이터 또는 문자열을 처리할 수 있음)
            // 타입은 'csv'로 지정하여 CSV 형식임을 명시합니다.
            const workbook = XLSX.read(csvText, {type: 'string', FS: ',', raw: true});

            // 모든 시트 이름 가져오기
            const sheetNameList = workbook.SheetNames;
            //console.log('시트 이름:', sheetNameList);

            // 첫 번째 시트 이름 가져오기
            const firstSheetName = sheetNameList[0];
            //console.log('첫 번째 시트 이름:', firstSheetName);

            // 해당 시트의 데이터를 JSON 형식으로 변환
            const jsonData = XLSX.utils.sheet_to_json(workbook.Sheets[firstSheetName]);

            administrativeData = convertJsonArrayToAdministrativeData(jsonData);
            populateProvinces(administrativeData); // 데이터 변환 후 시/도 옵션 로드
        })
        .catch(error => {
            console.error('There was a problem fetching the CSV file:', error);
        });
});


function convertJsonArrayToAdministrativeData(jsonArray) {
    const data = {};

    jsonArray.forEach(item => {
        const province = item['1단계'];
        const city = item['2단계'];
        const district = item['3단계'];
        const nx = item['격자 X'];
        const ny = item['격자 Y'];

        if (province && city && district && nx && ny) {
            if (!data[province]) {
                data[province] = {};
            }

            if (!data[province][city]) {
                data[province][city] = [];
            }

            if (!data[province][city].some(d => d.name === district)) {
                data[province][city].push({name: district, nx: nx, ny: ny});
            }
        }
    });

    for (const province in data) {
        for (const city in data[province]) {
            data[province][city].sort((a, b) => a.name.localeCompare(b.name));
        }
    }
    console.log('변환된 JSON 데이터:', data);
    return data;
}

// 시/도 옵션 생성
function populateProvinces(data) {
        provinceSelect.innerHTML = '<option value="" disabled selected>시/도</option>';
    for (const province in data) {
        const option = document.createElement('option');
        option.value = province;
        option.textContent = province;
        provinceSelect.appendChild(option);
    }
}

// 군/구 옵션 생성
function populateCities(selectedProvince) {
    citySelect.innerHTML = '<option value="" disabled selected>군/구</option>';
    districtSelect.innerHTML = '<option value="" disabled selected>읍/면/동</option>';
    districtSelect.disabled = true;

    if (selectedProvince && administrativeData[selectedProvince]) {
        citySelect.disabled = false;
        for (const city in administrativeData[selectedProvince]) {


            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        }
    } else {
        citySelect.disabled = true;
    }
}

// 읍/면/동 옵션 생성
function populateDistricts(selectedCity) {
    districtSelect.innerHTML = '<option value="" disabled selected>읍/면/동</option>';

    const selectedProvince = provinceSelect.value;

    if (selectedProvince && selectedCity && administrativeData[selectedProvince] && administrativeData[selectedProvince][selectedCity]) {
        districtSelect.disabled = false;
        administrativeData[selectedProvince][selectedCity].forEach(districtInfo => {
            const option = document.createElement('option');
            option.value = JSON.stringify({nx: districtInfo.nx, ny: districtInfo.ny});
            option.textContent = districtInfo.name;
            districtSelect.appendChild(option);
        });
    } else {
        districtSelect.disabled = true;
    }
}

// 이벤트 리스너 등록
provinceSelect.addEventListener('change', (event) => {
    let selectedProvince = event.target.value;

    populateCities(selectedProvince);
    keyword = selectedProvince;
});

citySelect.addEventListener('change', (event) => {
    const selectedCity = event.target.value;
    populateDistricts(selectedCity);
});

districtSelect.addEventListener('change', (event) => {
    const selectedValue = event.target.value;
    if (selectedValue) {
        const locationInfo = JSON.parse(selectedValue);
        const selectedNx = locationInfo.nx;
        const selectedNy = locationInfo.ny;
        let defaultLocation = [selectedNx, selectedNy];
        fetchWeatherData(defaultLocation); //선택한 지역을 기반으로 날씨 조회
        fetchNewsData(keyword);
    }
});