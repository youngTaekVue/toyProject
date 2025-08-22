let administrativeData = {}; // 전역 변수로 지역 데이터 관리
const fileInput = document.getElementById('fileInput');
const provinceSelect = document.getElementById('provinceSelect');
const citySelect = document.getElementById('citySelect');
const districtSelect = document.getElementById('districtSelect');

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) {
        return;
    }

    const reader = new FileReader();

    reader.onload = (event) => {
        const data = new Uint8Array(event.target.result);
        const workbook = XLSX.read(data, {type: 'array'});

        const sheetNameList = workbook.SheetNames;
        console.log('시트 이름:', sheetNameList);

        const firstSheetName = sheetNameList[0];
        const jsonData = XLSX.utils.sheet_to_json(workbook.Sheets[firstSheetName]);

        administrativeData = convertJsonArrayToAdministrativeData(jsonData);
        populateProvinces(administrativeData); // 데이터 변환 후 시/도 옵션 로드
        console.log('최종 지역 데이터:', administrativeData);
    };

    reader.readAsArrayBuffer(file);
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
    console.log(data);
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
    const selectedProvince = event.target.value;
    populateCities(selectedProvince);
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
        fetchWeatherData(defaultLocation);
    }
});