import mqtt_helper

def mqtt_callback(type_name, payload):
    print("Received message type: ", type_name)
    print("Received message payload: ", payload)

sending = "Armold/ToDummy"
receiving = "Armold/ToBrain"
runtype = input("enter if dummy")
if(runtype != ""):
    sending = "Armold/ToDummy"
    receiving = "Armold/ToBrain"

mqtt_client = mqtt_helper.MqttClient()
mqtt_client.callback = lambda type, payload: mqtt_callback(type, payload)
mqtt_client.connect(sending, receiving, use_off_campus_broker=False)

try:
    while True:
        message = input()
        mqtt_client.send_message("command", message)
except KeyboardInterrupt:
    mqtt_client.close()