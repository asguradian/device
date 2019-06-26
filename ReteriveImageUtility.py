import base64 
from ImageEncoder import *
import cv2
import glob
import datetime
import time
import os
processedImage={} # stored the reterived  image
#computer the hash of the image
def dhash(image, hashSize=8):
	# resize the input image, adding a single column (width) so we
	# can compute the horizontal gradient
	resized = cv2.resize(image, (hashSize + 1, hashSize))
 
	# compute the (relative) horizontal gradient between adjacent
	# column pixels
	diff = resized[:, 1:] > resized[:, :-1]
 
	# convert the difference image to a hash
	return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])
# fetch each iamge from the repository and check if it is already processed or not. hashing mechanism insures that we 
# do not process the same image twice ans it  takes the for the image to get acknowledged and removed
def fetchImage(workerName, queue, imageDirectory,device_id):
 print("Image processed") 
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
      print("image is corrupted, will be attempted next time")
   
 
