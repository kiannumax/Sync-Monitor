from json import loads
from time import sleep

# Curstom py modules
from components import oled, rot
from analysis import analysis, data_format
from connections import mqtt
from history import save_data

# Function for displaying the problem message
def problem_message(message):
    oled.fill(0)
    
    if message: # If issue is in formatting data
        oled.text("Data collection", 2, 0)
        oled.text("has failed..", 16, 10)
        oled.text("Try again!", 23, 20)
        oled.text("<Quit>", 38, 55)
        
    else: # If issue is in sending data
        oled.text("Data sending", 14, 0)
        oled.text("has failed..", 16, 10)
        oled.text("<Ok>", 47, 55)
        
    oled.show()
    # Exit the function when encoder button is pressed
    while True:
        if rot.fifo.has_data():
                action = rot.fifo.get()
                if action == 2:
                    return

# Function for displaying hrv data and buttons
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
    
# Function that gets called when HRV Analysis is chosen from menu
def hrv_analysis():
    measurement = analysis()
    # If analysis window is left by pressing encoder button
    if measurement[1]:
        return # Return to menu
    

    try: # Try formatting collected data
        data = data_format(measurement[0])
    
    except Exception as e: # If issue
        problem_message(True) # Display the corresponding message
        return # And return to menu when encoder button was pressed
    
    
    try: # Try sending message to mqtt
         mqtt.send_message(data)
    
    except Exception as e: # If issue display the corresponding message
        problem_message(False)
        
    # Show message of successful sending for 4s
    oled.fill(0)
    oled.text("Message send", 15, 0)
    oled.text("Successful!", 20, 10)
    
    oled.show()
    sleep(4)

    # 0 or 1 for save and quit
    hovered_option = 0
    # Initialize oled with data and buttons
    show_data(data, hovered_option)
    while True:
        # If encoder has been adjusted
        if rot.fifo.has_data():
            action = rot.fifo.get()

            if action == 2:  # If encoder button is pressed return to menu
                if hovered_option == 0: # If save option is chosen call the data saving function
                    save_data(data, 'hrv')
                    
                return
                    
            elif action == 1: # If encoder turned to the right
                if hovered_option != 1: # Limit
                    hovered_option = 1      
            
            elif action == -1: # If encoder turned to the left
                if hovered_option != 0: # Limit
                    hovered_option = 0

        # Update oled according to encoder adjustments
        show_data(data, hovered_option)
