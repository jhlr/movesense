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
// Trocar por bracelete: LEFT no nó esquerdo, RIGHT no nó direito.
#define NODE_SIDE "LEFT"

#define SERVICE_UUID        "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
#define IMU_CHAR_UUID        "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

#define SAMPLE_RATE_HZ 100
#define SAMPLE_PERIOD_MS (1000 / SAMPLE_RATE_HZ)

Adafruit_MPU6050 mpu;
BLECharacteristic *imuChar;
bool deviceConnected = false;

// Pacote binário: 4 bytes timestamp_ms + 6x float (ax,ay,az,gx,gy,gz) = 28 bytes
struct __attribute__((packed)) ImuSample {
  uint32_t timestamp_ms;
  float ax, ay, az;   // m/s^2
  float gx, gy, gz;   // rad/s
};

class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *server) override { deviceConnected = true; }
  void onDisconnect(BLEServer *server) override {
    deviceConnected = false;
    server->getAdvertising()->start(); // volta a anunciar após desconectar
  }
};

void setupBLE() {
  BLEDevice::init(String("MoveSense-") + NODE_SIDE);
  BLEServer *server = BLEDevice::createServer();
  server->setCallbacks(new ServerCallbacks());

  BLEService *service = server->createService(SERVICE_UUID);
  imuChar = service->createCharacteristic(
      IMU_CHAR_UUID,
      BLECharacteristic::PROPERTY_NOTIFY
  );
  imuChar->addDescriptor(new BLE2902());
  service->start();

  server->getAdvertising()->addServiceUUID(SERVICE_UUID);
  server->getAdvertising()->start();
}

void setupIMU() {
  if (!mpu.begin()) {
    Serial.println("Falha ao inicializar o MPU6050 — checar fiação I2C (SDA/SCL) e endereço.");
    while (true) delay(1000);
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_1000_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_44_HZ);
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  setupIMU();
  setupBLE();
  Serial.printf("MoveSense node [%s] pronto.\n", NODE_SIDE);
}

void loop() {
  static uint32_t lastSample = 0;
  uint32_t now = millis();
  if (now - lastSample < SAMPLE_PERIOD_MS) return;
  lastSample = now;

  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  ImuSample sample;
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
