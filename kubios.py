from json import loads, dumps
from framebuf import FrameBuffer, MONO_HLSB

# Curstom py modules
from components import oled, rot
from analysis import analysis, data_format
from connections import kubios_send
from history import save_data
from logo import logo_wait


def problem_message():
    oled.fill(0)
      
    oled.text("Kubios analysis", 2, 0)
    oled.text("has failed..", 16, 10)
    oled.text("Try again!", 23, 20)
    oled.text("<Quit>", 38, 55)
        
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
    

def kubios_analysis():
    measurement = analysis()
    
    if measurement[1]:
        return
    
    try:
        oled.fill(0)
        boot_logo = FrameBuffer(logo_wait, 128, 64, MONO_HLSB)
        oled.blit(boot_logo, 0, 0)
        oled.show()
        
        data = kubios_send(measurement[0])
        hrv  = data_format(measurement[0])
         
        hrv = loads(hrv)
        hrv['sns'] = round(data['analysis']['sns_index'], 2)
        hrv['pns'] = round(data['analysis']['pns_index'], 2)
         
        data = dumps(hrv)
    
    except Exception as e:
        print(e)
        problem_message()
        return
        
        
    hovered_option = 0
    show_data(data, hovered_option)
    while True:
        if rot.fifo.has_data():
            action = rot.fifo.get()
            
            if action == 2:
                if hovered_option == 0:
                    save_data(data, 'kubios')
                    
                return
                    
            elif action == 1:
                if hovered_option != 1:
                    hovered_option = 1      
            
            elif action == -1:
                if hovered_option != 0:
                    hovered_option = 0
        
                
        show_data(data, hovered_option)
