from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import mediapipe as mp
from count_reps import count_reps
import datetime


app = Flask(__name__)
model = load_model("models/LSTM_Attention_128HUs.h5")
pose = mp.solutions.pose.Pose()


SEQUENCE_LENGTH = 40
actions = np.array(['barbell biceps curl', 'bench press', 'chest fly machine', 'deadlift', 'decline bench press',
                    'hammer curl', 'hip thrust', 'incline bench press', 'lat pulldown', 'lateral raise',
                    'leg extension', 'leg raises', 'plank', 'pull Up', 'push-up', 'romanian deadlift',
                    'russian twist', 'shoulder press', 'squat', 't bar row', 'tricep Pushdown', 'tricep dips'])


@app.route('/exercise')
def exercise():
    return render_template('exercise.html')


@app.route('/')
def index():
    return render_template('index.html')


def extract_keypoints(results):
    return np.array([[res.x, res.y, res.z, res.visibility]
                    for res in results.pose_landmarks.landmark]).flatten()


current_action = ''
rep = 0
state = None
start = 0


def gen_frames():
    global current_action
    global rep
    global state
    global start
    current_action = ''
    rep = 0
    state = None
    sequence = []

    start = datetime.datetime.now()

    # cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture("./dataset/squat/squat_13.mp4")
    # cap = cv2.VideoCapture('./dataset/hammer curl/hammer curl_19.mp4')
    # cap = cv2.VideoCapture('./dataset/shoulder press/shoulder press_12.mp4') #
    # cap = cv2.VideoCapture('./dataset/barbell biceps curl/barbell biceps curl_46.mp4')

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Pose estimation and recognition logic
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            landmarks = extract_keypoints(results)
            mp.solutions.drawing_utils.draw_landmarks(
                frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)
        else:
            continue

        sequence.append(landmarks)

        if len(sequence) == SEQUENCE_LENGTH:
            res = model.predict(np.expand_dims(sequence, axis=0), verbose=0)[0]
            current_action = actions[np.argmax(res)]
            confidence = np.max(res)

            if confidence < 0.8:
                current_action = ''

        rep, state = count_reps(current_action, frame, results, rep, state)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_exercise')
def get_exercise():
    global current_action
    global rep
    global start

    return jsonify({'exercise': current_action, 'rep': rep, 'duration': start})


if __name__ == "__main__":
    app.run(debug=True)
