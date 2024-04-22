import cv2
import numpy as np
from enum import Enum
import math

CONFIDENCE_THRESHOLD = 0.2


class Keypoint(Enum):
    NOSE = 0
    RIGHT_EYE = 2
    LEFT_EYE = 5
    RIGHT_EAR = 7
    LEFT_EAR = 8
    RIGHT_SHOULDER = 11
    LEFT_SHOULDER = 12
    RIGHT_ELBOW = 13
    LEFT_ELBOW = 14
    RIGHT_WRIST = 15
    LEFT_WRIST = 16
    RIGHT_HIP = 23
    LEFT_HIP = 24
    RIGHT_KNEE = 25
    LEFT_KNEE = 26
    RIGHT_ANKLE = 27
    LEFT_ANKLE = 28

    def __int__(self):
        return self.value

    @classmethod
    def all_keypoints(cls):
        return {key.name: key.value for key in cls}


class Edges(Enum):
    NOSE_TO_RIGHT_EYE = (Keypoint.NOSE, Keypoint.RIGHT_EYE, 'm')
    NOSE_TO_LEFT_EYE = (Keypoint.NOSE, Keypoint.LEFT_EYE, 'c')
    RIGHT_EYE_TO_RIGHT_EAR = (Keypoint.RIGHT_EYE, Keypoint.RIGHT_EAR, 'm')
    LEFT_EYE_TO_LEFT_EAR = (Keypoint.LEFT_EYE, Keypoint.LEFT_EAR, 'c')
    NOSE_TO_RIGHT_SHOULDER = (Keypoint.NOSE, Keypoint.RIGHT_SHOULDER, 'm')
    NOSE_TO_LEFT_SHOULDER = (Keypoint.NOSE, Keypoint.LEFT_SHOULDER, 'c')
    RIGHT_SHOULDER_TO_RIGHT_ELBOW = (
        Keypoint.RIGHT_SHOULDER, Keypoint.RIGHT_ELBOW, 'm')
    LEFT_SHOULDER_TO_LEFT_ELBOW = (
        Keypoint.LEFT_SHOULDER, Keypoint.LEFT_ELBOW, 'c')
    RIGHT_ELBOW_TO_RIGHT_WRIST = (
        Keypoint.RIGHT_ELBOW, Keypoint.RIGHT_WRIST, 'm')
    LEFT_ELBOW_TO_LEFT_WRIST = (Keypoint.LEFT_ELBOW, Keypoint.LEFT_WRIST, 'c')
    RIGHT_SHOULDER_TO_RIGHT_HIP = (
        Keypoint.RIGHT_SHOULDER, Keypoint.RIGHT_HIP, 'm')
    LEFT_SHOULDER_TO_LEFT_HIP = (
        Keypoint.LEFT_SHOULDER, Keypoint.LEFT_HIP, 'c')
    RIGHT_HIP_TO_RIGHT_KNEE = (Keypoint.RIGHT_HIP, Keypoint.RIGHT_KNEE, 'm')
    LEFT_HIP_TO_LEFT_KNEE = (Keypoint.LEFT_HIP, Keypoint.LEFT_KNEE, 'c')
    RIGHT_KNEE_TO_RIGHT_ANKLE = (
        Keypoint.RIGHT_KNEE, Keypoint.RIGHT_ANKLE, 'm')
    LEFT_KNEE_TO_LEFT_ANKLE = (Keypoint.LEFT_KNEE, Keypoint.LEFT_ANKLE, 'c')
    LEFT_SHOULDER_TO_RIGHT_SHOULDER = (
        Keypoint.LEFT_SHOULDER, Keypoint.RIGHT_SHOULDER, 'y')
    LEFT_HIP_TO_RIGHT_HIP = (Keypoint.LEFT_HIP, Keypoint.RIGHT_HIP, 'y')

    @classmethod
    def all_edges(cls):
        return [(edge.value[0].value, edge.value[1].value, edge.value[2]) for edge in cls]


