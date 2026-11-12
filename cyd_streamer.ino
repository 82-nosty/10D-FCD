#include <WiFi.h>
#include <SPI.h>
#include <TFT_eSPI.h>
#include <TJpg_Decoder.h>
#include <Preferences.h>
#include <time.h>
#include "korean_font.h"
#include "clock_font.h"

// =========================================================================
// 10D FCD - FAN COOLER DISPLAY (240x320 PORTRAIT, DUAL LANGUAGE: KO / EN)
// =========================================================================

TFT_eSPI tft = TFT_eSPI();
WiFiServer streamServer(8888);
Preferences prefs;

// 240x320 고화질 4:4:4 프레임 더블 버퍼 (동적 힙 할당으로 각 48KB 확보)
#define MAX_FRAME_SIZE 49152
uint8_t* frameBufferA = nullptr;
uint8_t* frameBufferB = nullptr;

volatile uint8_t* activeRecvBuffer = nullptr;
volatile uint8_t* activeRenderBuffer = nullptr;
volatile uint32_t readyFrameSize = 0;
volatile bool newFrameAvailable = false;
volatile bool isRenderingJpg = false;
volatile bool isStreamingActive = false;

// 언어 모드: KO(0, 기본값), EN(1)
enum LanguageMode {
  LANG_KO = 0,
  LANG_EN = 1
};
LanguageMode currentLang = LANG_KO;
bool isFlipped180 = false; // 180도 화면 회전 (NVS 영구 보존)
int lastClockMin = -2;
LanguageMode lastClockLang = LANG_KO;
uint32_t lastClockTick = 0;
uint32_t lastPcActiveTime = 0;
bool isPcConnected = false;

// 물리적 잔상(Image Sticking/Burn-in) 방지: 백라이트 PWM 제어 규격 (ESP32 Arduino 3.x 지원)
#define BL_FREQ           5000
#define BL_RES            8
#define BL_BRIGHT_STREAM  255  // 100% (스트리밍 시 최고 화질)
#define BL_BRIGHT_STANDBY 90   // ~35% (대기 시계 화면 시 발열/전하 고착 방지)
uint8_t currentBacklight = 255;

void setBacklight(uint8_t brightness) {
  if (currentBacklight != brightness) {
    currentBacklight = brightness;
    ledcWrite(TFT_BL, brightness);
  }
}

// 리얼 블랙 다크모드 색상
#define COLOR_BG        0x0000  // Pure Black
#define COLOR_CYAN      0x07FF  // Crisp Cyan
#define COLOR_YELLOW    0xFFE0  // Gold Yellow
#define COLOR_GREEN     0x07E0  // Emerald Green
#define COLOR_RED       0xF800  // Bright Red
#define COLOR_WHITE     0xFFFF  // Pure White
#define COLOR_MUTED     0x8410  // Mid Slate Grey
#define COLOR_LINE      0x18E3  // Minimal Divider

bool tft_output(int16_t x, int16_t y, uint16_t w, uint16_t h, uint16_t* bitmap) {
  if (y >= tft.height()) return 0;
  tft.pushImage(x, y, w, h, bitmap);
  return 1;
}

void renderTask(void* pvParameters) {
  while (true) {
    if (newFrameAvailable && readyFrameSize > 0) {
      isStreamingActive = true;
      isRenderingJpg = true;
      newFrameAvailable = false;
      tft.startWrite();
      TJpgDec.drawJpg(0, 0, (const uint8_t*)activeRenderBuffer, readyFrameSize);
      tft.endWrite();
      isRenderingJpg = false;
    } else {
      vTaskDelay(1);
    }
  }
}

