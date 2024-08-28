import trackpy as tp
import pims
import matplotlib.pyplot as plt

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
    frames = load_frames("Rail_vids/diff/*.jpg")
    for frame in frames:
        show_image_with_wait(frame)
        f = tp.locate(frame, 11)
        print(f)
