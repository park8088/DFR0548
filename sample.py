'''
DC모터 1개를 돌려보는 프로그램. 하단에 자세한 설명 있음.
'''

from microbit import *
import math

DFMotorInit = 0#DC모터 제어를 위해서 이것을 추가해야 함

#---------------DFR0548보드 제어용 라이브러리 시작--------------#

class DFdriver:#보드 공통적으로 쓰이는 클래스
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
 
  def motorStop(self, Motors):
    self.pwm((4 - Motors) * 2, 0, 0);
    self.pwm((4 - Motors) * 2 + 1, 0, 0);
 
  def setStepper(self, number, dir):
    if(number == 1):
      if dir:
        buf = bytearray([7,6,5,4])
      else:
        buf = bytearray([5,4,7,6])
    else:
      if dir:
        buf = bytearray([3,2,1,0])
      else:
        buf = bytearray([1,0,3,2])
    self.pwm(buf[0], 3071, 1023)
    self.pwm(buf[1], 1023, 3071)
    self.pwm(buf[2], 4095, 2047)
    self.pwm(buf[3], 2047, 4095)

class DFMotor:#DC모터용 클래스
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

#---------------DFR0548보드 제어용 라이브러리 끝--------------#
'''
본 프로그램 시작. 모터를 여러 개 돌리려면
motor.run(2,motor.CW)
motor.run(3,motor.CW)
이런 식으로 추가하면 됨. 멈출 때도 역시 모터 번호 별로 멈춤.
motor.CW는 전진, motor.CCW는 후진
motor.runAll(motor.CCW)나 motor.stopAll()처럼 모든 모터를 제어할 수도 있음.
'''
motor = DFMotor()# 모터 라이브러리 초기화

while True:
    if button_a.is_pressed():#버튼a를 누르면
        motor.speed(200)#모터속도 200설정
        motor.run(1,motor.CW)#1번모터를 전진(CW)
        sleep(1000)#1초 대기
        motor.stop(1)#1번모터 정지
    elif button_b.is_pressed():
        motor.speed(150)#모터속도 150설정
        motor.runAll(motor.CCW)#모든 모터를 후진(CCW)
        sleep(1000)#1초 대기
        motor.stopAll()#모든 모터 정지
        