// =========================================================================
// 볼드 한글 렌더러
// =========================================================================
void drawKoreanGlyphScaled(int x, int y, uint16_t code, uint16_t color, uint16_t bg, int scale) {
  for (int i = 0; i < HAN_FONT_COUNT; ++i) {
    if (pgm_read_word(&HAN_FONTS[i].code) == code) {
      for (int row = 0; row < 16; ++row) {
        uint8_t b1 = pgm_read_byte(&HAN_FONTS[i].data[row * 2]);
        uint8_t b2 = pgm_read_byte(&HAN_FONTS[i].data[row * 2 + 1]);

        for (int col = 0; col < 8; ++col) {
          if (b1 & (1 << (7 - col))) {
            if (scale == 1) tft.drawPixel(x + col, y + row, color);
            else tft.fillRect(x + col * scale, y + row * scale, scale, scale, color);
          } else if (bg != 0) {
            if (scale == 1) tft.drawPixel(x + col, y + row, bg);
            else tft.fillRect(x + col * scale, y + row * scale, scale, scale, bg);
          }
        }
        for (int col = 0; col < 8; ++col) {
          if (b2 & (1 << (7 - col))) {
            if (scale == 1) tft.drawPixel(x + 8 + col, y + row, color);
            else tft.fillRect(x + (8 + col) * scale, y + row * scale, scale, scale, color);
          } else if (bg != 0) {
            if (scale == 1) tft.drawPixel(x + 8 + col, y + row, bg);
            else tft.fillRect(x + (8 + col) * scale, y + row * scale, scale, scale, bg);
          }
        }
      }
      return;
    }
  }
}

void drawKoreanStringScaled(int x, int y, const String& text, uint16_t color, uint16_t bg, int scale = 1) {
  int curX = x;
  int len = text.length();
  int idx = 0;

  while (idx < len) {
    uint8_t c1 = (uint8_t)text[idx];
    if (c1 < 0x80) {
      if (c1 == ' ') {
        curX += 6 * scale;
      } else {
        // 영문 알파벳/숫자는 TFT 표준 폰트로 정확하고 또렷하게 출력
        // TFT_eSPI의 drawChar 시그니처: drawChar(int32_t x, int32_t y, uint16_t c, uint32_t color, uint32_t bg, uint8_t size)
        tft.drawChar(curX, y, (uint16_t)c1, color, bg, scale * 2);
        curX += 12 * scale;
      }
      idx++;
    } else if ((c1 & 0xE0) == 0xE0 && idx + 2 < len) {
      uint8_t c2 = (uint8_t)text[idx + 1];
      uint8_t c3 = (uint8_t)text[idx + 2];
      uint16_t unicode = ((c1 & 0x0F) << 12) | ((c2 & 0x3F) << 6) | (c3 & 0x3F);

      drawKoreanGlyphScaled(curX, y, unicode, color, bg, scale);
      curX += (16 + 1) * scale;
      idx += 3;
    } else {
      idx++;
    }
  }
}

int measureKoreanStringWidth(const String& text, int scale = 1) {
  int w = 0;
  int len = text.length();
  int idx = 0;
  while (idx < len) {
    uint8_t c1 = (uint8_t)text[idx];
    if (c1 < 0x80) {
      w += (c1 == ' ') ? (6 * scale) : (12 * scale);
      idx++;
    } else if ((c1 & 0xE0) == 0xE0 && idx + 2 < len) {
      w += 17 * scale;
      idx += 3;
    } else {
      idx++;
    }
  }
  return w;
}

void drawCenteredKorean(int y, const String& text, uint16_t color, uint16_t bg, int scale = 1) {
  int w = measureKoreanStringWidth(text, scale);
  int x = max(0, (240 - w) / 2);
  drawKoreanStringScaled(x, y, text, color, bg, scale);
}

void drawLargeDigit(int x, int y, int digit, uint16_t color, uint16_t bg) {
  if (digit < 0 || digit > 9) return;
  const uint8_t* ptr = CLOCK_DIGITS[digit];
  tft.startWrite();
  tft.setWindow(x, y, x + CLOCK_DIGIT_W - 1, y + CLOCK_DIGIT_H - 1);
  for (int r = 0; r < CLOCK_DIGIT_H; ++r) {
    for (int c = 0; c < CLOCK_DIGIT_W; ++c) {
      uint8_t b = pgm_read_byte(ptr + r * 7 + (c / 8));
      if (b & (1 << (7 - (c % 8)))) {
        tft.pushColor(color);
      } else {
        tft.pushColor(bg);
      }
    }
  }
  tft.endWrite();
}

