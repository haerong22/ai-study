-- MODEL 데이터
INSERT INTO MODEL (ID, FILENAME, FILEPATH, LATITUDE, LONGITUDE, HEIGHT, SCALE)
VALUES (1, 'apt.glb', 'models/apt.glb', 37.1234, 127.5678, 0, 5),
       (2, 'tank.glb', 'models/tank.glb', 49.74136445847585, 34.58589998728861, 0, 3),
       (3, 'flag.glb', 'models/flag.glb', 41.544515850107736, 15.453174075468738, 0, 10);

-- ARTICLE 데이터
INSERT INTO ARTICLE (ID, MODEL_ID, CONTENT, IMAGE_URL, TITLE)
VALUES (1, 1, '한국의 지방 소멸 현상은 인구 감소와 고령화로 인해 지방 지역의 경제적, 사회적, 문화적 생태계가 쇠퇴하는 문제를 의미합니다.
- 인구 이동: 대도시로의 인구 집중으로 농촌과 중소도시의 인구가 줄어들고 있습니다.', 'https://m.segye.com/content/image/2022/11/13/20221113509033.jpg',
        '한국의 지방 소멸 이대로 괜찮은가?'),
       (2, 2, '러시아-우크라이나 전쟁
러시아-우크라이나 전쟁은 2022년 2월 24일 러시아의 우크라이나 침공으로 시작되었습니다.
러시아는 우크라이나 동부 지역의 분리주의 세력을 지원하며, 이 지역의 독립을 인정하겠다고 발표했습니다.',
        'https://img.sbs.co.kr/newimg/news/20221110/201719467_1280.jpg', '러시아 우크라이나 전쟁'),
       (3, 3, '이탈리아의 이민자 문제
이탈리아는 지리적 위치로 인해 지중해를 건너 유럽으로 들어오는 이민자들의 주요 경유지 중 하나입니다.
특히, 북아프리카와 중동 지역의 불안정한 정세로 인해 많은 이민자가 이탈리아로 유입되고 있습니다.',
        'https://dimg.donga.com/wps/NEWS/IMAGE/2016/08/02/79514884.1.jpg', '유럽의 이주민 문제');