// MoveSense — firmware do nó (um por bracelete: LEFT ou RIGHT)
//
// Hardware: ESP32 (qualquer devkit com I2C) + MPU6050 ou MPU9250 (I2C)
// Libs:     Adafruit_MPU6050 + Adafruit_Sensor (ou MPU9250_asukiaaa se usar o 9250)
//           ESP32 BLE Arduino (embutida no core espressif/arduino-esp32)
//
// O nó expõe um serviço BLE GATT com uma característica NOTIFY que streama
// amostras de IMU (accel + gyro + timestamp) em um pacote binário compacto.
// O hub (celular/PC) conecta nos dois nós (LEFT e RIGHT) e alinha os
// timestamps na coleta — ver analysis/movesense/ para o lado de processamento.

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// ---- Identidade do nó -------------------------------------------------
// Escolhido na gravação, sem editar o código (ver firmware/README.md):
//   arduino-cli compile ... --build-property compiler.cpp.extra_flags=-DNODE_SIDE=RIGHT
// gstack-shortcut(dec-af0824f6): lado definido na gravação em vez de ler pino físico,
// mitigado com identificador pintado no bracelete. Upgrade quando sair do protótipo de bancada.
#ifndef NODE_SIDE
#define NODE_SIDE LEFT
#endif
#define STR_(x) #x
#define STR(x) STR_(x)
#define NODE_SIDE_STR STR(NODE_SIDE)

// I2C do MPU6050 (pinos padrão da maioria das devkits ESP32)
#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22
#define I2C_CLOCK_HZ 400000

#define SERVICE_UUID        "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
#define IMU_CHAR_UUID        "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
#define SYNC_CHAR_UUID       "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

#define SAMPLE_RATE_HZ 100
#define SAMPLE_PERIOD_MS (1000 / SAMPLE_RATE_HZ)

Adafruit_MPU6050 mpu;
BLECharacteristic *imuChar;
BLECharacteristic *syncChar;
// escrito no callback BLE, lido no loop() (tasks diferentes no ESP32)
volatile bool deviceConnected = false;

// Pacote binário: 2 bytes seq_num + 4 bytes timestamp_ms + 6x float (ax,ay,az,gx,gy,gz) = 30 bytes
// Requer MTU negociado acima do padrão de 23 bytes (ver setupBLE) — sem isso
// o ESP32 BLE Arduino trunca notify() em 20 bytes de payload, silenciosamente.
struct __attribute__((packed)) ImuSample {
  uint16_t seq_num;    // incrementa a cada amostra, wrap em 65535 (~655s a 100Hz) — detecta gap de notify no hub
  uint32_t timestamp_ms;
  float ax, ay, az;   // m/s^2
  float gx, gy, gz;   // rad/s
};

// Pong do sync de relógio: hub escreve [uint16 ping_id]; o nó responde por notify
// [uint16 ping_id, uint32 node_rx_ms], com node_rx_ms = millis() capturado no
// primeiro instante do callback. Formato espelhado em analysis/movesense/clock_sync.py.
struct __attribute__((packed)) SyncPong {
  uint16_t ping_id;
  uint32_t node_rx_ms;
};

class SyncCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *characteristic) override {
    uint32_t rx = millis();  // antes de qualquer outra coisa: é isso que o hub mede
    String value = characteristic->getValue();
    if (value.length() != sizeof(uint16_t)) return;
    SyncPong pong;
    memcpy(&pong.ping_id, value.c_str(), sizeof(uint16_t));
    pong.node_rx_ms = rx;
    syncChar->setValue((uint8_t *)&pong, sizeof(pong));
    syncChar->notify();
  }
};

class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *server) override { deviceConnected = true; }
  void onDisconnect(BLEServer *server) override {
    deviceConnected = false;
    server->getAdvertising()->start(); // volta a anunciar após desconectar
  }
  // setMTU() só pede a negociação — sem logar o valor real aceito pelo
  // central, uma queda pro padrão de 23 bytes volta a truncar notify()
  // silenciosamente (o mesmo bug que essa revisão corrigiu).
  void onMtuChanged(BLEServer *server, esp_ble_gatts_cb_param_t *param) override {
    Serial.printf("MTU negociado: %d bytes\n", param->mtu.mtu);
  }
};

// gstack-shortcut(dec-b3253f71): negocia MTU pra cima em vez de encolher o
// pacote ou fragmentar. Central (hub) precisa aceitar a negociação — se não
// aceitar, notify() volta a truncar em 20 bytes silenciosamente.
#define DESIRED_MTU 247

void setupBLE() {
  BLEDevice::setMTU(DESIRED_MTU);
  BLEDevice::init(String("MoveSense-") + NODE_SIDE_STR);
  BLEServer *server = BLEDevice::createServer();
  server->setCallbacks(new ServerCallbacks());

  BLEService *service = server->createService(SERVICE_UUID);
  imuChar = service->createCharacteristic(
      IMU_CHAR_UUID,
      BLECharacteristic::PROPERTY_NOTIFY
  );
  imuChar->addDescriptor(new BLE2902());

  syncChar = service->createCharacteristic(
      SYNC_CHAR_UUID,
      BLECharacteristic::PROPERTY_WRITE_NR | BLECharacteristic::PROPERTY_NOTIFY
  );
  syncChar->addDescriptor(new BLE2902());
  syncChar->setCallbacks(new SyncCallbacks());
  service->start();

  server->getAdvertising()->addServiceUUID(SERVICE_UUID);
  server->getAdvertising()->start();
}

#define STATUS_LED_PIN 2  // LED onboard na maioria das devkits ESP32

void setupIMU() {
  if (!mpu.begin()) {
    Serial.println("Falha ao inicializar o MPU6050 — checar fiação I2C (SDA/SCL) e endereço.");
    pinMode(STATUS_LED_PIN, OUTPUT);
    while (true) {
      digitalWrite(STATUS_LED_PIN, HIGH);
      delay(200);
      digitalWrite(STATUS_LED_PIN, LOW);
      delay(200);
    }
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_1000_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_44_HZ);
}

void setup() {
  Serial.begin(115200);
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, I2C_CLOCK_HZ);
  setupIMU();
  setupBLE();
  Serial.printf("MoveSense node [%s] pronto.\n", NODE_SIDE_STR);
}

void loop() {
  static uint32_t lastSample = 0;
  static uint16_t seq = 0;
  uint32_t now = millis();
  if (now - lastSample < SAMPLE_PERIOD_MS) return;
  // avança em passos fixos de período (sem perder a fase a cada iteração do loop);
  // se atrasou mais de 1 período (I2C/BLE travou), ressincroniza em vez de rajada
  lastSample += SAMPLE_PERIOD_MS;
  if (now - lastSample >= SAMPLE_PERIOD_MS) lastSample = now;

  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  ImuSample sample;
  sample.seq_num = seq++;
  sample.timestamp_ms = now;
  sample.ax = accel.acceleration.x;
  sample.ay = accel.acceleration.y;
  sample.az = accel.acceleration.z;
  sample.gx = gyro.gyro.x;
  sample.gy = gyro.gyro.y;
  sample.gz = gyro.gyro.z;

  if (deviceConnected) {
    imuChar->setValue((uint8_t *)&sample, sizeof(sample));
    imuChar->notify();
  }
}
