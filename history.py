from time import gmtime
from json import loads, dumps

# Custom py modules
from components import oled, rot

# Function for saving analysis
def save_data(data, mode):
    data = loads(data) # Unpack json format
    data['type'] = mode # Add type to json
    
    date = gmtime() # Add date to json
    data['date'] = f"{date[2]}-{date[1]}-{date[0]} {date[3]}:{date[4]}"
    # Open file with append data and write a new json line
    file = open('history.txt', 'a')
    file.write(dumps(data) + '\n')
    file.close()
    
# Function for deleting a record from history
def delete_line(lines, line_number):
    file = open('history.txt', 'w')
    # Open a file with write method and write all previous lines excluding the one being deleted
    for number, line in enumerate(lines):
        if number != line_number:
            file.write(line)
   
    file.close()
    # Close and open it with a new method to return updated list of records
    file = open('history.txt', '+')
    lines = file.readlines()
    file.close()
    
    return lines
    
# Function for displaying record data with buttons
def show_measurement(data, hovered):
    data = loads(data)
    oled.fill(0)
    
    i = 0 # Display each attribute
    for key, value in data.items():
        if key != 'type' and key != 'date':
            oled.text(f"{key}: {value}", 0, i * 9)
            i += 1
    # Buttons with checks for hovering
    oled.text(f"{'<Delete>' if hovered == 0 else 'Delete'}", 0, 57)
    oled.text(f"{'<Back>' if hovered == 1 else 'Back'}", 80, 57)
    
    oled.show()

# Function for displaying all history records and buttons
def show_text(lines, hovered, start_i, empty):
    oled.fill(0)
    if empty: # If history is empty
        oled.text("History is empty", 0, 0)
        oled.text("<Back>", 38, 55)
        
    else: # If not empty
        # Display all records depending on the scroll state
        for i in range(start_i, (start_i + 3) if len(lines) >= 3 else len(lines)):
            line = lines[i].replace('\n', '')
            line = loads(line)
            # Specify record type B-Basic, K-Kubios
            text = ('B' if line['type'] == 'hrv' else 'K') + line['date']
            oled.text(f"{'>' if (hovered == i - start_i) else ' '}{text}", 0, 15 * (i - start_i))
        # Display Back button
        oled.text(f"{'<' if hovered == 3 else ' '}Back{'>' if hovered == 3 else ' '}", 80, 50)
    
    oled.show()

# Function that gets called when History is chosen from menu
def history():
    file = open("history.txt", '+')
    # Open history file and append lines to a list
    lines        = file.readlines()
    empty        = False
    if not len(lines): # If file is empty
        empty = True
        
    file.close()
      
    hovered_line = start_i = 0 # Hover and scroll states
    show_text(lines, hovered_line, start_i, empty) # Initialize oled view
    while True:
        if empty: # Show only button and message if empty
            while True:
                if rot.fifo.has_data(): # Return to menu if encoder button is pressed
                    if rot.fifo.get() == 2:
                            return
        # If encoder has been adjusted
        if rot.fifo.has_data():
            action = rot.fifo.get()
            
            if action == 2: # If encoder button is pressed
                if hovered_line == 3: # Return to menu if back is chosen
                    return
                
                else: # Otherwise display record data
                    hovered_option = 0
                    
                    show_measurement(lines[hovered_line], hovered_option)
                    while True: # Start a new loop for monitoring encoder adjustments
                        if rot.fifo.has_data():
                            action = rot.fifo.get()
                            
                            if action == 2: # If encoder button is pressed
                                if hovered_option == 0: # If delete option is chosen
                                    # Delet record
                                    lines = delete_line(lines, hovered_line + start_i)
                                    hovered_line = start_i = 0
                                    # Update history records data
                                    if len(lines) == 0:
                                        empty = True
                                    
                                break # Go back to records
                                    
                            elif action == 1: # If encoder turned to the right
                                if hovered_option != 1: # Limit
                                    hovered_option = 1      
                            
                            elif action == -1: # If encoder turned to the left
                                if hovered_option != 0: # Limit
                                    hovered_option = 0
                        # Update oled according to encoder adjustments
                        show_measurement(lines[hovered_line], hovered_option)
                
                
            elif action == 1: # If encoder turned to the right
                # If scroll has to be done
                if hovered_line == 2 and start_i + 3 != len(lines) and len(lines) >= 4:
                    start_i += 1
                    
                else: # If scroll not affected
                    if hovered_line != 3:
                        if hovered_line == len(lines) - 1:
                            hovered_line = 3
                        
                        else:
                            hovered_line += 1
            
            elif action == -1: # If encoder turned to the left
                # If scroll has to be done
                if hovered_line == 0 and start_i != 0:
                    start_i -= 1
                    
                elif hovered_line != 0: # If scroll is not affected
                    if hovered_line == 3 and len(lines) < 4:
                        hovered_line = len(lines) - 1
                    
                    else:
                        hovered_line -= 1
        # Update oled according to encoder adjustments
        show_text(lines, hovered_line, start_i, empty)