void drawLargeNumber2(int y, int num, uint16_t color, uint16_t bg) {
  int d1 = (num / 10) % 10;
  int d2 = num % 10;
  int gap = 8;
  int totalW = CLOCK_DIGIT_W * 2 + gap; // 56 * 2 + 8 = 120
  int startX = (240 - totalW) / 2;     // 60
  drawLargeDigit(startX, y, d1, color, bg);
  drawLargeDigit(startX + CLOCK_DIGIT_W + gap, y, d2, color, bg);
}

// =========================================================================
// 와이파이 연결 + PC 미연결/꺼짐 상태: 세로 대형 시계 (92px 초고화질 시계 + 기기 연결 안됨 2x)
// 물리적 잔상(Burn-in/Image Sticking) 방지: 픽셀 쉬프트(오비팅) + 스마트 백라이트 디밍
// =========================================================================
void showClockStandbyUI(bool forceRedraw) {
  setBacklight(BL_BRIGHT_STANDBY); // 대기 모드 진입 시 밝기 35%로 디밍 (잔류 전하 방지)

  struct tm timeinfo;
  bool hasTime = getLocalTime(&timeinfo, 5);
  int curMin = hasTime ? (timeinfo.tm_hour * 60 + timeinfo.tm_min) : -1;

  if (!forceRedraw && curMin == lastClockMin && currentLang == lastClockLang) {
    return;
  }
  lastClockMin = curMin;
  lastClockLang = currentLang;

  // 픽셀 쉬프트 (오비팅): 1분마다 X, Y 좌표를 8방향으로 미세 이동(-2px ~ +2px)
  // 고정 픽셀이 지속적으로 켜져 생기는 액정 고착을 원천 방지
  int shiftIndex = (curMin >= 0 ? curMin : (int)(millis() / 60000)) % 8;
  const int shiftX[8] = { 0,  2,  1, -1, -2, -1,  1,  0 };
  const int shiftY[8] = { 0,  1,  2,  1, -1, -2, -1,  0 };
  int ox = shiftX[shiftIndex];
  int oy = shiftY[shiftIndex];

  tft.fillScreen(COLOR_BG);

  if (hasTime) {
    drawLargeNumber2(12 + oy, timeinfo.tm_hour, COLOR_WHITE, COLOR_BG);
    drawLargeNumber2(112 + oy, timeinfo.tm_min, COLOR_CYAN, COLOR_BG);
  } else {
    tft.setTextDatum(TC_DATUM);
    tft.setTextColor(COLOR_WHITE, COLOR_BG);
    tft.drawString("--", 120 + ox, 36 + oy, 8);
    tft.setTextColor(COLOR_CYAN, COLOR_BG);
    tft.drawString("--", 120 + ox, 120 + oy, 8);
  }

  tft.drawFastHLine(20 + ox, 216 + oy, 200, COLOR_LINE);

  if (currentLang == LANG_KO) {
    // 32px 대형 볼드 한글 메시지 (오비팅 좌표 반영)
    int w = measureKoreanStringWidth("기기 연결 안됨", 2);
    int x = max(0, (240 - w) / 2) + ox;
    drawKoreanStringScaled(x, 230 + oy, "기기 연결 안됨", COLOR_MUTED, COLOR_BG, 2);
  } else {
    tft.setTextDatum(TC_DATUM);
    tft.setTextColor(COLOR_MUTED, COLOR_BG);
    tft.drawString("PC Disconnected", 120 + ox, 234 + oy, 4);
  }

  tft.setTextDatum(TC_DATUM);
  tft.setTextColor(0x4208, COLOR_BG);
  tft.drawString(WiFi.localIP().toString(), 120 + ox, 285 + oy, 2);
  tft.setTextDatum(TL_DATUM);
}

