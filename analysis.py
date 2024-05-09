from fifo import Fifo
from piotimer import Piotimer
from framebuf import FrameBuffer, MONO_HLSB
from time import time
from math import sqrt
from json import dumps

# Custom py modules
from components import oled, rot, LED, sensor
from logo import logo_wait

# Function for formatting hrv data into json string
def data_format(ppis):
    length = len(ppis)
   
    mean_ppi = sum(ppis) / length
    mean_hr  = 60000 / mean_ppi
    
    rmssd = sdnn = 0
    # Calculate rmssd and sdnn
    for i in range(length - 1):
        rmssd += (ppis[i + 1] - ppis[i]) ** 2
        sdnn  += (ppis[i] - mean_ppi) ** 2
        
    rmssd = sqrt(rmssd / length - 1)
    sdnn  = sqrt(sdnn / length - 1)

    # Save analysis data
    measurement = {
    "mean_hr": round(mean_hr),
    "mean_ppi": round(mean_ppi),
    "rmssd": round(rmssd),
    "sdnn": round(sdnn)
    }
    # Return hrv analysis in json string format
    return dumps(measurement)

# Initialize fifo for sensor samples
samples = Fifo(2000)

# Callback function for appending sensor reading to samples fifo
def detect_signal(tid):
    samples.put(sensor.read_u16())

# Function for displaying left time and waiting logo
def oled_update(time_left):
    wait_logo = FrameBuffer(logo_wait, 128, 64, MONO_HLSB)
    oled.blit(wait_logo, 0, 0)
    oled.text(f"{time_left}", 55, 55)
    
    oled.show()

# Function for measuring ppis for 30s
def measure_data():
    # Read sensor data every 4ms
    timer = Piotimer(period = 4, mode = Piotimer.PERIODIC, callback = detect_signal)
    LED.off()
    
    start_time = time()

    sample_list = []
    ppis        = []
    history     = []
    peakcounts  = []
    max_sample  = 0
    # Initialize required variables
    prev_time = None
    beat      = False
    
    oled_update(30)  # Initialize oled with 30s of left time
    while True:
        new_time = round(time() - start_time)
       
        if rot.fifo.has_data():
            action = rot.fifo.get()
            # If measurement was interrupted by an encoder button press
            if action == 2: # Disable led and timer
                timer.deinit()
                LED.off()
                
                return (None, True) # Exit the measurement window, interrupt = True
            
        if new_time >= 30: # If 30s have elapsed disable timer and led
            timer.deinit()
            LED.off()
                
            return (ppis, False) # Exit the measurement window, interrupt = False

        # If sensor has recorded something
        if samples.has_data():
            sample = samples.get()
            # Append sample
            sample_list.append(sample)
            history.append(sample)

            # If amount of samples is large enough
            if len(sample_list) >= 750:
                threshold = (4 * max(sample_list) +   min(sample_list)) / 5
                # Define threshold

                for i in sample_list:
                    # Update max sample if found larger
                    if i >= threshold and i > max_sample:
                        max_sample = i
                        
                    elif i < threshold and max_sample != 0:
                        try: # Otherwise try appending peak
                            peakcounts.append(sample_list.index(max_sample))
                            max_sample = 0
                        
                        except Exception as e:
                            continue # If issue ignore and continue

                # Go over peaks to define ppi
                for i in range(len(peakcounts)):
                    delta = peakcounts[i] - peakcounts[i - 1]
                    ppi   = delta * 4

                    # if ppi is reasonable find bpm
                    if 300 < ppi < 1200:
                        heartrate = round(60000 / ppi)

                        # If bpm is reasonable update oled
                        if heartrate > 30 and heartrate < 220:
                            ppis.append(ppi)

                # Empty lists for new samples
                sample_list = []
                peakcounts  = []

            # code part taken from https://blog.martinfitzpatrick.com/wemos-heart-rate-sensor-display-micropython/
            # Go over last 250 samples
            history = history[-250:]
            minima, maxima = min(history), max(history)
            # Find thresholds with min and max
            threshold_on = (minima + maxima * 3) // 4   
            threshold_off = (minima + maxima) // 2     

            if not beat and sample > threshold_on:
                # Turn on led if new heart beat
                beat = True
                LED.on()

            elif beat and sample < threshold_off:
                # Turn off led if signal falling after heart beat
                beat = False
                LED.off()
                
            # If a second has elapsed update oled
            if new_time != prev_time:
                prev_time = new_time
                oled_update(round(30 - new_time))

# Function for displaying initial message
def show_text(hovered):
    oled.fill(0)
        
    oled.text("Place finger ", 15, 0)
    oled.text("on the Sensor", 12, 10)
    oled.text("and start!", 25, 20)

    # Buttons with checks for hovering
    oled.text(f"{'<' if hovered == 0 else ''}Start{'>' if hovered == 0 else ''}", 0, 55)
    oled.text(f"{'<' if hovered == 1 else ''}Quit{'>' if hovered == 1 else ''}", 80, 55)
    
    oled.show()

# Function that is called when Kubios or HRV Analysis windows are opened
def analysis():
    hovered_option = 0
    # Display initial message
    show_text(hovered_option)
    while True:
        # If encoder has been adjusted
        if rot.fifo.has_data():
            action = rot.fifo.get()
        
            if action == 2: # If encoder button is pressed
                if hovered_option == 1: # If quit is chosen return to menu, interrupt = True
                    return (None, True)
                
                else: # Otherwise start data collection
                    return measure_data()
            
            elif action == 1: # If encoder turned to the right
                if hovered_option != 1: # Limit
                    hovered_option = 1
            
            elif action == -1: # If encoder turned to the left
                if hovered_option != 0: # Limit
                    hovered_option = 0
        # Update oled according to encoder adjustments
        show_text(hovered_option)
