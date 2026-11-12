// ESP32-2432S028 (CYD 2.8" ILI9341) - TFT_eSPI User_Setup.h
// Copy this file to: Documents/Arduino/libraries/TFT_eSPI/User_Setup.h

#define USER_SETUP_LOADED

#define ILI9341_2_DRIVER    // CYD 2.8인치 ILI9341 전용 드라이버
// #define ST7789_DRIVER    // 듀얼 USB 포트 신형 CYD 보드 사용 시

#define TFT_MISO 12
#define TFT_MOSI 13
#define TFT_SCLK 14
#define TFT_CS   15
#define TFT_DC    2
#define TFT_RST  -1
#define TFT_BL   21
#define TFT_BACKLIGHT_ON HIGH

#define SPI_FREQUENCY       65000000 // 65MHz 고속 SPI 전송
#define SPI_READ_FREQUENCY  20000000

#define LOAD_GLCD
#define LOAD_FONT2
#define LOAD_FONT4
#define LOAD_FONT6
#define LOAD_FONT7
#define LOAD_FONT8
#define LOAD_GFXFF

