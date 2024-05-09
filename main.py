'''Main file which runs automatically when Raspberry Pico powers on'''
from machine import Pin, reset
from framebuf import FrameBuffer, MONO_HLSB
from time import sleep

# Custom py modules
from logo import logo
from components import oled, LED
from connections import mqtt

# Reset led and oled just in case
oled.fill(0)
LED.off()
# Show bitmap logo while connecting to wifi and mqtt are being established
boot_logo = FrameBuffer(logo, 128, 64, MONO_HLSB)
oled.blit(boot_logo, 0, 0)
oled.show()

connection = True
try: # Try connecting
    mqtt.connect_wlan()
    mqtt.connect_mqtt()
    
except Exception as e: # If fails set connection state to False
    connection = False
    
if connection: # If connection successful show the message for 5s and call the menu function
    for i in range(5, 0, -1):
        oled.fill(0)
        
        oled.text("System boot", 19, 0)
        oled.text("Successful!", 20, 10)
        oled.text("Menu appears in:", 5, 40)
        oled.text(f"{i}", 60, 50)
        
        oled.show()
        sleep(1)
        
    import main_menu
    
else: # If connection failed show the message for 5s and reboot
    for i in range(5, 0, -1):
        oled.fill(0)
        
        oled.text("Oops...", 40, 0)
        oled.text("System booting", 7, 10)
        oled.text("has failed!", 20, 20)
        oled.text("Reboot in:", 25, 40)
        oled.text(f"{i}", 60, 50)
        
        oled.show()
        sleep(1)

    reset()
    