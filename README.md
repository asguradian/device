# Device
The project simulates being a IoT device. It consist of two main file: capture.py and device1.py. All necesary files to make the communcation possible(private key root CA) are are added on the repository. The project is done is python using following extra dependencies beides the one needed to communicate with the cloud IoT:
```sh
JsonPickle
Opencv
Anaconda Python
Conda (to install Opencv)
pip from conda(to install JsonPickle)
```
Please use Anaconda python  and setup pip command to install dependency to anaconda repo.

You have to separately run this two file; the order does not matter.

# Capture.py
 This file reads from a video file(i simulated a video file to be a camera(video also present on the repo)) and store the image on a disk path. It  will remove the old image to make the  room for the new images. It insures that at every point of there is a fixed number of images on a directory. It accepts 4 parameter which are will documented on the script itself. to run this file issue the command:
 ```sh
$ python capture.py  -f 10 -w 200 -h 200 -o /home/anil/pics
```
# device1.py
This file is a driver program that can communicate with the IoT core. This file uses the multi-threading concept to read the images from the specified directory and put on to a queue such that once the communication to the cloud is established the images, are reterived one by one and uploaded to the cloud. The worker thread keeps on examining the directory and reades the new file that are added by capture.py script. It then checks if the current file is already processed( previously read or not). If so it will disgard the file or else it will add the corresponding image to the queue for sending it to the cloud. Once the image is acknowledged by the cloud, the corresponding file is removed from the directory.

The worker thread is not affected by the network connectivity issue. It just read the file and put it on to the queue. The program automatically try to re-connect to the cloud if the connection is broken and again reads the image from the queue. Non of the images are lost due to connection lost issue as the images from the queue is only picked if the connection is successfully established. Run this file using following command:

Please make sure you have read & write permission on the directory you want  read and write the file.

If you have you own platform please provide necessary details here

```sh
$ python device1.py \
    --project_id=PROJECT_ID \
    --registry_id=REGISTRY_ID \
    --device_id=DEVICE_ID \
    --private_key_file=PATH TO rsa_private.pem \
    --algorithm=RS256(KEY TYPE)
    --dir= ABS PATH TO THE DIRECTORY(without / at last)
```  

The functionality of the program is well tested using  google cloud platform's IoT support by creating real topic, device.  functionality of the program is well tested using  google cloud platform's IoT support by creating real topic, device. 