// =========================================================================
// 와이파이 미연결 상태: 경고 아이콘 + 기기 셋업을 진행해주세요.
// =========================================================================
void showSetupNeededUI() {
  setBacklight(BL_BRIGHT_STREAM);
  tft.fillScreen(COLOR_BG);

  // 노란색 경고 삼각형 + 느낌표(!)
  tft.fillTriangle(120, 68, 82, 132, 158, 132, COLOR_YELLOW);
  tft.fillRect(117, 86, 6, 24, COLOR_BG);
  tft.fillRect(117, 116, 6, 6, COLOR_BG);

  if (currentLang == LANG_KO) {
    drawCenteredKorean(164, "기기 셋업을", COLOR_WHITE, COLOR_BG, 1);
    drawCenteredKorean(192, "진행해주세요.", COLOR_WHITE, COLOR_BG, 1);
  } else {
    tft.setTextDatum(TC_DATUM);
    tft.setTextColor(COLOR_WHITE, COLOR_BG);
    tft.drawString("Please run", 120, 162, 4);
    tft.drawString("device setup.", 120, 192, 4);
    tft.setTextDatum(TL_DATUM);
  }
}

// =========================================================================
// 10D FCD 진행 중 상태 화면 (검색 / 접속 시도용)
// =========================================================================
void showStandbyUI(const String& statusEn, const String& statusKo, const String& ipStr) {
  setBacklight(BL_BRIGHT_STREAM);
  tft.fillScreen(COLOR_BG);

  // 1. 헤더: 10D FCD 타이틀 + 언어 인디케이터
  tft.setTextColor(COLOR_CYAN, COLOR_BG);
  tft.setTextSize(3);
  tft.drawString("10D FCD", 20, 16);

  tft.setTextColor(COLOR_MUTED, COLOR_BG);
  tft.setTextSize(2);
  if (currentLang == LANG_KO) {
    tft.drawString("KO", 195, 22);
  } else {
    tft.drawString("EN", 195, 22);
  }

  tft.drawFastHLine(20, 48, 200, COLOR_CYAN);

  // 2. 연결 상태
  tft.setTextColor(COLOR_MUTED, COLOR_BG);
  tft.setTextSize(1);
  if (currentLang == LANG_KO) {
    drawKoreanStringScaled(20, 64, "연결 상태", COLOR_MUTED, COLOR_BG, 1);
    drawKoreanStringScaled(20, 88, statusKo, COLOR_YELLOW, COLOR_BG, 1);
  } else {
    tft.drawString("CONNECTION STATUS", 20, 64);
    tft.setTextColor(COLOR_YELLOW, COLOR_BG);
    tft.setTextSize(2);
    tft.drawString(statusEn, 20, 86);
  }

  tft.drawFastHLine(20, 126, 200, COLOR_LINE);

  // 3. 무선 IP 주소
  tft.setTextColor(COLOR_MUTED, COLOR_BG);
  tft.setTextSize(1);
  if (currentLang == LANG_KO) {
    drawKoreanStringScaled(20, 142, "무선 네트워크 IP", COLOR_MUTED, COLOR_BG, 1);
  } else {
    tft.drawString("WIRELESS TCP IP", 20, 142);
  }

  tft.setTextColor(COLOR_WHITE, COLOR_BG);
  tft.setTextSize(3);
  tft.drawString(ipStr, 20, 168);

  tft.setTextColor(COLOR_GREEN, COLOR_BG);
  tft.setTextSize(2);
  tft.drawString("PORT: 8888", 20, 210);

  tft.drawFastHLine(20, 246, 200, COLOR_LINE);

  // 4. 하단 미니멀 상태 표시
  tft.setTextColor(COLOR_GREEN, COLOR_BG);
  tft.setTextSize(1);
  if (currentLang == LANG_KO) {
    drawKoreanStringScaled(20, 266, "스트리밍 대기 중", COLOR_GREEN, COLOR_BG, 1);
  } else {
    tft.drawString("STANDBY FOR STREAM", 20, 266);
  }

  tft.setTextColor(COLOR_MUTED, COLOR_BG);
  tft.drawString("10D FCD v2.1.8", 20, 296);
}

void applyRotation() {
  tft.setRotation(isFlipped180 ? 2 : 0); // 0: 세로 정방향, 2: 180도 반전 세로
}

