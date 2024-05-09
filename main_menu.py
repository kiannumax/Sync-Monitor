from time import sleep

# Custom py modules
from components import oled, rot
from history import history
from hr_monitor import hr_monitor
from hrv import hrv_analysis
from kubios import kubios_analysis


def show_text(options, hovers):
    oled.fill(0)
    
    for i in range(5):
        text = f"{'<' if hovers == i else ' '}{options[i]}{'>' if hovers == i else ' '}"
        oled.text(text, (90 if i == 4 else 0), (50 if i == 4 else 15 * i))
         
    oled.show()


options        = ["Live HR", "HRV Analysis", "Kubios", "History", "OFF"]
options_funcs  = [hr_monitor, hrv_analysis, kubios_analysis, history]
hovered_option = 0


show_text(options, hovered_option)
while True:
    if rot.fifo.has_data():
        action = rot.fifo.get()
        
        if action == 2:
            if hovered_option == 4:
                oled.fill(0)
                oled.show()
                
                break
            
            else:
                options_funcs[hovered_option]()
        
        elif action == 1:
            if hovered_option != 4:
                hovered_option += 1       
        
        elif action == -1:
            if hovered_option != 0:
                hovered_option -= 1
        
                
        show_text(options, hovered_option)
        