# 10D FCD (Fan Cooler Display) 테마 제작 및 에디터 개발 종합 가이드

본 문서는 **10D FCD (Fan Cooler Display)** 시스템의 선언형 테마(Theme) 제작 및 차세대 테마 에디터 개발을 위한 공식 개발 명세서입니다.  
다른 AI 에이전트 또는 디자이너/개발자가 10개 이상의 신규 프리셋 테마를 제작하거나 에디터를 구현할 때 본 가이드의 모든 규칙과 제약 사항을 준수해야 합니다.

---

## 1. 하드웨어 스펙 및 시스템 아키텍처

| 항목 | 상세 사양 | 주의 및 제약 사항 |
| :--- | :--- | :--- |
| **타겟 장치** | **ESP32-2432S028 (CYD / Cheap Yellow Display)** | ESP32-WROOM-32 듀얼코어 240MHz, 520KB SRAM |
| **디스플레이** | **2.8인치 ILI9341 TFT-LCD (저항식 터치)** | 세로 모드(Portrait) 고정: **240 × 320 픽셀** |
| **화면 포맷** | 16-bit RGB565 Little-Endian | 240x320 프레임 버퍼 크기: 153,600 바이트 (150KB) |
| **설치 환경** | **PC 쿨러 팬 중앙 및 케이스 내부 HUD** | 블랙 아크릴/강화유리 내부에서 발광하므로 **다크 모드(Dark Mode)** 필수 |
| **스트리밍 파이프라인** | PC 클라이언트 ➔ Wi-Fi TCP/UDP 스트리밍 (20~30 FPS) | PC에서 테마를 240x320 고화질 렌더링 후 MJPEG 실시간 무선 전송 |
| **폰트 가독성 원칙** | 240×320 작은 화면에 최적화된 폰트 크기 | 윈도우 기본 맑은 고딕(`malgun.ttf`, `malgunbd.ttf`) 또는 Arial 볼드 권장 |

> [!IMPORTANT]
> **해상도와 종횡비**: 모든 테마는 가로 **240px**, 세로 **320px** 세로 화면 기준입니다. 가로 해상도가 240px로 매우 컴팩트하므로 가로 여백(Padding)을 10~15px 이내로 컴팩트하게 배치해야 텍스트 잘림이 발생하지 않습니다.

---

## 2. 테마 폴더 및 파일 구조

모든 테마는 `cyd_streamer/pc_client/themes/<theme_id>/` 개별 폴더 내에 위치합니다.

```
cyd_streamer/pc_client/themes/
├── THEME_GUIDE.md               # 본 개발 가이드라인
├── classic_hud/                 # 디자인 1: 기본 클래식 쿨러 코어 HUD
│   ├── theme.json               # 선언형 테마 정의 파일
│   └── preview.png              # 240x320 썸네일 미리보기 이미지
├── cyber_neon/                  # 디자인 2: 사이버 네온 HUD
│   ├── theme.json
│   └── preview.png
└── <신규_테마_폴더명>/
    ├── theme.json               # 필수
    ├── preview.png              # 필수 (240x320 PNG)
    ├── background.png           # 선택 (배경 이미지 사용 시)
    └── icons/                   # 선택 (아이콘 또는 로고 오버레이)
        └── cpu_icon.png
```

---

## 3. 선언형 JSON 테마 스키마 (`theme.json`)

### 최상위 필드 구조
```json
{
  "id": "theme_unique_id",
  "name": "테마 표시 이름 (한국어 또는 영어)",
  "version": "1.0.0",
  "author": "제작자 이름 (e.g. 10D Official, AI Designer)",
  "description": "테마에 대한 한 줄 설명",
  "background_color": [10, 14, 22],
  "background_image": "background.png",
  "elements": [
    ...
  ]
}
```

* `background_color`: `[R, G, B]` (0~255). 배경 이미지가 없을 때 단색으로 칠해집니다.
* `background_image`: (선택) 테마 폴더 기준 상대 경로. 240×320 크기로 자동 스케일링됩니다.
* `elements`: 화면에 순서대로(Z-index 순서) 렌더링될 요소 목록입니다.

---

## 4. 지원 UI 요소 (Element Types)

### 1) 텍스트 (`type: "text"`)
실시간 하드웨어 토큰 치환을 지원하는 텍스트입니다.
```json
{
  "type": "text",
  "text": "%cpu%% (%c_sta%)",
  "x": 220,
  "y": 235,
  "font": "malgunbd.ttf",
  "size": 13,
  "color": [248, 250, 252],
  "anchor": "ra"
}
```
* `anchor`: Pillow 텍스트 앵커 규격
  * `la`: 좌측 상단 (Left-Ascent) - 기본값
  * `ra`: 우측 상단 (Right-Ascent) - 우측 정렬 시 유용
  * `mm`: 중앙 (Middle-Middle) - 센터 정렬
  * `ms`: 중앙 하단 (Middle-Baseline)

