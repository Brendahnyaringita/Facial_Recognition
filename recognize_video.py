# python recognize_video.py --detector face_detection_model \
#	--embedding-model openface_nn4.small2.v1.t7 \
#	--recognizer output/recognizer.pickle \
#	--le output/le.pickle--le output/le.pickle


from imutils.video import VideoStream
from imutils.video import FPS
from imutils.video import WebcamVideoStream
import numpy as np
import argparse
import imutils
import pickle
import time
import cv2
import os
import scipy.misc
import threading
from multiprocessing.pool import ThreadPool
import logging

# SMS handler; class smshandler  
from sms_handler import smshandler

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--detector", required=True,
	help="path to OpenCV's deep learning face detector")
ap.add_argument("-m", "--embedding-model", required=True,
	help="path to OpenCV's deep learning face embedding model")
ap.add_argument("-r", "--recognizer", required=True,
	help="path to model trained to recognize faces")
ap.add_argument("-l", "--le", required=True,
	help="path to label encoder")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

def face_classifier(facedimensions):

	#converting the array to an image
	faceDimensions = scipy.misc.toimage(facedimensions)
	# construct a blob for the face ROI, then pass the blob
	# through our face embedding model to obtain the 128-d
	# quantification of the face
	faceBlob = cv2.dnn.blobFromImage(faceDimensions, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
	embedder.setInput(faceBlob)
	vec = embedder.forward()
	predictions = recognizer.predict_proba(vec)[0]
	j = np.argmax(predictions)
	probability = predictions[j]
	return probability,j


# load our serialized face detector from disk
print("[INFO] loading face detector...")
protoPath = os.path.sep.join([args["detector"], "deploy.prototxt"])
modelPath = os.path.sep.join([args["detector"],
	"res10_300x300_ssd_iter_140000.caffemodel"])
detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

# load our serialized face embedding model from disk
print("[INFO] loading face recognizer...")
embedder = cv2.dnn.readNetFromTorch(args["embedding_model"])

# load the actual face recognition model along with the label encoder
recognizer = pickle.loads(open(args["recognizer"], "rb").read())
le = pickle.loads(open(args["le"], "rb").read())

# initialize the video stream, then allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = WebcamVideoStream(src = 0).start()
#vs = VideoStream(src=0).start()
#time.sleep(2.0)

# start the FPS throughput estimator
fps = FPS().start()

result = ""
message_handler = smshandler()

# loop over frames from the video file stream
while True:
	# grab the frame from the threaded video stream
	frame = vs.read()

	# resize the frame to have a width of 600 pixels (while
	# maintaining the aspect ratio), and then grab the image
	# dimensions
	frame = imutils.resize(frame, width=600)
	(h, w) = frame.shape[:2]

	# construct a blob from the image
	imageBlob = cv2.dnn.blobFromImage(
		cv2.resize(frame, (300, 300)), 1.0, (300, 300),
		(104.0, 177.0, 123.0), swapRB=False, crop=False)

	# apply OpenCV's deep learning-based face detector to localize
	# faces in the input image
	detector.setInput(imageBlob)
	detections = detector.forward()

	# loop over the detections
	#This step is for processing the detections
	for i in range(0, detections.shape[2]):
		# extract the confidence (i.threshold., probability) associated with
		# the prediction
		confidence = detections[0, 0, i, 2]

		# filter out weak detections
		if confidence > args["confidence"]:
			# compute the (x, y)-coordinates of the bounding box for
			# the face
			boundingBox = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = boundingBox.astype("int")

			# extract the face ROI
			faceDimensions = frame[startY:endY, startX:endX]
			(fH, fW) = faceDimensions.shape[:2]


			# ensure the face width and height are sufficiently large
			if fW < 20 or fH < 20:
				continue

			# # construct a blob for the face ROI, then pass the blob
			# # through our face embedding model to obtain the 128-d
			# # quantification of the face
			# faceBlob = cv2.dnn.blobFromImage(faceDimensions, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
			# embedder.setInput(faceBlob)
			# vec = embedder.forward()
            #
			# # perform classification to recognize the face
			# predictions = recognizer.predict_proba(vec)[0]
			# j = np.argmax(predictions)
			#
			# probability = predictions[j]

			print("Starting recognizer thread")
			pool = ThreadPool(processes=1)
			faceDimension = scipy.misc.toimage(faceDimensions)
			async_result = pool.apply_async(face_classifier,[np.asarray(faceDimensions)])


			threshold = 0.90
			truthValue = 0.55
			probability,j = async_result.get()


			if probability > truthValue:
				name = le.classes_[j]
				
			else:
				name = "unknown"

			if probability > threshold:
				result = le.classes_[j]
				# If there is >90 % probability do something
				# Here for example the capturing will be paused for a couple of seconds(10) after sending sms

				message_handler.sendsms(name)
				time.sleep(10)


			# draw the bounding box of the face along with the
			# associated probability
			text = "{}: {:.2f}%".format(name, probability * 100)
			y = startY - 10 if startY - 10 > 10 else startY + 10
			cv2.rectangle(frame, (startX, startY), (endX, endY),
				(0, 0, 255), 2)
			cv2.putText(frame, text, (startX, y),
			cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

	# update the FPS counter
	fps.update()

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	print(result)

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break





# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()