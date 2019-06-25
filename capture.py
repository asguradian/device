import time
import cv2
import argparse
#video = cv2.VideoCapture(0);
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
while(1):
 #ret, frame = cap.read()
 img= cv2.imread("1.png")
 x = float(w/img.shape[1])
 print(x)
 y = float(h/img.shape[0])
 resized= cv2.resize(img, (0, 0), fx=x, fy=y)
 if(counter>f):
  counter=counter % f;
 cv2.imwrite(o+"/img_"+str(counter % f)+".jpg",resized)
 counter+=1 

