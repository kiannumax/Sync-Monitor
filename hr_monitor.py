from fifo import Fifo
from piotimer import Piotimer

# Custom py modules
from components import oled, rot, sensor, LED

# Initialize fifo for sensor samples
samples = Fifo(2000)
# Callback function for appending sensor reading to samples fifo
def detect_signal(tid):
    samples.put(sensor.read_u16())

# Function for displaying updated bpm and quit button
def update_oled(bpm):
   oled.fill(0)
   
   oled.text(f"BPM: {bpm if bpm else ''}", 0, 55)
   oled.text("<Quit>", 80, 55)
   
   oled.show()
    
# Function that gets called when HR Monitor is chosen from menu
def hr_monitor():
    # Read sensor data every 4ms
    timer = Piotimer(period = 4, mode = Piotimer.PERIODIC, callback = detect_signal)
    LED.off()

    sample_list = []
    history     = []
    peakcounts  = []
    ppg_demos   = []
    max_sample  = i = 0
    # Initialize required variables
    heartrate      = None
    beat = updated = False
    # Initialize oled with bpm and button
    update_oled(heartrate)
    while True:
        # If encoder has been adjusted
        if rot.fifo.has_data():
            action = rot.fifo.get()

            if action == 2: # If encoder button is pressed disable timer and led
                timer.deinit()
                LED.off()
                return # Return to menu
            
        # If sensor has recorded something
        if samples.has_data():
            sample = samples.get()
            # Append sample
            sample_list.append(sample)
            history.append(sample)

            # If amount of samples is large enough
            if len(sample_list) >= 750:
                # Define threshold
                threshold = (4 * max(sample_list) +   min(sample_list)) / 5

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
                            updated = True   
                            update_oled(heartrate)
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
            
            # If sample demos length is 4 take average and plot it on graph
            if len(ppg_demos) == 4:
                i += 1
                if i == 128: # If end of oled
                    i = 0
                    updated = False # Change graph update state
                    
                if i % 20 == 0: # Update oled every 20 new plots on the graph
                    if updated: # If previous graph is cleared
                        oled.show()
                
                ppg_point = sum(ppg_demos) / 4 # Average ppg sample
                ppg_demos = [] # Empty demos list

                # Scaling in order to fit in desired part of oled
                ppg_sample = ((ppg_point - minima) / ((maxima - minima) if (maxima - minima != 0) else 1)) * 63
                ppg_sample = (ppg_sample / 2) + (31.5 - (63 / (4)))
                # Plot ppg sample
                oled.pixel(i, int(53 - ppg_sample), 1)
                
            else: # If smaller then append new sample
                ppg_demos.append(sample)
