# Custom py modules
from components import oled, rot
from history import history
from hr_monitor import hr_monitor
from hrv import hrv_analysis
from kubios import kubios_analysis

# Function for updating the menu text
def show_text(options, hovers):
    oled.fill(0)
    
    for i in range(5): # Go over each element and change view if hovered over
        text = f"{'<' if hovers == i else ' '}{options[i]}{'>' if hovers == i else ' '}"
        oled.text(text, (90 if i == 4 else 0), (50 if i == 4 else 15 * i))
         
    oled.show()

# Menu options and their corresponding functions
options        = ["Live HR", "HRV Analysis", "Kubios", "History", "OFF"]
options_funcs  = [hr_monitor, hrv_analysis, kubios_analysis, history]
hovered_option = 0


show_text(options, hovered_option)
while True:
    # If encoder has been adjusted
    if rot.fifo.has_data():
        action = rot.fifo.get()
        # If encoder pressed
        if action == 2:
            # If option off, clear oled and escape the loop
            if hovered_option == 4:
                oled.fill(0)
                oled.show()
                break
            
            else: # Else call the corresponding to the hovered option function
                options_funcs[hovered_option]()
        
        elif action == 1: # If encoder turned to the right
            if hovered_option != 4: # Limit
                hovered_option += 1       
        
        elif action == -1: # If encoder turned to the left
            if hovered_option != 0: # Limit
                hovered_option -= 1
        
        # Update text according to encoder adjustments
        show_text(options, hovered_option)
        