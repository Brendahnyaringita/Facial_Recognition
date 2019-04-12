#! /bin/bash

# Makes it exec .. chmod +x run_video.sh

python recognize_video.py --detector face_detection_model --embedding-model output/openface_nn4.small2.v1.t7 --recognizer output/recognizer.pickle --le output/le.pickle