### 2) 프로그레스 바 (`type: "bar"`)
시스템 센서(CPU, RAM, DISK 등)와 연동되는 직선형 진행도 바입니다.
```json
{
  "type": "bar",
  "bind": "cpu",
  "direction": "horizontal",
  "x": 20,
  "y": 250,
  "w": 200,
  "h": 8,
  "radius": 4,
  "bg_color": [28, 34, 46, 255],
  "fill_color": [0, 229, 255, 255]
}
```
* `bind`: `"cpu"`, `"ram"`, `"disk"` 중 선택
* `direction`: `"horizontal"` (가로) 또는 `"vertical"` (세로)
* `radius`: 모서리 둥글기 반경 (픽셀)

### 3) 원형 회전 쿨러 링 (`type: "ring"`)
쿨러 팬이 도는 듯한 시각적 효과를 주는 회전 듀얼 아크 링입니다.
```json
{
  "type": "ring",
  "cx": 120,
  "cy": 140,
  "radius": 50,
  "width": 5,
  "speed": 120,
  "color1": [0, 229, 255],
  "color2": [59, 130, 246]
}
```
* `cx`, `cy`: 링 중심 좌표 (240x320 기준 중심은 x=120)
* `speed`: 초당 회전 각도 (120이면 3초에 1회전)

### 4) 게이지 아크 미터 (`type: "arc_meter"` 또는 `"gauge"`)
원형 센서 계기판 형태로 하드웨어 부하율을 표시합니다.
```json
{
  "type": "arc_meter",
  "bind": "cpu",
  "cx": 120,
  "cy": 140,
  "radius": 45,
  "width": 6,
  "start_angle": 135,
  "sweep_angle": 270,
  "bg_color": [40, 50, 65],
  "fill_color": [0, 229, 255]
}
```
* `start_angle`: 시작 각도 (도)
* `sweep_angle`: 전체 회전 폭 (도, 예: 270도)

### 5) 라운드 사각형 박스 (`type: "box"`)
HUD 위젯 카드 배경이나 글래스모피즘 반투명 패널입니다.
```json
{
  "type": "box",
  "x": 10,
  "y": 10,
  "w": 220,
  "h": 50,
  "radius": 8,
  "fill": [14, 17, 24, 190],
  "outline": [45, 55, 72, 255]
}
```
* `fill`: `[R, G, B, Alpha]` (Alpha 0~255)
* `outline`: 테두리 색상 `[R, G, B, Alpha]`

### 6) 구분선 (`type: "line"`)
```json
{
  "type": "line",
  "x1": 20,
  "y1": 50,
  "x2": 220,
  "y2": 50,
  "color": [35, 42, 56],
  "width": 1
}
```

### 7) 이미지 / 아이콘 오버레이 (`type: "image"`)
```json
{
  "type": "image",
  "src": "icons/cpu.png",
  "x": 20,
  "y": 230,
  "w": 16,
  "h": 16
}
```

---

## 5. 실시간 동적 변수 토큰 레퍼런스

텍스트 요소(`text`)에 아래 토큰을 작성하면 렌더링 시점에 실시간 센서 값으로 자동 변환됩니다:

### 시간 및 날짜
| 토큰 | 설명 | 예시 출력 |
| :--- | :--- | :--- |
| `%now%` | 현재 시각 (24시간 HH:MM) | `14:30` |
| `%time%` | 현재 시각 (24시간 HH:MM:SS) | `14:30:45` |
| `%hh%` / `%H%` | 시 (24시간 00~23) | `14` |
| `%h12%` / `%I%` | 시 (12시간 01~12) | `02` |
| `%MM%` / `%min%` | 분 (00~59) | `30` |
| `%ss%` / `%sec%` | 초 (00~59) | `45` |
| `%ampm%` | 오전/오후 (AM / PM) | `PM` |
| `%yyyy%` | 연도 4자리 | `2026` |
| `%yy%` | 연도 2자리 | `26` |
| `%mm%` | 월 2자리 (01~12) | `11` |
| `%dd%` | 일 2자리 (01~31) | `13` |
| `%date%` | 전체 날짜 (YYYY.MM.DD) | `2026.11.13` |
| `%day_ko%` | 한국어 요일 | `금` (월~일) |
| `%day_en%` | 영문 요일 | `FRI` (MON~SUN) |

### CPU 하드웨어
| 토큰 | 설명 | 예시 출력 |
| :--- | :--- | :--- |
| `%cpu%` | CPU 실시간 사용률 정수 | `45` |
| `%cpu_float%` | CPU 실시간 사용률 소수점 1자리 | `45.2` |
| `%cpu_ghz%` | CPU 동작 클럭 (GHz) | `4.20` |
| `%cpu_mhz%` | CPU 동작 클럭 (MHz) | `4200` |
| `%cpu_cores%` | CPU 논리 코어(스레드) 수 | `16` |
| `%cpu_cores_phys%` | CPU 물리 코어 수 | `8` |
| `%c_sta%` | CPU 클럭 요약 | `4.20GHz` |

