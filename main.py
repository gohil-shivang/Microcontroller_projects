import board
dir(board)
import adafruit_mpu6050
import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
from pyftdi.i2c import I2cController
from pyftdi.ftdi import Ftdi
i2c = I2cController()
i2c.configure('ftdi://ftdi:232h:1:3/1')
slave = i2c.get_port(0x68)
#mpu = adafruit_mpu6050.MPU6050(i2c)
power_mng = 0x6B
smplrt_div = 0x19
CONFIG = 0x1A
config_of_gyro = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47
TEMP_OUT0 = 0x41
    
def init():
# Write to sample rate register
  slave.write_to(smplrt_div, b'\x07')
# Write to power management register
  slave.write_to(power_mng, b'\x01')
# Write to Configuration register
  slave.write_to(CONFIG, b'\x00')
# Write to Gyro configuration register
  slave.write_to(config_of_gyro, b'\x18')
# Write to interrupt enable register
  slave.write_to(INT_ENABLE, b'\x01')
devAddr = 0x68 # MPU6050 device Address
init()
print("Gyroscope and Accelerometer Data:")



def getData(addr):
#16-bit sensor data, in higher byte and lower byte
    hi = slave.read_from(addr, 1).hex()
    lo = slave.read_from(addr + 1, 1).hex()
    value = int(hi + lo, 16)
    if(value > 32768):
        value = value - 65536
    return value


Vertices = ((1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1), (-1, 1, 1), (-1, -1, -1), (-1, -1, 1), (-1, 1, -1))
Edges = ((0, 1), (0, 3), (0, 4), (1, 2), (1, 7), (2, 5), (2, 3), (3, 6), (4, 6), (4, 7), (5, 6), (5, 7))
Quads = ((0, 3, 6, 4), (2, 5, 6, 3), (1, 2, 5, 7), (1, 0, 4, 7), (7, 4, 6, 5), (2, 3, 0, 1))

def wireCube():
    glBegin(GL_LINES)
    for cubeEdge in Edges:
        for vertex in cubeEdge:
            glVertex3fv(Vertices[vertex])
    glEnd()

gGain = 1.8
pg.init()
display = (900, 600)
pg.display.set_mode(display, DOUBLEBUF|OPENGL)
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -5)

while True:
#Read Accelerometer raw value
    xAcc = getData(ACCEL_XOUT_H)
    yAcc = getData(ACCEL_YOUT_H)
    zAcc = getData(ACCEL_ZOUT_H)
# print(xAcc, yAcc, zAcc)

    #Temp = getTemp(TEMP_OUT0)
#Read Gyroscope raw value
    xGyro = getData(GYRO_XOUT_H)
    yGyro = getData(GYRO_YOUT_H)
    zGyro = getData(GYRO_ZOUT_H)
# print(xGyro, yGyro, zGyro)
#Full scale range +/- 250 degree/C as per sensitivity scale factor
    xA = xAcc/16384.0
    yA = yAcc/16384.0
    zA = zAcc/16384.0
    xG = xGyro/131.0
    yG = yGyro/131.0
    zG = zGyro/131.0
    if zG>1:
        glRotatef(zG*gGain,0,zG*gGain,0)
    if zG<-1:
        glRotatef(-zG*gGain,0,zG*gGain,0)
    if yG>1:
        glRotatef(yG*gGain,yG*gGain,0,0)
    if yG<-1:
        glRotatef(-yG*gGain,yG*gGain,0,0)
    if xG>1:
        glRotatef(xG*gGain,0,0,xG*gGain)
    if xG<-1:
        glRotatef(-xG*gGain,0,0,xG*gGain)
    for event in pg.event.get():  
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                glRotatef(1, 0, 1, 0)
            if event.key == pg.K_RIGHT:
                glRotatef(-1, 0, 1, 0)
            if event.key == pg.K_UP:
                glRotatef(1, 1, 0, 0)
            if event.key == pg.K_DOWN:
                glRotatef(-1, 1, 0, 0)
            if event.key == pg.K_z:
                glRotatef(1, 0, 0, 1)
            if event.key == pg.K_x:
                glRotatef(-1, 0, 0, 1)
            if event.key == pg.K_q:
                pg.quit()
                sys.exit()
glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
wireCube()
pg.display.flip()
pg.time.wait(10)
pg.quit()
    #print(mpu.getTemp())
print("xG, yG, zG = %.2f, %.2f, %.2f \u00b0/s" %(xG, yG, zG))
print("xA, yA, zA = %.2f, %.2f, %.2f g" %(xA, yA, zA))


