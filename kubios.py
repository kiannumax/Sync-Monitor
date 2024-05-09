from json import loads, dumps
from framebuf import FrameBuffer, MONO_HLSB

# Curstom py modules
from components import oled, rot
from analysis import analysis, data_format
from connections import kubios_send
from history import save_data
from logo import logo_wait

# Function for displaying the problem message
def problem_message():
    oled.fill(0)
      
    oled.text("Kubios analysis", 2, 0)
    oled.text("has failed..", 16, 10)
    oled.text("Try again!", 23, 20)
    oled.text("<Quit>", 38, 55)
        
    oled.show()
    # Exit the function when encoder button is pressed
    while True:
        if rot.fifo.has_data():
                action = rot.fifo.get()
                if action == 2:
                    return

# Function for displaying the hrv and Kubios data with buttons
def show_data(data, hovered):
    data = loads(data)
    oled.fill(0)
    
    i = 0 # Display each attribute
    for key, value in data.items():
        oled.text(f"{key}: {value}", 0, i * 9)
        i += 1
    # Buttons with checks for hovering
    oled.text(f"{'<Save>' if hovered == 0 else 'Save'}", 0, 57)
    oled.text(f"{'<Quit>' if hovered == 1 else 'Quit'}", 80, 57)
    
    oled.show()
    
# Function that gets called when Kubios is chosen from menu
def kubios_analysis():
    measurement = analysis()
    # If analysis window is left by pressing encoder button
    if measurement[1]:
        return # Return to menu
    
    try: # If all 30s of data collection is done try
        oled.fill(0) # Show waiting logo while sending receiving data from Kubios
        boot_logo = FrameBuffer(logo_wait, 128, 64, MONO_HLSB)
        oled.blit(boot_logo, 0, 0)
        oled.show()
        # Define data from Kubios and format custom hrv data in json
        data = kubios_send(measurement[0])
        hrv  = data_format(measurement[0])
         
        hrv = loads(hrv) # Unpack and modify hrv json
        hrv['sns'] = round(data['analysis']['sns_index'], 2)
        hrv['pns'] = round(data['analysis']['pns_index'], 2)
        # Final data containing custom hrv analysis and pns and sns values from Kubios
        data = dumps(hrv)
    
    except Exception as e: # If issue display message and return to menu when encoder button is pressed
        problem_message()
        return
        
    # 0 or 1 for save and quit
    hovered_option = 0
    # Initialize oled with data and buttons
    show_data(data, hovered_option)
    while True:
        # If encoder has been adjusted
        if rot.fifo.has_data():
            action = rot.fifo.get()
            # If encoder is pressed return to menu
            if action == 2:
                if hovered_option == 0: # If save option is chosen call the data saving function
                    save_data(data, 'kubios')
                    
                return
                    
            elif action == 1: # If encoder turned to the right
                if hovered_option != 1: # Limit
                    hovered_option = 1      
            
            elif action == -1: # If encoder turned to the left
                if hovered_option != 0: # Limit
                    hovered_option = 0
        
        # Update oled according to encoder adjustments
        show_data(data, hovered_option)
