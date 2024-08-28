import trackpy as tp
import pims
import matplotlib.pyplot as plt
import pandas as pd

def show_image_with_wait(image):
    fig, ax = plt.subplots()
    ax.imshow(image, cmap='gray')
    plt.axis('off')

    def on_key(event):
        if event.key:
            plt.close(fig)

    fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show()

# Load the frames of differences
def load_frames(frame_dir):
    frames = pims.ImageSequence(frame_dir)
    return frames

if __name__ == '__main__':
    frames = load_frames("Rail_vids/diff_back/*.jpg")
    f = tp.batch(frames[:10], 11)
    t = tp.link(f, 5, memory=3)

    plt.figure()
    tp.plot_traj(t)

    # for frame in frames:
        # show_image_with_wait(frame)
    # tp.annotate(f, frames[:])

    f.to_excel("Rail_vids/track.xlsx")
    print(f)
