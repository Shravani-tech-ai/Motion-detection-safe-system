import threading
import winsound
import cv2
import imutils
import numpy as np
import mail
import time

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

_, start_frame = cap.read()
start_frame = imutils.resize(start_frame, width=500)
start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

alarm = False
alarm_mode = False
alarm_counter = 0
pause_motion_detection = False

MAX_BEEP_COUNT = 10

def beep_alarm():
    global alarm, alarm_mode, alarm_counter, pause_motion_detection
    beep_count = 0
    while alarm_mode and beep_count < MAX_BEEP_COUNT:
        print("ALARM")
        winsound.Beep(2500, 1000)  # Beep at 2500 Hz for 1000 ms (1 second)
        beep_count += 1
    # Deactivate the alarm after beeping 10 times
    alarm = False
    alarm_counter = 0  # Reset the counter so motion detection resumes
    print("Alarm deactivated after 10 beeps, pausing motion detection for 20 seconds.")
    pause_motion_detection = True  # Pause motion detection for 20 seconds
    time.sleep(20)  # Wait for 20 seconds before resuming motion detection
    pause_motion_detection = False  # Resume motion detection

while True:
    if not pause_motion_detection:  # Only run motion detection if not paused
        _, frame = cap.read()
        frame = imutils.resize(frame, width=500)

    if alarm_mode:
        frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)

        difference = cv2.absdiff(start_frame, frame_bw)
        threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]
        start_frame = frame_bw

        if threshold.sum() > 10000: # This is the sensitivity of the motion detection
            alarm_counter += 1
            if alarm_counter > 20:
                if not alarm:
                    alarm = True
                    threading.Thread(target=beep_alarm).start()
                    threading.Thread(target=mail.send_email, args=(frame, frame)).start()
        else:
            if alarm_counter > 0:
                alarm_counter -= 1
        cv2.imshow("Cam", threshold)
    elif not alarm_mode and alarm:
        black_frame = np.zeros_like(frame)
        cv2.imshow("Cam", black_frame)
    else:
        cv2.imshow("Cam", frame)

    key_pressed = cv2.waitKey(30)
    if key_pressed == ord('t'):
        print("You have activated/deactivated the alarm!")
        alarm_mode = not alarm_mode
        alarm_counter = 0
    elif key_pressed == ord('q'):
        print("Quitting the program!")
        alarm_mode = False
        break

cap.release()
cv2.destroyAllWindows()
