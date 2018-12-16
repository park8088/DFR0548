from microbit import *
import math

DFMotorInit = 0

class DFdriver:
  def __init__(self,freq,init):
    self.I2C = i2c
    self.I2C.init(freq=100000,sda=pin20,scl=pin19)
    if not init:
      self.i2cW(0x00, 0x00)
      self.freq(freq)
 
  def i2cW(self, reg, value):
    buf = bytearray(2)
    buf[0] = reg
    buf[1] = value
    self.I2C.write(0x40,buf)
 
  def i2cR(self, reg):
    buf = bytearray(1)
    buf[0] = reg
    self.I2C.write(0x40,buf)
    return self.I2C.read(0x40,1)
 
  def freq(self, freq):
    pre = math.floor(((25000000/4096/(freq * 0.915))-1) + 0.5)
    oldmode = self.i2cR(0x00)
    self.i2cW(0x00, (oldmode[0] & 0x7F) | 0x10)
    self.i2cW(0xFE, pre)
    self.i2cW(0x00, oldmode[0])
    sleep(5)
    self.i2cW(0x00, oldmode[0] | 0xa1)
 
  def pwm(self, channel, on, off):
    if ((channel < 0) or (channel > 15)):
      return
    buf = bytearray(5)
    buf[0] = 0x06 + 4 * channel
    buf[1] = on & 0xff
    buf[2] = (on >> 8) & 0xff
    buf[3] = off & 0xff
    buf[4] = (off >> 8) & 0xff
    self.I2C.write(0x40,buf)
    
class DFMotor:
  def __init__(self):
    global DFMotorInit
    self.CW = 1
    self.CCW = -1
    self._dri = DFdriver(100,DFMotorInit)
    if not DFMotorInit:
      DFMotorInit = 1
    self._speed = 0
 
  def speed(self, Speed):
    self._speed = abs(Speed) *16
    if (self._speed >= 4096):
      self._speed = 4095
 
  def run(self, _mot, dir):
    self._speed = self._speed * dir
    pp = (4 - _mot) * 2
    if self._speed > 0:
      self._dri.pwm(pp, 0, self._speed)
      self._dri.pwm(pp+1, 0, 0)
    else:
      self._dri.pwm(pp, 0, 0)
      self._dri.pwm(pp+1, 0, -self._speed)
 
  def stop(self, _mot):
    self._dri.pwm((4 - _mot) * 2, 0, 0);
    self._dri.pwm((4 - _mot) * 2 + 1, 0, 0)
 
  def runAll(self,dir):
    for i in range(1,4):
      self.run(i, dir)
  
  def stopAll(self):
    for i in range(1,4):
      self.stop(i)
#----------여기까지가 모터드라이버 라이브러리입니다.--------------------
#----------이 다음부터 실제 작동에 필요한 코딩을 하면 됩니다.-----------
