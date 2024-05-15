import cv2
import numpy as np
import os
from tensorflow.keras.models import load_model
import mediapipe as mp
from collections import Counter
from tqdm import tqdm
import datetime

model = load_model("models/LSTM_Attention_128HUs.h5")
pose = mp.solutions.pose.Pose()
mp_drawing = mp.solutions.drawing_utils
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

SEQUENCE_LENGTH = 40
actions = np.array(['barbell biceps curl', 'bench press',
                    'hammer curl', 'hip thrust',  'lat pulldown', 'leg raises',  'pull up', 'push up', 'shoulder press', 'squat'])
# actions = np.array([ 'squat'])
dataset_dir = "./dataset"

def extract_keypoints(results):
    return np.array([[res.x, res.y, res.z, res.visibility]
                    for res in results.pose_landmarks.landmark]).flatten()

for action in actions:
      action_dir = os.path.join(dataset_dir, action)
      if action != "shoulder press":
            continue
      # print(action, " - ", len(os.listdir(action_dir)))
      print("Action: ", action)
      mp4_files = [file for file in os.listdir(action_dir) if file.endswith(".mp4")]
      total_count = len(mp4_files)
      matched_count = 0
      for filename in tqdm(mp4_files):
            file_path = os.path.join(action_dir, filename)
            
            pred_action_array = []
            sequence = []
            current_action = ''
            
            cap = cv2.VideoCapture(file_path)

            while True:
                  ret, frame = cap.read()
                  if not ret:
                        break
                  
                  # Pose estimation and recognition logic
                  rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                  results = pose.process(rgb_frame)

                  if results.pose_landmarks:
                        landmarks = extract_keypoints(results)
                  else:
                      continue

                  sequence.append(landmarks)

                  if len(sequence) >= SEQUENCE_LENGTH:
                        res = model.predict(np.expand_dims(
                        sequence[-SEQUENCE_LENGTH:], axis=0), verbose=0)[0]
                        current_action = actions[np.argmax(res)]
                        confidence = np.max(res)

                        if confidence < 0.8:
                              current_action = ''
                        
                        pred_action_array.append(current_action)
                  
            # Count occurrences of each entry
            entry_counts = Counter(pred_action_array)

            # Find the entry with the maximum occurrence
            most_common_entry = entry_counts.most_common(1)[0][0]
            print("Predicted action for file - ", filename, " is: ", most_common_entry)
            
            if most_common_entry==action :
                  matched_count = matched_count + 1
      print("Accuracy for action - ", action, " is: ", (matched_count/total_count)*100)

      
