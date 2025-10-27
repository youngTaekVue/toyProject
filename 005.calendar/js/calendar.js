document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'ko',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },

        selectable: true, // 👈 일정 추가를 위해 필수

        // 🌟 조회 API (기존 코드)
        events: 'http://localhost:3000/calendar/api/events',

        // 🌟 일정 생성 로직 (추가)
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

        // ... 기타 옵션 ...
    });

    calendar.render();
});

// 서버에 일정 생성 요청을 보내는 함수
function createEventOnServer(title, startStr, endStr, allDay, calendar) {
    const eventData = {
        title: title,
        start: startStr,
        end: endStr,
        allDay: allDay
    };

    fetch('http://localhost:3000/calendar/api/insert', { // 👈 POST 요청
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventData),
    })
        .then(response => {
            if (!response.ok) {
                // 서버 응답이 200이 아닐 경우 오류 처리
                return response.json().then(err => {
                    throw new Error(err.error || '일정 추가 실패');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.id) {
                alert('일정이 성공적으로 추가되었습니다!');
                // FullCalendar에 이벤트 추가 및 화면 새로고침
                calendar.addEvent({
                    id: data.id,
                    title: data.title,
                    start: data.start,
                    end: data.end,
                    allDay: data.allDay,
                    url: data.url // Google Calendar 링크 포함
                });
            } else {
                // 이 코드는 보통 실행되지 않지만, 만약을 위해 처리
                alert('일정 추가 실패: 서버 응답 오류');
            }
        })
        .catch(error => {
            console.error('클라이언트 요청 또는 서버 처리 오류:', error);
            alert(`일정 추가 중 오류가 발생했습니다: ${error.message}`);
        });
}