# KULT

> Kyunghee University Library Toolkit v0.1.0a1

경희대학교 중앙도서관 앱을 참고해 만든 비공식 파이썬 라이브러리입니다. 좌석예약, 연장, 사용내역 조회 등이 가능합니다.

악용 방지를 위해 도서관 서버 주소는 제외하고 배포하였습니다. 직접 해당부분을 수정하신 후 사용해주십시오.

아직 미구현된 부분이 많습니다. 사용 전 참고바랍니다.

## Installation

```
$ git clone https://github.com/lewisleedev/kult.git

// 도서관 서버 주소 수정

$ python setup.py install
```

## Quick Start
```
import kult

client = kult.Client(student_id)
client.get_user_data() # returns dictionary
client.get_seat_history() # returns list of dictionaries
client.set_seat(seat_number, room_number)
client.continue_seat(seat_number, room_number)
```