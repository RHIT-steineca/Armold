import mqtt_helper

def mqtt_callback(type_name, payload):
    print("Received message type: ", type_name)
    print("Received message payload: ", payload)

sending = "Armold/ToBrain"
receiving = "Armold/ToDummy"

mqtt_client = mqtt_helper.MqttClient()
mqtt_client.client.clean_session = False
mqtt_client.callback = lambda type, payload: mqtt_callback(type, payload)
mqtt_client.connect(sending, receiving, use_off_campus_broker=True)

try:
    while True:
        mqtt_client.client.loop()
except KeyboardInterrupt:
    mqtt_client.close()