def calculate_angle(frame, keypoints, keypoint1, keypoint2, keypoint3):
    y, x, _ = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))

    keypoint1_coordinate = shaped[int(keypoint1)]
    keypoint2_coordinate = shaped[int(keypoint2)]
    keypoint3_coordinate = shaped[int(keypoint3)]

    # Convert normalized coordinates to pixel coordinates
    y_scale, x_scale = 1.0, 1.0
    kp1_x, kp1_y = keypoint1_coordinate[0] * \
        x_scale, keypoint1_coordinate[1] * y_scale
    kp2_x, kp2_y = keypoint2_coordinate[0] * \
        x_scale, keypoint2_coordinate[1] * y_scale
    kp3_x, kp3_y = keypoint3_coordinate[0] * \
        x_scale, keypoint3_coordinate[1] * y_scale

    # Calculate vectors
    vector1 = np.array([kp1_x - kp2_x, kp1_y - kp2_y])
    vector2 = np.array([kp3_x - kp2_x, kp3_y - kp2_y])

    # Calculate dot product
    dot_product = np.dot(vector1, vector2)

    # Calculate magnitudes
    magnitude1 = np.linalg.norm(vector1)
    magnitude2 = np.linalg.norm(vector2)

    # Calculate cosine of the angle
    cosine_angle = dot_product / (magnitude1 * magnitude2)

    # Calculate the angle in radians
    angle_rad = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

    # Convert angle to degrees
    angle_deg = np.degrees(angle_rad)

    return angle_deg


