document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');

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

        // 🌟 일정 생성 로직 (select)은 그대로 유지
        select: function (info) {
            var title = prompt('새 일정 제목을 입력하세요:');
            console.log(info)
            if (title) {
                // 서버의 POST API로 일정 생성 요청
                createEventOnServer(title, info.startStr, info.endStr, info.allDay, calendar);
            }
            // 선택 영역 해제
            calendar.unselect();
        },
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
});

// 서버에 일정 생성 요청을 보내는 함수 (변경 없음)
function createEventOnServer(title, startStr, endStr, allDay, calendar) {
    // ... 기존 코드 유지 ...
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