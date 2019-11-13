import sys, os, cv2
from IPython.display import clear_output


def new_directory(path):
    if not os.path.isdir(os.path.join(os.getcwd(), path)):
        os.mkdir(path)

def extract_video(src, dest):
    # Extract the frames from original video
    framenumber = 0
    framectr = 0
    omovie = cv2.VideoCapture(src)
    frame_height = omovie.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frame_width = omovie.get(cv2.CAP_PROP_FRAME_WIDTH)

    while(1):
        ret, frame = omovie.read()
        if not ret:
            break
        print('Extracting: %d' % framenumber)
        clear_output(wait=True)
        cv2.imwrite(dest % framenumber, frame)
        framenumber += 1

    omovie.release()


new_directory('frames')
new_directory('composite')
extract_video('monkey.mov', 'frames/%d.tif')
