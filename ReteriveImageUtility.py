import base64 
from ImageEncoder import *
import cv2
import glob
import datetime
import time
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
  images = [cv2.imread(file) for file in glob.glob(imageDirectory+"/*.png")]
  for img in images:
    try:
     imageHash= str(dhash(img));
     processedImage[imageHash] 
    except KeyError as e:   
     encodedImg=base64.b64encode(img)
     stream=encodeImage(encodedImg, datetime.datetime.now(),device_id,imageHash)
     processedImage[imageHash]=1
     queue.put(stream)
    except cv2.error as e:
      print("image is corrupted, will be attempted next time")
   
 
