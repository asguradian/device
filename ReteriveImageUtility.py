import base64 
from ImageEncoder import *
import cv2
import glob
import datetime
import time
import os
processedImage={} # stored the reterived  image filename so that the same image file is not processed twice.

# Fetch each iamge from the directory and check if it is already processed or not.
# Every time the method reads all the file in the specified directory and process those which are not  previously procssed.
def fetchImage(workerName, queue, imageDirectory,device_id):
 while(1):
  paths =  sorted(glob.glob(imageDirectory+"/*.png"))
  images = [cv2.imread(file) for file in paths]
  for path in paths:
    if os.path.exists(path):
     try:
      processedImage[path] 
     except KeyError as e:
      image = cv2.imread(path)     
      encodedImg=base64.b64encode(image)
      stream=encodeImage(encodedImg, datetime.datetime.now(),device_id,path)
      processedImage[path]=1
      queue.put(stream)
     except cv2.error as e:
      print("image is corrupted, will be attempted next directory read call")
   
 
