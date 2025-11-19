document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var calendarContainerEl = document.querySelector('.calendar-container'); // 전체 래퍼 클래스

    // 1월부터 12월까지의 배경 이미지 파일 경로를 배열로 정의합니다. (인덱스 0은 사용하지 않음)
    // 실제 이미지 경로에 맞게 수정하세요.
    const monthBackgroundImages = [
        null, // 인덱스 0 (사용 안 함)
        'images/january-bg.jpg',   // 1월
        'images/february-bg.jpg',  // 2월
        'images/march-bg.jpg',     // 3월
        'images/april-bg.jpg',     // 4월
        'images/may-bg.jpg',       // 5월
        'images/june-bg.jpg',      // 6월
        'images/july-bg.jpg',      // 7월
        'images/august-bg.jpg',    // 8월
        'images/september-bg.jpg', // 9월
        'images/october-bg.jpg',   // 10월
        'images/november-bg.jpg',  // 11월
        'images/december-bg.jpg'   // 12월
    ];

    // 💡 1. kbo_list 데이터를 FullCalendar Event Source 규격에 맞게 수정:
    //    이벤트 배열은 'events' 속성 아래에 위치해야 하며, 'id'를 최상위에 둡니다.
    const kbo_source = {
        id: 'kbo-toggle',
        events: [ // 💡 'event' 대신 'events' 속성을 사용해야 합니다.
            {
                title: 'KBO: LG vs KT (개막전)',
                start: '2025-10-01T17:00:00+09:00',
                backgroundColor: '#3366FF',
                allDay: false
            },
            {
                title: 'KBO: 두산 vs 롯데',
                start: '2025-10-05T17:00:00+09:00',
                backgroundColor: '#3366FF',
                allDay: false
            },
            {
                title: 'KBO: KIA vs 삼성',
                start: '2025-10-15T17:00:00+09:00',
                backgroundColor: '#3366FF',
                allDay: false,
            }]
    };

    // A의 일정 소스도 ID를 부여하여 토글할 준비
    const source_a = {
        id: 'schedule-a',
        url: 'http://localhost:3000/calendar/api/events/A',
        color: 'red'
    };

    // 공휴일 소스도 ID를 부여하여 토글할 준비
    const source_b = {
        id: 'schedule-b',
        url: 'http://localhost:3000/calendar/api/events/B',
        color: 'blue'
    };
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        displayEventTime: false,
        locale: 'ko',
        // headerToolbar: false,
        // headerToolbar: {
        //     left: 'prev,next today',
        //     center: 'title',
        //     right: 'dayGridMonth,timeGridWeek,timeGridDay'
        // },

        selectable: true,

        // 🌟 여러 일정 소스(Event Sources) 설정
        eventSources: [
            // 💡 2. ID가 포함된 전체 객체(source_a, kbo_source)를 배열에 추가
            source_a,
            //   source_b,
            kbo_source
        ],
        // 뷰가 변경될 때 (월 변경 시) 실행되는 콜백
        datesSet: function (info) {
            // 현재 달력의 시작 날짜 (startDate)를 가져옵니다.
            var currentMonth = info.view.currentStart.getMonth() + 1; // 1 (1월) ~ 12 (12월)

            // 1. 컨테이너에 월별 클래스 동적 추가 (기존 방식 유지)
            var monthClass = 'month-' + (currentMonth < 10 ? '0' : '') + currentMonth;

            // 기존 월별 클래스 제거
            calendarContainerEl.className = calendarContainerEl.className.split(' ')
                .filter(c => !c.startsWith('month-'))
                .join(' ');

            // 새 월별 클래스 추가
            calendarContainerEl.classList.add(monthClass);

            // 2. 배경 이미지 스타일을 동적으로 적용
            const imageUrl = monthBackgroundImages[currentMonth];

            if (imageUrl) {
                // 상단 커스텀 이미지 영역에 배경 이미지를 직접 적용
                const customHeaderImageEl = document.querySelector('.custom-header-image');

                // 이미지 태그가 있다면 숨기고, 배경으로 대체합니다.
                const imgTag = customHeaderImageEl.querySelector('img');
                if (imgTag) {
                    imgTag.style.display = 'none'; // 이미지 태그 숨기기
                }

                // 컨테이너 배경 스타일 적용
                customHeaderImageEl.style.backgroundImage = `url('${imageUrl}')`;
                customHeaderImageEl.style.backgroundSize = 'cover';
                customHeaderImageEl.style.backgroundPosition = 'center';
            }
        },
        // 🌟 일정 생성 로직 (select)은 그대로 유지
        select: function (info) {
            var title = prompt('새 일정 제목을 입력하세요:');
                        if (title) {
                // 서버의 POST API로 일정 생성 요청
                createEventOnServer(title, info.startStr, info.endStr, info.allDay, calendar);
            }
            // 선택 영역 해제
            calendar.unselect();
        }
        ,
        // 이벤트 클릭 핸들러
        eventClick: function (info) {
            // 캘린더 이벤트 객체 정보 (info.event)
            const event = info.event;

            // 이벤트의 확장 속성 (extendedProps)에 저장된 세부 내용에 접근
            const detail = event.extendedProps.detail || '세부 정보 없음';

            // **세부 내용을 표시하는 방식**

            // 1. 간단한 Alert 창으로 표시
            alert(`[${event.title}]\n\n시작: ${event.startStr}\n종료: ${event.endStr || '(종일)'}\n\n세부 내용:\n${detail}`);

            // 2. 모달(Modal) 창 또는 사이드바(Sidebar)를 띄워 세부 정보를 보여줄 수도 있습니다.
            // showDetailModal(event.title, event.start, event.end, detail);
        }

        // ... 기타 옵션 ...
    });

    calendar.render();

    // 💡 3. setupEventSourceToggles 함수 호출 시 배열을 전달
    //    A의 일정 토글도 함께 처리할 수 있도록 배열로 전달합니다.
    setupEventSourceToggles(calendar, [source_a, kbo_source]);
})
;

