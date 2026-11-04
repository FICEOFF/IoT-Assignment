#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>
#include <Adafruit_SHT31.h>

static const u1_t PROGMEM APPEUI[8] = {  }; // Join EUI
void os_getArtEui(u1_t* buf) { memcpy_P(buf, APPEUI, 8); }

static const u1_t PROGMEM DEVEUI[8] = {  }; // Device EUI
void os_getDevEui(u1_t* buf) { memcpy_P(buf, DEVEUI, 8); }

static const u1_t PROGMEM APPKEY[16] = {  }; // App Key
void os_getDevKey(u1_t* buf) { memcpy_P(buf, APPKEY, 16); }

const unsigned TX_INTERVAL = 10;

const lmic_pinmap lmic_pins = {
    .nss = 10,
    .rxtx = LMIC_UNUSED_PIN,
    .rst = 7,
    .dio = {2, 5, 6}
};

static osjob_t sendjob;

void do_send(osjob_t* j);
Adafruit_SHT31 sht31 = Adafruit_SHT31();

void scheduleNext() {
    os_setTimedCallback(&sendjob, os_getTime() + sec2osticks(TX_INTERVAL), do_send);
}

void onEvent(ev_t ev) {
    switch (ev) {
        case EV_JOINING:
            Serial.println(F("EV_JOINING"));
            break;
        case EV_JOINED:
            Serial.println(F("EV_JOINED"));
            LMIC_setLinkCheckMode(0);
            break;
        case EV_JOIN_FAILED:
            Serial.println(F("EV_JOIN_FAILED"));
            break;
        case EV_TXCOMPLETE:
            Serial.println(F("EV_TXCOMPLETE"));
            scheduleNext();
            break;
        default:
            break;
    }
}

void do_send(osjob_t* j) {
    if (LMIC.opmode & OP_TXRXPEND) {
        Serial.println(F("OP_TXRXPEND, not sending"));
        return;
    }
    float t = sht31.readTemperature();
    float h = sht31.readHumidity();
    if (isnan(t) || isnan(h)) {
        Serial.println(F("SHT31 read failed"));
        scheduleNext();
        return;
    }
    uint16_t temp = (uint16_t)(int16_t)lroundf(t * 100);
    uint16_t humid = (uint16_t)lroundf(h * 100);
    uint8_t payload[4] = {
        (uint8_t)(temp >> 8), (uint8_t)(temp & 0xFF),
        (uint8_t)(humid >> 8), (uint8_t)(humid & 0xFF)
    };
    LMIC_setTxData2(1, payload, sizeof(payload), 0);
    Serial.print(F("Packet queued: "));
    Serial.print(t, 1);
    Serial.print(F(" C, "));
    Serial.print(h, 1);
    Serial.println(F(" %"));
}

void setup() {
    Serial.begin(9600);
    if (!sht31.begin(0x44)) {
        Serial.println(F("SHT31 not found"));
        while (1) {
            delay(1000);
        }
    }
    os_init();
    LMIC_reset();
    LMIC_setupChannel(0, 923200000, DR_RANGE_MAP(DR_SF12, DR_SF7), BAND_CENTI);
    LMIC_setDrTxpow(DR_SF12, 14);
    do_send(&sendjob);
}

void loop() {
    os_runloop_once();
}
