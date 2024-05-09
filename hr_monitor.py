from fifo import Fifo
from piotimer import Piotimer

# Custom py modules
from components import oled, rot, sensor, LED

samples = Fifo(2000)

def detect_signal(tid):
    samples.put(sensor.read_u16())


def update_oled(bpm):
   oled.fill(0)
   
   oled.text(f"BPM: {bpm if bpm else ''}", 0, 55)
   oled.text("<Quit>", 80, 55)
   
   oled.show()
    
    
def hr_monitor():
    timer = Piotimer(period = 4, mode = Piotimer.PERIODIC, callback = detect_signal)
    LED.off()

    sample_list = []
    history     = []
    peakcounts  = []
    ppg_demos   = []
    max_sample  = i = 0
    
    heartrate      = None
    beat = updated = False
    
    update_oled(heartrate)
    while True:
        if rot.fifo.has_data():
            action = rot.fifo.get()
        
            if action == 2:
                timer.deinit()
                LED.off()
                return
            
            
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
                            updated = True   
                            update_oled(heartrate)

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
            
            
            if len(ppg_demos) == 4:
                i += 1
                if i == 128:
                    i = 0
                    updated = False
                    
                if i % 20 == 0:
                    if updated:
                        oled.show()
                
                ppg_point = sum(ppg_demos) / 4
                ppg_demos = []
                
                ppg_sample = ((ppg_point - minima) / ((maxima - minima) if (maxima - minima != 0) else 1)) * 63
                ppg_sample = (ppg_sample / 2) + (31.5 - (63 / (4)))
            
                oled.pixel(i, int(53 - ppg_sample), 1)
                
            else:
                ppg_demos.append(sample)
