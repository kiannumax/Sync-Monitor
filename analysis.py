from fifo import Fifo
from piotimer import Piotimer
from framebuf import FrameBuffer, MONO_HLSB
from time import time
from math import sqrt
from json import dumps

# Custom py modules
from components import oled, rot, LED, sensor
from logo import logo_wait


def data_format(ppis):
    length = len(ppis)
   
    mean_ppi = sum(ppis) / length
    mean_hr  = 60000 / mean_ppi
    
    rmssd = sdnn = 0
    for i in range(length - 1):
        rmssd += (ppis[i + 1] - ppis[i]) ** 2
        sdnn  += (ppis[i] - mean_ppi) ** 2
        
    rmssd = sqrt(rmssd / length - 1)
    sdnn  = sqrt(sdnn / length - 1)
    
    measurement = {
    "mean_hr": round(mean_hr),
    "mean_ppi": round(mean_ppi),
    "rmssd": round(rmssd),
    "sdnn": round(sdnn)
    }
    
    return dumps(measurement)


samples = Fifo(2000)

def detect_signal(tid):
    samples.put(sensor.read_u16())
    
def oled_update(time_left):
    wait_logo = FrameBuffer(logo_wait, 128, 64, MONO_HLSB)
    oled.blit(wait_logo, 0, 0)
    oled.text(f"{time_left}", 55, 55)
    
    oled.show()


def measure_data():
    timer = Piotimer(period = 4, mode = Piotimer.PERIODIC, callback = detect_signal)
    LED.off()
    
    start_time = time()

    sample_list = []
    ppis        = []
    history     = []
    peakcounts  = []
    max_sample  = 0
    
    heartrate = prev_time = None
    beat      = False
    
    oled_update(30)
    while True:
        new_time = round(time() - start_time)
       
        if rot.fifo.has_data():
            action = rot.fifo.get()
        
            if action == 2:
                timer.deinit()
                LED.off()
                
                return (None, True)
            
        if new_time >= 30:
            timer.deinit()
            LED.off()
                
            return (ppis, False)
            
            
        if samples.has_data():
            sample = samples.get()
    
            sample_list.append(sample)
            history.append(sample)
            
            if len(sample_list) >= 750:
                threshold = (4 * max(sample_list) +   min(sample_list)) / 5

                for i in sample_list:
                    if i >= threshold and i > max_sample:
                        max_sample = i
                        
                    elif i < threshold and max_sample != 0:
                        try:
                            peakcounts.append(sample_list.index(max_sample))
                            max_sample = 0
                        
                        except Exception as e:
                            continue

                for i in range(len(peakcounts)):
                    delta = peakcounts[i] - peakcounts[i - 1]
                    ppi   = delta * 4
                    

                    if 300 < ppi < 1200:
                        heartrate = round(60000 / ppi)
                            
                        if heartrate > 30 and heartrate < 220:
                            ppis.append(ppi)
                            updated = True   

                sample_list = []
                peakcounts  = []
                
                
            history = history[-250:]
            minima, maxima = min(history), max(history)

            threshold_on = (minima + maxima * 3) // 4   
            threshold_off = (minima + maxima) // 2     

            if not beat and sample > threshold_on:
                beat = True
                LED.on()

            elif beat and sample < threshold_off:
                beat = False
                LED.off()
                
                
            if new_time != prev_time:
                prev_time = new_time
                oled_update(round(30 - new_time))
            



def show_text(hovered):
    oled.fill(0)
        
    oled.text("Place finger ", 15, 0)
    oled.text("on the Sensor", 12, 10)
    oled.text("and start!", 25, 20)

    oled.text(f"{'<' if hovered == 0 else ''}Start{'>' if hovered == 0 else ''}", 0, 55)
    oled.text(f"{'<' if hovered == 1 else ''}Quit{'>' if hovered == 1 else ''}", 80, 55)
    
    oled.show()


def analysis():
    hovered_option = 0
    
    show_text(hovered_option)
    while True:
        if rot.fifo.has_data():
            action = rot.fifo.get()
        
            if action == 2:
                if hovered_option == 1:
                    return (None, True)
                
                else:
                    return measure_data()
            
            elif action == 1:
                if hovered_option != 1:
                    hovered_option = 1
            
            elif action == -1:
                if hovered_option != 0:
                    hovered_option = 0
                    
        show_text(hovered_option)
        
                