import base64 
from ImageEncoder import *
import cv2
import datetime
import time
def fetchImage(workerName, queue, imageDirectory,device_id):
 while(1):
  img=cv2.imread('1.png')
  retval, buffer = cv2.imencode('.png', img)
  encodedImg=base64.b64encode(buffer)
  stream=encodeImage(encodedImg, datetime.datetime.now(),device_id)
  queue.put(stream)
  time.sleep(1)
 
