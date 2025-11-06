let apiUrl = 'http://localhost:3000/news/dataList';
let keyword = '';
async function fetchNewsData(param) {
    // 1. 파라미터 객체 정의
    const params = {
        id: param
    };
    //2. URLSearchParams 객체 생성
    const urlParams = new URLSearchParams(params);
    // 3. 기존 URL에 쿼리 문자열 추가
    let apiUrlWithParams = param === undefined ? apiUrl : `${apiUrl}?${urlParams.toString()}`;
    try {
        const response = await fetch(apiUrlWithParams, {
            method: 'GET',
        });

        if (!response.ok) {
            throw new Error(`API 요청 실패: ${response.status}`);
        }

        const data = await response.json();
        console.log('API 호출 성공, 데이터:', data);

        // 데이터를 표시할 컨테이너 요소
        const container = document.getElementById('item_Container1');

        // 기존 내용을 비워줍니다 (선택 사항)
        container.innerHTML = '';

        if (data && data.items) {
            console.log(data.items);

            // `data.items` 배열의 각 항목을 순회합니다.
            data.items.forEach(item => {
                //     console.log(`Title: ${item.title}, Link: ${item.link}`);

                // 📌 반복문 안에서 각 항목별로 새로운 HTML 요소를 생성합니다.
                const newsItem = document.createElement('div');
                newsItem.classList.add('col-12', 'mb-3'); // Bootstrap 그리드 클래스 추가

                // 템플릿 리터럴을 사용해 HTML 내용을 구성합니다.
                // ${item.title}와 ${item.link}를 사용해 동적 데이터 삽입
                newsItem.innerHTML = `
                    <div class="card shadow-sm h-100 default-card">
                        <div class="card-body">
                            <h6 class="card-subtitle mb-2 text-body-secondary">${item.title}</h6>
                            <a href="${item.link}" class="card-link" target="_blank">기사 보러 가기</a>
                        </div>
                    </div>
                `;

                // 📌 생성된 요소를 컨테이너에 추가합니다.
                container.appendChild(newsItem);
            });
        }
    } catch (error) {
        console.error('API 호출 중 오류 발생:', error);
    }
}


// 초기 로드 시 날씨 정보 가져오기
$(document).ready(function () { // jQuery ready 함수를 사용하여 DOM 로드 후 실행
    fetchNewsData();
});