def count_reps(exercise_type, frame, results, rep=0, state=None):
    y, x, _ = frame.shape

    keypoints_with_scores = [(landmark.x,
                              landmark.y,
                              landmark.visibility)
                             for landmark in results.pose_landmarks.landmark]

    shaped = np.squeeze(np.multiply(keypoints_with_scores, [y, x, 1]))

    if exercise_type == "hammer curl" or exercise_type == "barbell biceps curl":

        angle = calculate_angle(frame, keypoints_with_scores,  Keypoint.LEFT_SHOULDER,
                                Keypoint.LEFT_ELBOW, Keypoint.LEFT_WRIST)

        if angle == None:
            return
        if angle < 30:
            state = "up"
        if angle > 140 and state == 'up':
            state = "down"
            rep += 1
        if angle > 140 and state == None:
            state = "down"

        shoulder_keypoint = shaped[int(Keypoint.LEFT_ELBOW)]
        kp_x, kp_y = int(shoulder_keypoint[0]), int(shoulder_keypoint[1])

        cv2.putText(frame, f'{angle:.2f}', (kp_x, kp_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    elif exercise_type == "squat":

        # Calculate knee angles
        left_knee_angle = calculate_angle(
            frame, keypoints_with_scores, Keypoint.LEFT_HIP, Keypoint.LEFT_KNEE, Keypoint.LEFT_ANKLE)
        right_knee_angle = calculate_angle(
            frame, keypoints_with_scores, Keypoint.RIGHT_HIP, Keypoint.RIGHT_KNEE, Keypoint.RIGHT_ANKLE)

        # Calculate hip angles
        left_hip_angle = calculate_angle(
            frame, keypoints_with_scores, Keypoint.LEFT_SHOULDER, Keypoint.LEFT_HIP, Keypoint.LEFT_KNEE)
        right_hip_angle = calculate_angle(
            frame, keypoints_with_scores, Keypoint.RIGHT_SHOULDER, Keypoint.RIGHT_HIP, Keypoint.RIGHT_KNEE)

        if (left_knee_angle == None or right_knee_angle == None or left_hip_angle == None or right_hip_angle == None):
            return

        thr = 135
        if (left_knee_angle < thr) and (right_knee_angle < thr) and (left_hip_angle < thr) and (right_hip_angle < thr):
            state = "down"
        if (left_knee_angle > thr) and (right_knee_angle > thr) and (left_hip_angle > thr) and (right_hip_angle > thr) and (state == 'down'):
            state = 'up'
            rep += 1
        if (left_knee_angle > thr) and (right_knee_angle > thr) and (left_hip_angle > thr) and (right_hip_angle > thr) and (state == None):
            state = 'up'

    elif exercise_type == "shoulder press" or exercise_type == "pull up" or exercise_type == "lat pulldown":

        elbow_angle = calculate_angle(frame, keypoints_with_scores,  Keypoint.LEFT_SHOULDER,
                                      Keypoint.LEFT_ELBOW, Keypoint.LEFT_WRIST)

        # Compute distances between joints
        shoulder2elbow_dist = abs(math.dist(
            shaped[int(Keypoint.LEFT_SHOULDER)], shaped[int(Keypoint.LEFT_ELBOW)]))
        shoulder2wrist_dist = abs(math.dist(
            shaped[int(Keypoint.LEFT_SHOULDER)], shaped[int(Keypoint.LEFT_WRIST)]))

        if (elbow_angle > 130) and (shoulder2elbow_dist < shoulder2wrist_dist):
            state = "up"
        if (elbow_angle < 50) and (shoulder2elbow_dist > shoulder2wrist_dist) and (state == 'up'):
            state = 'down'
            rep += 1
        if (elbow_angle < 50) and (shoulder2elbow_dist > shoulder2wrist_dist) and (state == None):
            state = 'down'

    elif exercise_type == "push up" :

        elbow_angle = calculate_angle(frame, keypoints_with_scores,  Keypoint.LEFT_SHOULDER,
                                      Keypoint.LEFT_ELBOW, Keypoint.LEFT_WRIST)

        if (elbow_angle > 130):
            state = "up"
        if (elbow_angle < 80) and (state == 'up'):
            state = 'down'
            rep += 1
        if (elbow_angle < 80) and (state == None):
            state = 'down'

    elif exercise_type =="bench press":
            shoulder2elbow_dist = abs(math.dist(
                shaped[int(Keypoint.LEFT_SHOULDER)], shaped[int(Keypoint.LEFT_ELBOW)]))
            shoulder2wrist_dist = abs(math.dist(
                shaped[int(Keypoint.LEFT_SHOULDER)], shaped[int(Keypoint.LEFT_WRIST)]))
           
            if (shoulder2elbow_dist < shoulder2wrist_dist):
                state = "up"
            if  (shoulder2elbow_dist > shoulder2wrist_dist) and (state == 'up'):
                state = 'down'
                rep += 1
            if  (shoulder2elbow_dist > shoulder2wrist_dist) and (state == None):
                state = 'down'
                
    elif exercise_type == "hip thrust":
            
        left_hip_angle = calculate_angle(
            frame, keypoints_with_scores, Keypoint.LEFT_SHOULDER, Keypoint.LEFT_HIP, Keypoint.LEFT_KNEE)
        right_hip_angle = calculate_angle(
            frame, keypoints_with_scores, Keypoint.RIGHT_SHOULDER, Keypoint.RIGHT_HIP, Keypoint.RIGHT_KNEE)
        
        thr = 150
        
        if (left_hip_angle < thr):
            state = "down"
        if  (left_hip_angle > thr) and (state == 'down'):
            state = 'up'
            rep += 1
        if  (left_hip_angle > thr)  and (state == None):
            state = 'up'
    
    elif exercise_type == "leg raises":
            
        left_hip_angle = calculate_angle(
            frame, keypoints_with_scores, Keypoint.LEFT_SHOULDER, Keypoint.LEFT_HIP, Keypoint.LEFT_KNEE)
        right_hip_angle = calculate_angle(
            frame, keypoints_with_scores, Keypoint.RIGHT_SHOULDER, Keypoint.RIGHT_HIP, Keypoint.RIGHT_KNEE)
        
        thr = 160
        
        if (left_hip_angle < thr):
            state = "up"
        if  (left_hip_angle > thr) and (state == 'up'):
            state = 'down'
            rep += 1
        if  (left_hip_angle > thr)  and (state == None):
            state = 'down'
        
        
    else:
        pass

    return rep, state
