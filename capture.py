import time
import cv2
import argparse
from multiprocessing import Queue
#video = cv2.VideoCapture(0);
from FileUtils import *
queue=Queue() #holds previously used fileName 
# # This script captures the image at the defined frame rate and resize the image to
# to the defined dimension and store it to the specified directory. The files are stored in a circular 
# manner such that at every point of time there is a fixed number of image on the directory. It deletes the old images to make roon for the new images.
counter=0;

def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Example Google Cloud IoT MQTT device connection code.')
    parser.add_argument(
        '--f',
        default=6,
        type=int,
        required=True,
        help='Number of frame to read per minute.')
    parser.add_argument(
        '--h', required=True,type=int, help='Height of the image')
    parser.add_argument(
        '--w',type=int,
        required=True,
        help='Width of the image')
    parser.add_argument(
        '--o', required=True, help='Absolute location of the directory where image are saved')
    return parser.parse_args()

args = parse_command_line_args()
f=args.f
h=args.h
w=args.w
o= args.o
timeSleep= 60/f
cap = cv2.VideoCapture('12.mp4')
while(cap.isOpened()):
 ret, img = cap.read()
 x = float(w/img.shape[1])
 y = float(h/img.shape[0])
 resized= cv2.resize(img, (0, 0), fx=x, fy=y)
 if(counter>f-1):
   oldestImage=queue.get(block=False);
   removeFile(oldestImage)
 newImage= o+"/"+str(counter)+".png";  
 queue.put(newImage)
 cv2.imwrite(newImage,resized)
 counter+=1
 time.sleep(timeSleep)


