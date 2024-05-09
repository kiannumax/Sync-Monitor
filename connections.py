from network import WLAN, STA_IF
from time import sleep
from umqtt.simple import MQTTClient
from urequests import post

# Function for sending and receiving data from Kubios
def kubios_send(data):
    # Required credentials and links for the Kubios connection
    APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
    CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
    CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"
    TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"
    # Initialize connection
    response = post(
         url = TOKEN_URL,
         data = 'grant_type=client_credentials&client_id={}'.format(CLIENT_ID),
         headers = {'Content-Type':'application/x-www-form-urlencoded'},
         auth = (CLIENT_ID, CLIENT_SECRET))
    
    response = response.json()
    # Dataset to be sent to Kubios
    dataset = {
            "type": "RRI",
            "data": data,
            "analysis": {
                "type": "readiness"
                }
            }
    
    access_token = response["access_token"]
   
    response = post( # Request for data analyzing the given list of ppis
         url = "https://analysis.kubioscloud.com/v2/analytics/analyze",
         headers = {"Authorization": "Bearer {}".format(access_token), "X-Api-Key": APIKEY}, json = dataset)
    
    return response.json()

# Class used for wifi and mqtt information and connection
class Mqtt:
    def __init__(self, SSID, PASSWORD, BROKER_IP):
    
        self.SSID        = SSID
        self.PASSWORD    = PASSWORD
        self.BROKER_IP   = BROKER_IP
        self.ip          = None
        self.mqtt_client = None
    
    # Method to connect to WLAN
    def connect_wlan(self):
        # Connecting to the group WLAN
        wlan = WLAN(STA_IF)
        wlan.active(True)
        wlan.connect(self.SSID, self.PASSWORD)

        # Attempt to connect once per second
        while not wlan.isconnected():
            sleep(1)

        self.ip = wlan.ifconfig()[0] # Save IP
        
    # Method for connecting to mqtt and saving the client
    def connect_mqtt(self):
        mqtt_client = MQTTClient("", self.BROKER_IP)
        mqtt_client.connect(clean_session = True)
        
        self.mqtt_client = mqtt_client
        
    # Method for sending messages to mqtt
    def send_message(self, msg):
        self.mqtt_client.publish("HRV-Analysis", msg)
    
# Initialize class with group's credentials
mqtt = Mqtt("KMD652_GROUP_8", "maxviswakchris", "192.168.8.185")
