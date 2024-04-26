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
mp_drawing = mp.solutions.drawing_utils
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


SEQUENCE_LENGTH = 40
actions = np.array(['barbell biceps curl', 'bench press',
                    'hammer curl', 'hip thrust',  'lat pulldown', 'leg raises',  'pull up', 'push up', 'shoulder press', 'squat'])


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
is_body_present = False
is_face_present = False
is_proper_lighting = False


def perform_quality_control(frame):
    global is_body_present
    global is_face_present
    global is_proper_lighting

    # Convert frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Perform pose estimation with MediaPipe
    results = pose.process(rgb_frame)

    # Check if body is present
    is_body_present = results.pose_landmarks is not None

    # Perform face detection with Haar cascade classifier
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    is_face_present = len(faces) > 0

    # Check for proper lighting
    mean_intensity = cv2.mean(gray)[0]  # Mean intensity of the frame
    is_proper_lighting = mean_intensity > 100  # Adjust this threshold as needed

    # Overlay text boxes on the frame
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    font_color = (100, 255, 0)
    line_thickness = 1

    # Display face detection result
    face_text = "Face Present" if is_face_present else "Face Not Present"
    cv2.putText(frame, face_text, (420, 20), font,
                font_scale, font_color, line_thickness)

    # Display body detection result
    body_text = "Body Present" if is_body_present else "Body Not Present"
    cv2.putText(frame, body_text, (420, 50), font,
                font_scale, font_color, line_thickness)

    # Display proper lighting check result
    lighting_text = "Proper Lighting" if is_proper_lighting else "Low Lighting"
    cv2.putText(frame, lighting_text, (420, 80), font,
                font_scale, font_color, line_thickness)

    return frame


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

    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture('./dataset/barbell biceps curl/barbell biceps curl_46.mp4')
    # cap = cv2.VideoCapture("./dataset/squat/squat_13.mp4")
    # cap = cv2.VideoCapture('./dataset/shoulder press/shoulder press_11.mp4')
    # cap = cv2.VideoCapture('./dataset/push up/push-up_3.mp4')
    # cap = cv2.VideoCapture('./dataset/pull up/pull up_13.mp4')
    # cap = cv2.VideoCapture('./dataset/lat pulldown/lat pulldown_1.mp4')
    # cap = cv2.VideoCapture('./dataset/bench press/bench press_31.mp4')
    # cap = cv2.VideoCapture('./dataset/hammer curl/hammer curl_19.mp4')
    # cap = cv2.VideoCapture('./dataset/hip thrust/hip thrust_10.mp4')
    # cap = cv2.VideoCapture('./dataset/leg raises/leg raises_10.mp4')

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

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            continue
        
        # frame = perform_quality_control(frame)
        
        # # if (not is_body_present or not is_face_present or not is_proper_lighting):
        # #     ret, buffer = cv2.imencode('.jpg', frame)
        # #     frame = buffer.tobytes()

        # #     yield (b'--frame\r\n'
        # #            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # #     continue

        sequence.append(landmarks)

        if len(sequence) >= SEQUENCE_LENGTH:
            res = model.predict(np.expand_dims(
                sequence[-SEQUENCE_LENGTH:], axis=0), verbose=0)[0]
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

    return jsonify({'exercise': current_action, 'rep': rep, 'duration': start, 'is_body_present': is_body_present ,'is_face_present':  is_face_present,'is_proper_lighting': is_proper_lighting})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
