from pathlib import Path

import cv2
from PIL.ImageChops import overlay

import pandas as pd


# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def frame_diff(frame1, frame2):
    diff = cv2.absdiff(frame1, frame2)
    cv2.normalize(diff, diff, 0, 255, cv2.NORM_MINMAX)
    return diff



def diff_overlay(raw_frame, diff_frame):
    diff_frame[:, :, 2] = 0  # Set the red channel to zero to make it cyan
    overlay = cv2.addWeighted(raw_frame, 0.3, diff_frame, 0.7, 0)
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

    frame_path = Path("Rail_vids/frames")
    base_img = cv2.imread(str(frame_path / "frame_0.jpg"))


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
            overlay = diff_overlay(frame, diff)
            data = {"frame_count": frame_count}
            for roi in rois:
                data.update(roi)
                data["mean"] = diff[roi["y"]:roi["br_y"], roi["x"]:roi["br_x"]].mean()
                data["max"] = diff[roi["y"]:roi["br_y"], roi["x"]:roi["br_x"]].max()
                data["min"] = diff[roi["y"]:roi["br_y"], roi["x"]:roi["br_x"]].min()
                datapoints.append(data)

        prev_frame = frame
        frame_count += 1

    df = pd.DataFrame(datapoints)
    df.to_csv("Rail_vids/diff.csv")
    df.to_excel("Rail_vids/diff.xlsx")


            # cv2.imwrite(str(overlay_path / f"{frame_count}.jpg"), overlay)
            # cv2.imwrite(str(diff_path / f"{frame_count}.jpg"), diff)





# See PyCharm help at https://www.jetbrains.com/help/pycharm/
