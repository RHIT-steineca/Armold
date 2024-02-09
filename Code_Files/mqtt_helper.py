"""
  Library for making MQTT easier to use.
"""

import json
import paho.mqtt.client as mqtt

class MqttClient(object):
  """Helper class to make it easier to work with MQTT subscriptions and publications."""

  def __init__(self):
    self.client = mqtt.Client()
    self.subscription_topic_name = None
    self.publish_topic_name = None
    self.callback = None

  def connect(self, subscription_topic_name, publish_topic_name,
              mqtt_broker_ip_address="mosquitto.csse.rose-hulman.edu",
              use_off_campus_broker=False):
    if mqtt_broker_ip_address == "mosquitto.csse.rose-hulman.edu" and use_off_campus_broker:
    #   print("Using broker.hivemq.com instead of mosquitto.csse.rose-hulman.edu")
      mqtt_broker_ip_address = "broker.hivemq.com"
    self.subscription_topic_name = subscription_topic_name
    self.publish_topic_name = publish_topic_name

    # Callback for when the connection to the broker is complete.
    self.client.on_connect = self._on_connect
    self.client.message_callback_add(self.subscription_topic_name, self._on_message)

    # print("Connecting to mqtt broker {}".format(mqtt_broker_ip_address), end="")
    self.client.connect(mqtt_broker_ip_address)
    # self.client.connect(mqtt_broker_ip_address, 1883, 60)
    self.client.loop_start()

  def send_message(self, type_name, payload=None):
    message_dict = {"type": type_name}
    if payload is not None:
      message_dict["payload"] = payload
    message = json.dumps(message_dict)
    self.client.publish(self.publish_topic_name, message)

  # noinspection PyUnusedLocal
  def _on_connect(self, client, userdata, flags, rc):
    if rc == 0:
        # print(" ... Connected!")
    else:
        # print(" ... Error!!!")
        exit()

    # print("Publishing to topic:", self.publish_topic_name)
    self.client.on_subscribe = self._on_subscribe

    # Subscribe to topic(s)
    self.client.subscribe(self.subscription_topic_name)

  # noinspection PyUnusedLocal
  def _on_subscribe(self, client, userdata, mid, granted_qos):
    # print("Subscribed to topic:", self.subscription_topic_name)

  # noinspection PyUnusedLocal
  def _on_message(self, client, userdata, msg):
    message = msg.payload.decode()
    # print("Received message:", message)
    if not self.callback:
        # print("Missing a callback")
        return

    # Attempt to parse the message and call the appropriate function.
    try:
        message_dict = json.loads(message)
    except ValueError:
        # print("Unable to decode the received message as JSON")
        return

    if "type" not in message_dict:
        # print("Received a messages without a 'type' parameter.")
        return
    message_type = message_dict["type"]
    message_payload = None
    if "payload" in message_dict:
        message_payload = message_dict["payload"]        

    self.callback(message_type, message_payload)

  def close(self):
    self.callback = None
    self.client.loop_stop()
    self.client.disconnect()