### RAM 하드웨어
| 토큰 | 설명 | 예시 출력 |
| :--- | :--- | :--- |
| `%ram%` | RAM 실시간 사용률 (소수점 1자리) | `48.0` |
| `%ram_int%` | RAM 실시간 사용률 정수 | `48` |
| `%ram_used_gb%` | RAM 사용 용량 (GB) | `15.3GB` |
| `%ram_total_gb%` | RAM 전체 장착 용량 (GB) | `32.0GB` |
| `%ram_free_gb%` | RAM 잔여 용량 (GB) | `16.7GB` |
| `%ram_used_mb%` | RAM 사용 용량 (MB) | `15667` |
| `%ram_total_mb%` | RAM 전체 용량 (MB) | `32768` |
| `%r_sta%` | RAM 요약 문자열 | `15.3GB/32.0GB` |

### DISK (저장장치 C: 드라이브)
| 토큰 | 설명 | 예시 출력 |
| :--- | :--- | :--- |
| `%disk%` | C: 드라이브 사용률 (%) | `62` |
| `%disk_float%` | C: 드라이브 사용률 소수점 (%) | `62.4` |
| `%disk_used_gb%` | 사용 중인 디스크 용량 (GB) | `250GB` |
| `%disk_total_gb%` | 전체 디스크 용량 (GB) | `512GB` |
| `%disk_free_gb%` | 남은 디스크 용량 (GB) | `262GB` |
| `%d_sta%` | 디스크 요약 문자열 | `250GB/512GB` |

### 네트워크 & 시스템 & 스트리밍
| 토큰 | 설명 | 예시 출력 |
| :--- | :--- | :--- |
| `%fps%` | 무선 스트리밍 전송 FPS (소수점 1자리) | `25.0` |
| `%fps_int%` | 무선 스트리밍 전송 FPS 정수 | `25` |
| `%hostname%` | PC 호스트명 | `DESKTOP-GAMING` |
| `%ip%` | PC 로컬 IP 주소 | `192.168.0.24` |

---

## 6. AI 에이전트를 위한 10개 프리셋 테마 자동 생성 지침

다른 AI 에이전트가 10D FCD용 신규 프리셋 테마를 생성할 때는 아래 프롬프트 가이드를 바탕으로 각 테마 폴더에 `theme.json`과 `preview.png`를 정확히 생성해야 합니다.

### 권장 10개 테마 컨셉
1. **`pro_sensor_dark` (고밀도 하드웨어 센서 패널)**: CPU/RAM/DISK/클럭/IP를 세밀한 데이터 그리드로 배치
2. **`racing_tachometer` (슈퍼카 타코미터 HUD)**: 하단 원형 아크 RPM 게이지, 중앙 대형 속도계 폰트로 CPU 표기
3. **`retro_synthwave` (80s 네온 레트로 신스웨이브)**: 마젠타/오렌지 그라데이션, 디지털 와이어프레임 그리드
4. **`cyberpunk_mecha` (사이버펑크 메카 HUD)**: 옐로우/블랙의 인더스트리얼 경고선, 육각형 프레임과 각진 바
5. **`minimal_clean` (미니멀 화이트 클린)**: 극도로 정갈한 타이포그래피, 얇은 선과 대형 시계
6. **`space_warp_core` (SF 우주선 워프 코어 HUD)**: 펄스 링, 코어 안정성(CPU), 에너지 잔량(RAM), 딥 블루 컬러
7. **`arcade_pixel_8bit` (8비트 아케이드 레트로)**: 픽셀 박스, HP 바(CPU)와 MP 바(RAM), 레트로 스테이터스
8. **`scifi_emergency` (SF 비상 경보 오렌지 HUD)**: 헥사곤 경고 박스, 특유의 오렌지 모노크롬, 비상 카운트다운
9. **`matrix_terminal` (그린 매트릭스 터미널)**: 레트로 CRT 모니터 감성 녹색 폰트, 호스트명 및 IP 커맨드라인
10. **`anime_pastel_glow` (애니메 파스텔 글로우)**: 라벤더/민트/핑크 부드러운 네온, 감성적인 원형 게이지

### AI 테마 생성용 프롬프트 템플릿
```text
당신은 10D FCD(ESP32 CYD 2.8" 240x320 Portrait 무선 쿨러 디스플레이)의 전문 UI/UX 테마 디자이너입니다.
'THEME_GUIDE.md'에 명시된 좌표계(240x320)와 토큰 스펙을 준수하여, <테마명> 폴더를 생성하고 유효한 theme.json을 작성하십시오.
반드시 Python PIL 스크립트를 사용하여 240x320 크기의 사실적인 preview.png도 함께 렌더링하여 저장해야 합니다.
```

---

## 7. 테마 검증 및 테스트 방법

신규 생성한 테마는 PC 클라이언트를 실행하지 않고도 아래 스크립트로 즉시 문법 및 렌더링 무결성을 검증할 수 있습니다:

```python
# test_theme_render.py
from pc_client.core.theme_engine import ThemeEngine
from pc_client.core.system_monitor import SystemMonitor

engine = ThemeEngine()
stats = SystemMonitor.get_stats()
for theme in engine.themes:
    engine.current_theme = theme
    img = engine.render_theme_frame(t=1.0, stats=stats, fps_val=25.0)
    assert img.size == (240, 320)
    print(f"Theme '{theme['name']}' Render OK! Size: {img.size}")
```