void loadPreferences() {
  prefs.begin("fcd_store", false);
  int l = prefs.getInt("lang", 0);
  currentLang = (l == 1) ? LANG_EN : LANG_KO;
  isFlipped180 = prefs.getBool("flip", false);
  prefs.end();
  applyRotation();
}

void saveLanguage(LanguageMode mode) {
  currentLang = mode;
  prefs.begin("fcd_store", false);
  prefs.putInt("lang", (int)mode);
  prefs.end();
}

void saveFlipMode(bool flip) {
  isFlipped180 = flip;
  prefs.begin("fcd_store", false);
  prefs.putBool("flip", isFlipped180);
  prefs.end();
  applyRotation();
}

void checkWifiAndInit() {
  prefs.begin("wifi_store", true);
  String savedSsid = prefs.getString("ssid", "");
  String savedPass = prefs.getString("pass", "");
  prefs.end();

  if (savedSsid.length() > 0) {
    showStandbyUI("Connecting...", "와이파이 연결 중", savedSsid);
    WiFi.disconnect(true);
    delay(100);
    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);
    WiFi.begin(savedSsid.c_str(), savedPass.c_str());

    int timeout = 30;
    while (WiFi.status() != WL_CONNECTED && timeout > 0) {
      delay(500);
      timeout--;
    }

    if (WiFi.status() == WL_CONNECTED) {
      configTime(9 * 3600, 0, "pool.ntp.org", "time.google.com");
      streamServer.begin();
      showClockStandbyUI(true);
      return;
    }
  }

  showSetupNeededUI();
}

void saveWifi(const String& ssid, const String& pass) {
  prefs.begin("wifi_store", false);
  prefs.putString("ssid", ssid);
  prefs.putString("pass", pass);
  prefs.end();
}

void refreshCurrentUI() {
  if (WiFi.status() == WL_CONNECTED) {
    if (isPcConnected || (millis() - lastPcActiveTime < 15000)) {
      showStandbyUI("Ready", "컴퓨터 연결 대기 중", WiFi.localIP().toString());
    } else {
      showClockStandbyUI(true);
    }
  } else {
    showSetupNeededUI();
  }
}

