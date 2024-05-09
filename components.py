from machine import Pin, I2C, reset, ADC
from ssd1306 import SSD1306_I2C
from time import ticks_ms
from fifo import Fifo
from led import Led


class Encoder:
    def __init__(self, rot_a, rot_b, btn):
       self.a = Pin(rot_a, mode = Pin.IN, pull = Pin.PULL_UP)
       self.b = Pin(rot_b, mode = Pin.IN, pull = Pin.PULL_UP)
       self.btn = Pin(btn, mode = Pin.IN, pull = Pin.PULL_UP)
       self.prev_tick = 0
       
       self.fifo = Fifo(30, typecode = 'i')
       self.a.irq(handler = self.handler, trigger = Pin.IRQ_RISING, hard = True)
       self.btn.irq(handler = self.btn_handler, trigger = Pin.IRQ_RISING, hard = True)
            
            
    def btn_handler(self, pin):
        curr_tick = ticks_ms()
    
        if curr_tick - self.prev_tick > 50:
            self.fifo.put(2)
        
        self.prev_tick = curr_tick
        
        
    def handler(self, pin):       
        if self.b():
            self.fifo.put(-1)
        
        else:
            self.fifo.put(1)
            
            
i2c  = I2C(1, scl = Pin(15), sda = Pin(14), freq = 400000)
oled = SSD1306_I2C(128, 64, i2c)

sensor = ADC(Pin(26))
LED    = Led(20, Pin.OUT)
rot    = Encoder(10, 11, 12)
