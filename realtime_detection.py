#import packages
from imutils.video import VideoStream
from multiprocessing import Process 
from multiprocessing import Queue 
from imutils.video import FPS
import numpy as np 
import argparse
import imutils
import time
import os



#create function classify_frame eith 3 parameters: net, inputQueue, outputQueue
def classify_frame(net, inputQueue, outputQueue):
    #keep looping
    while True:
        #this checks if there's a frame in input queue, 
        #resize it and construct blob

        if not inputQueue.empty():
            #grab frame, resize, and create blob
            frame = inputQueue.get()
            frame = cv2.resize(frame,(300, 300))
            blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)

            #set blob as input to deep learning object detector, 
            #obtain detections
            net.setInput(blob)
            detections = net.forward()

            #write detections to output queue
            outputQueue.put(detections)




ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

#initialize list of class labels
#generate bounding box

CLASSES = ["background", "cat", "person"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

#load serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

#initialize input queue(frames), output queue  (detections)

inputQueue = Queue(maxsize=1)
outputQueue = Queue(maxsize=1)
detections = None 