void setup() {
  Serial.begin(921600);
  Serial.setRxBufferSize(32768);

  frameBufferA = (uint8_t*)malloc(MAX_FRAME_SIZE);
  frameBufferB = (uint8_t*)malloc(MAX_FRAME_SIZE);
  activeRecvBuffer = frameBufferA;
  activeRenderBuffer = frameBufferB;

  // 백라이트 하드웨어 PWM 설정 (ESP32 3.x 신형 API: 물리적 잔상 및 발열 방지)
  ledcAttach(TFT_BL, BL_FREQ, BL_RES);
  setBacklight(BL_BRIGHT_STREAM);

  tft.init();
  loadPreferences(); // NVS에서 언어 및 180도 회전 설정 복원 (모든 부팅/대기/에러 화면에 즉시 적용)
  tft.invertDisplay(true); // 리얼 다크모드 보정
  tft.setSwapBytes(false);
  tft.fillScreen(COLOR_BG);

  TJpgDec.setJpgScale(1);
  TJpgDec.setSwapBytes(true);
  TJpgDec.setCallback(tft_output);

  loadPreferences();
  checkWifiAndInit();

  xTaskCreatePinnedToCore(
    renderTask,
    "RenderTask",
    8192,
    NULL,
    3,
    NULL,
    1
  );

  Serial.println("10D_FCD_ONLINE");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    lastPcActiveTime = millis();
    isPcConnected = true;

    // 언어 전환 명령어
    if (cmd == "SET_LANG:KO") {
      saveLanguage(LANG_KO);
      refreshCurrentUI();
      Serial.println("LANG_SET:KO");
    }
    else if (cmd == "SET_LANG:EN") {
      saveLanguage(LANG_EN);
      refreshCurrentUI();
      Serial.println("LANG_SET:EN");
    }
    else if (cmd == "GET_LANG") {
      Serial.println(currentLang == LANG_KO ? "LANG:KO" : "LANG:EN");
    }
    // 180도 화면 회전 (NVS 영구 보존) 명령어
    else if (cmd == "SET_FLIP:1") {
      saveFlipMode(true);
      refreshCurrentUI();
      Serial.println("FLIP_SET:1");
    }
    else if (cmd == "SET_FLIP:0") {
      saveFlipMode(false);
      refreshCurrentUI();
      Serial.println("FLIP_SET:0");
    }
    else if (cmd == "GET_FLIP") {
      Serial.println(isFlipped180 ? "FLIP:1" : "FLIP:0");
    }
    else if (cmd == "GET_IP") {
      if (WiFi.status() == WL_CONNECTED) {
        Serial.println("WIFI_IP:" + WiFi.localIP().toString());
      } else {
        Serial.println("WIFI_IP:0.0.0.0");
      }
    }
    else if (cmd == "SCAN") {
      showStandbyUI("Scanning...", "주변 와이파이 검색 중", "Please wait...");
      WiFi.disconnect();
      delay(50);
      WiFi.mode(WIFI_STA);

      int n = WiFi.scanNetworks(false, true);
      String result = "SCAN_RESULT:";
      for (int i = 0; i < n; ++i) {
        String s = WiFi.SSID(i);
        if (s.length() > 0) {
          result += s;
          if (i < n - 1) result += ",";
        }
      }
      WiFi.scanDelete();
      Serial.println(result);
      showStandbyUI("Scan Done", "검색 완료", "Found " + String(n) + " APs");
    }
    else if (cmd.startsWith("CONNECT:")) {
      int comma = cmd.indexOf(',', 8);
      if (comma != -1) {
        String ssid = cmd.substring(8, comma);
        String pass = cmd.substring(comma + 1);

        showStandbyUI("Connecting...", "공유기 접속 시도 중", ssid);
        WiFi.disconnect(true);
        delay(100);
        WiFi.mode(WIFI_STA);
        WiFi.setSleep(false);
        WiFi.begin(ssid.c_str(), pass.c_str());

        int timeout = 40;
        while (WiFi.status() != WL_CONNECTED && timeout > 0) {
          delay(500);
          timeout--;
        }

        if (WiFi.status() == WL_CONNECTED) {
          saveWifi(ssid, pass);
          configTime(9 * 3600, 0, "pool.ntp.org", "time.google.com");
          streamServer.begin();
          String ipStr = WiFi.localIP().toString();
          showClockStandbyUI(true);
          Serial.println("WIFI_CONNECTED:" + ipStr);
        } else {
          showSetupNeededUI();
          Serial.println("WIFI_FAIL");
        }
      }
    }
  }

  WiFiClient client = streamServer.available();
  if (client) {
    client.setNoDelay(true);
    setBacklight(BL_BRIGHT_STREAM); // 스트리밍 활성화 시 100% 최고 밝기 복원
    // PC 연결 완료 시 대형 시계 대신 기존 대시보드 UI를 띄움
    showStandbyUI("Connected", "컴퓨터 연결됨 (대기)", WiFi.localIP().toString());

    uint8_t header[8];
    while (client.connected()) {
      int bytesRead = 0;
      uint32_t headerTimeout = millis();
      while (bytesRead < 8 && client.connected()) {
        if (client.available()) {
          header[bytesRead++] = client.read();
          headerTimeout = millis();
        } else {
          if (bytesRead == 0) {
            // 스트리밍 대기 중 유휴 상태 유지
            delay(2);
            headerTimeout = millis();
          } else {
            if (millis() - headerTimeout > 1000) break;
            delayMicroseconds(50);
          }
        }
      }

      if (bytesRead < 8) break;

      uint32_t frameLen = ((uint32_t)header[4] << 24) |
                          ((uint32_t)header[5] << 16) |
                          ((uint32_t)header[6] << 8)  |
                          ((uint32_t)header[7]);

      // 1. 무손실 RAW RGB565 스트리밍 ('VRAW', 153600 bytes)
      if (header[0] == 'V' && header[1] == 'R' && header[2] == 'A' && header[3] == 'W') {
        if (frameLen != 153600) continue;
        while (newFrameAvailable || isRenderingJpg) delayMicroseconds(100);

        const int LINES_PER_CHUNK = 40;
        const int CHUNK_BYTES = 240 * LINES_PER_CHUNK * 2; // 19200 bytes (8 chunks)
        bool ok = true;
        tft.setSwapBytes(true); // Python Little-Endian(<u2) RGB565 매칭
        for (int y = 0; y < 320; y += LINES_PER_CHUNK) {
          int got = 0;
          uint32_t rt = millis();
          while (got < CHUNK_BYTES && client.connected()) {
            int avail = client.available();
            if (avail > 0) {
              int n = client.read((uint8_t*)(activeRecvBuffer + got), min(avail, CHUNK_BYTES - got));
              if (n > 0) {
                got += n;
                rt = millis();
              }
            } else {
              if (millis() - rt > 1500) { ok = false; break; }
              delayMicroseconds(50);
            }
          }
          if (!ok || got < CHUNK_BYTES) { ok = false; break; }
          tft.pushImage(0, y, 240, LINES_PER_CHUNK, (uint16_t*)activeRecvBuffer);
        }
        tft.setSwapBytes(false); // TJpgDec용 기본값 복원
        if (ok) client.write('K');
        continue;
      }

      // 2. 실시간 제어 명령 패킷 ('VCMD', e.g. FLIP:1, FLIP:0, LANG:KO)
      if (header[0] == 'V' && header[1] == 'C' && header[2] == 'M' && header[3] == 'D') {
        if (frameLen > 0 && frameLen < 64) {
          char cmdBuf[64];
          int got = 0;
          uint32_t rt = millis();
          while (got < frameLen && client.connected()) {
            if (client.available()) {
              cmdBuf[got++] = (char)client.read();
              rt = millis();
            } else {
              if (millis() - rt > 1000) break;
              delayMicroseconds(50);
            }
          }
          cmdBuf[got] = '\0';
          String c(cmdBuf);
          c.trim();
          if (c == "FLIP:1") {
            saveFlipMode(true);
          } else if (c == "FLIP:0") {
            saveFlipMode(false);
          } else if (c == "LANG:KO") {
            saveLanguage(LANG_KO);
          } else if (c == "LANG:EN") {
            saveLanguage(LANG_EN);
          }
          client.write('K');
        }
        continue;
      }

      if (header[0] != 'V' || header[1] != 'L' || header[2] != 'I' || header[3] != 'F') {
        continue;
      }

      if (frameLen == 0 || frameLen > MAX_FRAME_SIZE) {
        continue;
      }

      uint32_t payloadRead = 0;
      uint32_t readTimeout = millis();
      while (payloadRead < frameLen && client.connected()) {
        int avail = client.available();
        if (avail > 0) {
          int toRead = min(avail, (int)(frameLen - payloadRead));
          int actual = client.read((uint8_t*)(activeRecvBuffer + payloadRead), toRead);
          if (actual > 0) {
            payloadRead += actual;
            readTimeout = millis();
          }
        } else {
          if (millis() - readTimeout > 1500) break;
          delayMicroseconds(50);
        }
      }

      if (payloadRead != frameLen) {
        break;
      }

      while (newFrameAvailable) {
        delayMicroseconds(100);
      }

      volatile uint8_t* temp = activeRecvBuffer;
      activeRecvBuffer = activeRenderBuffer;
      activeRenderBuffer = temp;

      readyFrameSize = frameLen;
      newFrameAvailable = true;

      // PC에게 다음 프레임 수신 준비 완료(ACK) 전송
      client.write('K');
    }
    client.stop();
    isPcConnected = false;
    refreshCurrentUI();
  }

  // PC 미연결/꺼짐 상태(최근 15초 이상 PC 통신 없음)에서만 1초마다 NTP 시계 자동 갱신
  if (WiFi.status() == WL_CONNECTED && !isPcConnected && (millis() - lastPcActiveTime >= 15000)) {
    if (millis() - lastClockTick >= 1000) {
      lastClockTick = millis();
      showClockStandbyUI(false);
    }
  }

  delay(2);
}
