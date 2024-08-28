from distutils.command.clean import clean
from pathlib import Path

import cv2
import pybgs as bgs
from PIL.ImageChops import overlay

import pandas as pd


# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def find_contours(diff_frame):
    contours, _ = cv2.findContours(diff_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rgb_frame = cv2.cvtColor(diff_frame, cv2.COLOR_GRAY2BGR)
    bounding_boxes = []

    # Loop through each detected contour
    for contour in contours:
        # Get the bounding box for the contour
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(rgb_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        bounding_boxes.append((x, y, w, h))
    return rgb_frame

def cleanup_diff(diff_frame):
    diff_frame = cv2.cvtColor(diff_frame, cv2.COLOR_BGR2GRAY)
    # diff_frame = cv2.threshold(diff_frame, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    diff_frame = cv2.GaussianBlur(diff_frame, (5, 5), 0)
    _, diff_frame = cv2.threshold(diff_frame, 50, 255, cv2.THRESH_TOZERO)
    diff_frame = cv2.medianBlur(diff_frame, 5)
    diff_frame = cv2.threshold(diff_frame, 50, 255, cv2.THRESH_BINARY)[1]
    diff_frame = cv2.dilate(diff_frame, None, iterations=2)
    return diff_frame

def frame_diff(frame1, frame2):
    diff = cv2.absdiff(frame1, frame2)
    cv2.normalize(diff, diff, 0, 255, cv2.NORM_MINMAX)
    return diff



def diff_overlay(raw_frame, diff_frame):
    diff_frame[:, :, 2] = 0  # Set the red channel to zero to make it cyan
    overlay = cv2.addWeighted(raw_frame, 0.7, diff_frame, 0.3, 0)
    return  overlay

def frame_iter(video_path):
    # for some reason, the video is 30fps, but the frames are 60fps and every other frame has no droplets
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    if success:
        yield image  # Yield the first frame
    frame_count = 1
    while success:
        success, image = vidcap.read()
        if success and frame_count % 2 != 0:
            yield image
        frame_count += 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    frame_count = 0
    prev_frame = None

    diff_path = Path("Rail_vids/diff")
    overlay_path = Path("Rail_vids/overlay")
    overlay_path.mkdir(exist_ok=True)
    diff_path.mkdir(exist_ok=True)
    diff_back_path = Path("Rail_vids/diff_back")
    diff_back_path.mkdir(exist_ok=True)
    roi_path = Path("Rail_vids/rois")
    roi_path.mkdir(exist_ok=True)

    frame_path = Path("Rail_vids/frames")
    avg_path = Path("Rail_vids/AVG_diff_back.jpg")
    base_img = cv2.imread(str(frame_path / "frame_0.jpg"))
    base_avg = cv2.imread(str(avg_path))

    back_sub = cv2.bgsegm.createBackgroundSubtractorGSOC()

    num_of_channels = 2

    rois = []
    for channel in range(num_of_channels):
        x, y, w, h = cv2.selectROI(f"Select {channel}", base_img, fromCenter=False, showCrosshair=True)
        roi = {
            "channel": channel,
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "br_x": x + w,
            "br_y": y + h
        }
        rois.append(roi)


    datapoints = []

    for frame in frame_iter("Rail_vids/DEV1 PH8 10X 100_BF_01.mp4"):
        print(f"frame_count: {frame_count}")
        if prev_frame is not None:
            diff = frame_diff(prev_frame, frame)
            diff_back = frame_diff(base_img, frame)
            diff_back2 = frame_diff(diff_back, base_avg)
            diff_clean = cleanup_diff(diff_back2)
            overlay = diff_overlay(frame, cv2.cvtColor(diff_clean, cv2.COLOR_GRAY2BGR))

            cv2.imwrite(str(diff_back_path / f"{frame_count}.jpg"), diff_clean)
            contours = find_contours(diff_clean)
            cv2.imwrite(str(overlay_path / f"{frame_count}.jpg"), overlay)
            cv2.imshow('FG Mask', contours)

            keyboard = cv2.waitKey(10)
            data = {"frame_count": frame_count}
            for roi in rois:
                data.update(roi)
                data["mean"] = diff_back2[roi["y"]:roi["br_y"], roi["x"]:roi["br_x"]].mean()
                data["max"] = diff_back2[roi["y"]:roi["br_y"], roi["x"]:roi["br_x"]].max()
                data["min"] = diff_back2[roi["y"]:roi["br_y"], roi["x"]:roi["br_x"]].min()
                cv2.imwrite(str(roi_path / f"{frame_count}_{roi['channel']}.jpg"), diff_back2[roi["y"]:roi["br_y"], roi["x"]:roi["br_x"]])
            datapoints.append(data)

        prev_frame = frame
        frame_count += 1

    # df = pd.DataFrame(datapoints)
    # df.to_csv("Rail_vids/diff.csv")
    # df.to_excel("Rail_vids/diff.xlsx")


            # cv2.imwrite(str(overlay_path / f"{frame_count}.jpg"), overlay)
            # cv2.imwrite(str(diff_path / f"{frame_count}.jpg"), diff)





# See PyCharm help at https://www.jetbrains.com/help/pycharm/