// 서버에 일정 생성 요청을 보내는 함수 (구현 예시)
function createEventOnServer(title, startStr, endStr, allDay, calendar) {
    // 1. 서버로 보낼 데이터 준비
    const eventData = {
        title: title,
        start: startStr,
        end: endStr,
        allDay: allDay,
        calendarId: calendar // 어떤 캘린더에 추가할지 식별자 (선택 사항)
    };

    // 2. Fetch API를 사용하여 서버의 엔드포인트로 POST 요청 전송
    const serverEndpoint = 'http://localhost:3000/calendar/api/insert'; // 실제 서버의 일정 생성 API 경로로 변경하세요.

    fetch(serverEndpoint, {
        method: 'POST', // 데이터 생성 요청이므로 POST 메서드를 사용합니다.
        headers: {
            'Content-Type': 'application/json', // 보내는 데이터 형식은 JSON입니다.
            // 필요하다면 인증 토큰 등을 추가할 수 있습니다 (예: 'Authorization': 'Bearer YOUR_TOKEN')
        },
        body: JSON.stringify(eventData) // JavaScript 객체를 JSON 문자열로 변환하여 전송
    })
        .then(response => {
            // 응답 상태 확인 (HTTP 200-299 코드는 성공으로 간주)
            if (!response.ok) {
                // 서버에서 오류 응답이 왔을 경우
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json(); // 서버 응답 본문을 JSON으로 파싱
        })
        .then(data => {
            // 3. 서버 응답 처리
            console.log('Event created successfully on server:', data);
            alert('일정이 서버에 성공적으로 저장되었습니다.');

            // 서버에서 반환된 새 이벤트 ID 등으로 캘린더 UI를 업데이트하는 추가 로직이 필요할 수 있습니다.
            // 예를 들어, data.eventId를 사용하여 프론트엔드 캘린더 요소의 ID를 설정합니다.

        })
        .catch(error => {
            // 4. 요청 실패 또는 오류 응답 처리
            console.error('Error creating event on server:', error);
            alert('일정 생성 중 오류가 발생했습니다: ' + error.message);
        });
}

// 💡 4. setupEventSourceToggles 함수 수정: 배열을 처리할 수 있도록 유지
/**
 * 체크박스 상태에 따라 FullCalendar의 Event Source를 토글하는 함수
 * @param {FullCalendar.Calendar} calendar
 * @param {Array<Object>} eventSourcesConfig - ID와 데이터를 포함한 Event Source 설정 배열
 */
function setupEventSourceToggles(calendar, eventSourcesConfig) {
    console.log(eventSourcesConfig);

    // 이 부분에서 'kbo-toggle'과 'schedule-a' 두 개의 체크박스를 찾을 수 있습니다.
    eventSourcesConfig.forEach(source => {
        // 체크박스의 ID는 Event Source의 ID와 동일하다고 가정합니다.
        const checkbox = document.getElementById(source.id);

        if (checkbox) {
            checkbox.addEventListener('change', function () {
                const sourceId = source.id;
                const isChecked = this.checked;

                // 1. 일정 소스 ID로 현재 캘린더에 등록되어 있는지 확인
                let existingSource = calendar.getEventSourceById(sourceId);

                if (isChecked) {
                    // 체크됨: 캘린더에 없으면 추가 (다시 로드)
                    if (!existingSource) {
                        // 💡 배열에서 해당 ID를 가진 소스 객체 전체를 찾아서 추가
                        const sourceToAdd = eventSourcesConfig.find(s => s.id === sourceId);
                        if (sourceToAdd) {
                            calendar.addEventSource(sourceToAdd);
                        }
                    }
                } else {
                    // 체크 해제됨: 캘린더에 있으면 제거 (숨김)
                    if (existingSource) {
                        // 💡 FullCalendar API 메서드를 사용하여 소스를 제거합니다.
                        existingSource.remove();
                    }
                }
            });
        }
    });
}