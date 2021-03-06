# Main driver program that conects to the IoT core cloud and uploads the image. Once t he image is acknowledge, it is removed 
# from the local storage
import argparse
import datetime
import json
import os
import ssl
import time
import cv2
import jwt
import paho.mqtt.client as mqtt
import base64
import cv2
import time
import jsonpickle
from  multiprocessing import Queue
import _thread
from Data import Stream
from FileUtils import *
from ReteriveImageUtility import fetchImage
QUEUE=Queue() # queue that keeps all the image read by the worker image reader thread
backlog= Queue() # queue that holds file name of the file sent to the IoT core platform
def create_jwt(project_id, private_key_file, algorithm):
    """Create a JWT (https://jwt.io) to establish an MQTT connection."""
    token = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'aud': project_id
    }
    with open(private_key_file, 'r') as f:
        private_key = f.read()
    print('Creating JWT using {} from private key file {}'.format(
        algorithm, private_key_file))
    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


class Device(object):
    """Represents the state of a single device."""

    def __init__(self):
        self.temperature = 0
        self.fan_on = False
        self.connected = False

    def update_sensor_data(self):
        """Pretend to read the device's sensor data.
        If the fan is on, assume the temperature decreased one degree,
        otherwise assume that it increased one degree.
        """
        if self.fan_on:
            self.temperature -= 1
        else:
            self.temperature += 1

    def wait_for_connection(self, timeout):
        """Wait for the device to become connected."""
        total_time = 0
        while not self.connected and total_time < timeout:
            time.sleep(1)
            total_time += 1

        if not self.connected:
            raise RuntimeError('Could not connect to MQTT bridge.')

    def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
        """Callback for when a device connects."""
        print('Connection Result:', error_str(rc))
        self.connected = True

    def on_disconnect(self, unused_client, unused_userdata, rc):
        """Callback for when a device disconnects."""
        print('Disconnected:', error_str(rc))
        self.connected = False
   # once the image is recived by the cloud, it is acknowledge by calling this method.
   # On each ackknowledge, a image filename is peek from the backlog queue and corresponding file is removed
   # from  the local storage
    def on_publish(self, unused_client, unused_userdata, unused_mid):
       imagePath=backlog.get()
       removeFile(imagePath)
       print('Published image acknowledged acked.')

    def on_subscribe(self, unused_client, unused_userdata, unused_mid,
                     granted_qos):
        """Callback when the device receives a SUBACK from the MQTT bridge."""
        print('Subscribed: ', granted_qos)
        if granted_qos[0] == 128:
            print('Subscription failed.')

    def on_message(self, unused_client, unused_userdata, message):
        """Callback when the device receives a message on a subscription."""
        payload = message.payload.decode('utf-8')
        print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))

        # The device will receive its latest config when it subscribes to the
        # config topic. If there is no configuration for the device, the device
        # will receive a config with an empty payload.
        if not payload:
            return

        # The config is passed in the payload of the message. In this example,
        # the server sends a serialized JSON string.
        data = json.loads(payload)
        if data['fan_on'] != self.fan_on:
            # If changing the state of the fan, print a message and
            # update the internal state.
            self.fan_on = data['fan_on']
            if self.fan_on:
                print('Fan turned on.')
            else:
                print('Fan turned off.')


def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Example Google Cloud IoT MQTT device connection code.')
    parser.add_argument(
        '--project_id',
        default='perch-244901',
        help='GCP cloud project name.')
    parser.add_argument(
        '--registry_id', default='deviceregister', help='Cloud IoT registry id')
    parser.add_argument(
        '--device_id',default='iot',
        help='Cloud IoT device id')
    parser.add_argument(
        '--private_key_file', default= "rsa_private.pem", help='Path to private key')
    parser.add_argument(
        '--algorithm',
        choices=('RS256', 'ES256'),
        default='RS256',
        help='Which encryption algorithm to use to generate the JWT.')
    parser.add_argument(
        '--cloud_region', default='us-central1', help='GCP cloud region')
    parser.add_argument(
        '--ca_certs',
        default='roots.pem',
        help='CA root certificate. Get from https://pki.google.com/roots.pem')
    parser.add_argument(
        '--mqtt_bridge_hostname',
        default='mqtt.googleapis.com',
        help='MQTT bridge hostname.')
    parser.add_argument(
        '--mqtt_bridge_port', type=int, default=8883, help='MQTT bridge port.')
    parser.add_argument(
        '--message_type', choices=('event', 'state'),
        default='event',
        help='Indicates whether the message to be published is a '
              'telemetry event or a device state message.')
    parser.add_argument(
        '--dir',required=True, help='Disk directory from where the images has to be read. Please do not put / at the end')

    return parser.parse_args()


def main():
    args = parse_command_line_args()

    # Create the MQTT client and connect to Cloud IoT.
    client = mqtt.Client(
        client_id='projects/{}/locations/{}/registries/{}/devices/{}'.format(
            args.project_id,
            args.cloud_region,
            args.registry_id,
            args.device_id))
    client.username_pw_set(
        username='unused',
        password=create_jwt(
            args.project_id,
            args.private_key_file,
            args.algorithm))
    client.tls_set(ca_certs=args.ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    device = Device()

    client.on_connect = device.on_connect
    client.on_publish = device.on_publish
    client.on_disconnect = device.on_disconnect
    client.on_subscribe = device.on_subscribe
   # client.on_message = device.on_messagei
    _thread.start_new_thread(fetchImage,("ImageReteriver", QUEUE, args.dir,args.device_id)) # start the worker thread to read the images
    while(1): # infinite loop  to check for network connectivity and if network is reachable  connects to the cloud
     try: 
      print("trying to connect")
      client.connect(args.mqtt_bridge_hostname, args.mqtt_bridge_port)
      client.loop_start()
    # This is the topic that the device will publish telemetry events
    # (temperature data) to.
      mqtt_telemetry_topic = '/devices/{}/events'.format(args.device_id)
    # This is the topic that the device will receive configuration updates on.
      mqtt_config_topic = '/devices/{}/config'.format(args.device_id)
    # Wait up to 5 seconds for the device to connect.
   #   device.wait_for_connection(5)

    # Subscribe to the config topic.
      client.subscribe(mqtt_config_topic, qos=1)
      while(1):
        print("processing image to upload")
        stream=QUEUE.get(True); # read the image from the queue(from the one that hold the lastest image)
        payload= jsonpickle.encode(stream) # json encode the image
        client.publish(mqtt_telemetry_topic, payload, qos=1) # publish it to the cloud
        backlog.put(stream.fileName) # put the file name for removal once acknowledged
        time.sleep(1) # sleep for a second before reading the next image
     except: # if connection fails
      client.disconnect() 
      client.loop_stop()
    print('Finished loop successfully. Goodbye!')
if __name__ == '__main__':
    main()
