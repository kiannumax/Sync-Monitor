from json import loads
from time import sleep

# Curstom py modules
from components import oled, rot
from analysis import analysis, data_format
from connections import mqtt
from history import save_data


def problem_message(message):
    oled.fill(0)
    
    if message:
        oled.text("Data collection", 2, 0)
        oled.text("has failed..", 16, 10)
        oled.text("Try again!", 23, 20)
        oled.text("<Quit>", 38, 55)
        
    else:   
        oled.text("Data sending", 14, 0)
        oled.text("has failed..", 16, 10)
        oled.text("<Ok>", 47, 55)
        
    oled.show()
    
    while True:
        if rot.fifo.has_data():
                action = rot.fifo.get()
                if action == 2:
                    return


def show_data(data, hovered):
    data = loads(data)
    oled.fill(0)
    
    i = 0
    for key, value in data.items():
        oled.text(f"{key}: {value}", 0, i * 9)
        i += 1
        
    oled.text(f"{'<Save>' if hovered == 0 else 'Save'}", 0, 57)
    oled.text(f"{'<Quit>' if hovered == 1 else 'Quit'}", 80, 57)
    
    oled.show()
    

def hrv_analysis():
    measurement = analysis()
    
    if measurement[1]:
        return
    
    
    data = None
    try:
        data = data_format(measurement[0])
    
    except Exception as e:
        print(e)
        problem_message(True)
        return
    
    
    try:
         mqtt.send_message(data)
    
    except Exception as e:
        print(e)
        problem_message(False)
        
        
    oled.fill(0)
    oled.text("Message send", 15, 0)
    oled.text("Successful!", 20, 10)
    
    oled.show()
    sleep(5)
    
    hovered_option = 0
    show_data(data, hovered_option)
    while True:
        if rot.fifo.has_data():
            action = rot.fifo.get()
            
            if action == 2:
                if hovered_option == 0:
                    save_data(data, 'hrv')
                    
                return
                    
            elif action == 1:
                if hovered_option != 1:
                    hovered_option = 1      
            
            elif action == -1:
                if hovered_option != 0:
                    hovered_option = 0
        
                
        show_data(data, hovered_option)

    