from time import sleep
from time import gmtime
from json import loads, dumps

# Custom py modules
from components import oled, rot


def save_data(data, mode):
    data = loads(data)
    data['type'] = mode
    
    date = gmtime()
    data['date'] = f"{date[2]}-{date[1]}-{date[0]} {date[3]}:{date[4]}"
    
    file = open('history.txt', 'a')
    file.write(dumps(data) + '\n')
    file.close()
    
    
def delete_line(lines, line_number):
    file = open('history.txt', 'w')
    
    for number, line in enumerate(lines):
        if number != line_number:
            file.write(line)
   
    file.close()
    
    file = open('history.txt', '+')
    lines = file.readlines()
    file.close()
    
    return lines
    
    
def show_measurement(data, hovered):
    data = loads(data)
    oled.fill(0)
    
    i = 0
    for key, value in data.items():
        if key != 'type' and key != 'date':
            oled.text(f"{key}: {value}", 0, i * 9)
            i += 1
        
    oled.text(f"{'<Delete>' if hovered == 0 else 'Delete'}", 0, 57)
    oled.text(f"{'<Back>' if hovered == 1 else 'Back'}", 80, 57)
    
    oled.show()


def show_text(lines, hovered, start_i, empty):
    oled.fill(0)
    if empty:
        oled.text("History is empty", 0, 0)
        oled.text("<Back>", 38, 55)
        
    else:
        for i in range(start_i, (start_i + 3) if len(lines) >= 3 else len(lines)):
            line = lines[i].replace('\n', '')
            line = loads(line)
            
            text = ('B' if line['type'] == 'hrv' else 'K') + line['date']
            
            oled.text(f"{'>' if (hovered == i - start_i) else ' '}{text}", 0, 15 * (i - start_i))
            
        oled.text(f"{'<' if hovered == 3 else ' '}Back{'>' if hovered == 3 else ' '}", 80, 50)
    
    oled.show()


def history():
    file = open("history.txt", '+')

    lines        = file.readlines()
    empty        = False
    if not len(lines):
        empty = True
        
    file.close()
      
    hovered_line = start_i = 0
    show_text(lines, hovered_line, start_i, empty)
    while True:
        if empty:
            while True:
                if rot.fifo.has_data():
                    if rot.fifo.get() == 2:
                            return
        
        if rot.fifo.has_data():
            action = rot.fifo.get()
            
            if action == 2:
                if hovered_line == 3:
                    return
                
                else:
                    hovered_option = 0
                    
                    show_measurement(lines[hovered_line], hovered_option)
                    while True:
                        if rot.fifo.has_data():
                            action = rot.fifo.get()
                            
                            if action == 2:
                                if hovered_option == 0:
                                    lines = delete_line(lines, hovered_line + start_i)
                                    hovered_line = start_i = 0
                                    
                                    
                                    if len(lines) == 0:
                                        empty = True
                                    
                                break
                                    
                            elif action == 1:
                                if hovered_option != 1:
                                    hovered_option = 1      
                            
                            elif action == -1:
                                if hovered_option != 0:
                                    hovered_option = 0
                                    
                        show_measurement(lines[hovered_line], hovered_option)
                
                
            elif action == 1:
                if hovered_line == 2 and start_i + 3 != len(lines) and len(lines) >= 4:
                    start_i += 1
                    
                else:
                    if hovered_line != 3:
                        if hovered_line == len(lines) - 1:
                            hovered_line = 3
                        
                        else:
                            hovered_line += 1
            
            elif action == -1:
                if hovered_line == 0 and start_i != 0:
                    start_i -= 1
                    
                elif hovered_line != 0:
                    if hovered_line == 3 and len(lines) < 4:
                        hovered_line = len(lines) - 1
                    
                    else:
                        hovered_line -= 1
                    
        show_text(lines, hovered_line, start_i, empty)
                 
