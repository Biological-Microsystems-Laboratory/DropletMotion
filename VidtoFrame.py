import cv2
from pathlib import Path

def vid_to_frame(video_path, frame_path):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    frame_path.mkdir(exist_ok=True)
    while success:
        cv2.imwrite(str(frame_path / f"frame_{count}.jpg"), image)  # save frame as JPEG file
        success, image = vidcap.read()
        print('Read a new frame: ', success)
        count += 1



vid_to_frame("Rail_vids/DEV1 PH8 10X 100_BF_01.mp4", Path("Rail_vids/frames"))