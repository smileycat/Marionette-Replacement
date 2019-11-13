from IPython.display import clear_output
from matplotlib import pyplot as plt
import cv2, glob, random
import numpy as np


'''
1. Look for red points where [x, y] == 1
2. if [x, y] is in threshold of some Segment S
3. add the coordinate into Segment S and average S
4. such that S = [avg_x, avg_y, coord_list_x, coord_list_y]
5. if not then throw the coordinate into a new part n+1
'''
def segmentation_alg(segments, x, y):
    # First element
    if not segments:
        segments.append([[x], [y]])
        return segments

    diff = []
    k = 40 # the minimum distance between coordinates
    # Find the closest segment S for coordinate (x, y)
    for coordx, coordy in segments:
        diff.append(abs(x-np.mean(coordx)) + abs(y-np.mean(coordy)))

    # if the difference between (x, y) and (avg_x, avg_y) in 
    # closest segment is within threshold, add element to the segment.
    if min(diff) < k:
        min_index = diff.index(min(diff))

        x_list, y_list = segments.pop(min_index)
        x_list.append(x)
        y_list.append(y)

        segments.insert(0, [x_list, y_list])
    else:
        segments.append([[x], [y]])

    return segments


''' Each 'part' detected must contain some number n of coordinates
    such that n > threshold in order to be a valid part.
    Input: binary map (e.g. redmap)
    Output: sorted coordinates of each part. e.g. ([1, 2], [1, 3])
'''
def find_parts(binary_map):
    segments = []
    parts = []
    threshold = 30

    for x in range(binary_map.shape[0]):
        for y in range(binary_map.shape[1]):
            if binary_map[x, y] == 1:
                segments = segmentation_alg(segments, x, y)

    # Add all segments Si if no. of coordinates in Si is greater than threshold
    for s in segments:
        if len(s[0]) > threshold:
            center_x = int(np.mean(s[0]))
            center_y = int(np.mean(s[1]))
            parts.append([center_x, center_y])

    return sorted(parts , key=lambda k: [k[0], k[1]])


def load_custom_background(height, width):
    bg_frames = []

    for i in range (15):
        img = cv2.imread('bg_frames/frame%d.jpg' % i)
        bg_frames.append(img[0:height, 0:width])

    return bg_frames


def replace_bluescreen(img, bg_img):
    background = 180
    threshold = 20
    
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j, 0] > img[i, j, 1] and img[i, j, 0] > img[i, j, 2] and (img[i, j, 0] - img[i, j, 1]) + (img[i, j, 0] - img[i, j, 1]) > 10:
                img[i, j] = bg_img[i, j]

    return img


''' Find all the red points in the given image 'frame' and returns
    'redmap' - a binary binary_map such that all red points are 1 and non-red 
    points are 0
'''
def find_markers(frame):
    redmap = np.zeros((frame.shape[0], frame.shape[1]))

    for x in range(redmap.shape[0]):
        for y in range(redmap.shape[1]):
            if frame[x, y, 2] > red and (frame[x, y, 2] - 100 > frame[x, y, 1]) and (frame[x, y, 2]-100 > frame[x, y, 0]):
                redmap[x, y] = 1
            else:
                redmap[x, y] = 0

    return redmap

''' Draw circles for each red part of the monkey and connect each circle
    to the body (center circle) by a line, imitating monkey's motion
'''
def draw_shapes(img, parts):
    # Draw circles for the red parts of monkey
    for y, x in parts:
        cv2.circle(img, (x, y), 18, (255, 255, 255), -1)

    # Draw lines and connect 5 circles if exact 5 parts are found
    if len(parts) != 5:
        return img

    # leg 1, 2
    l2x, l2y = parts.pop(4)
    l1x, l1y = parts.pop(3)

    # Here we sort the remaining parts once again because of my assumption:
    # I assume the body part is within the first 3 elements; in other words,
    # I assume the body has a lower y-axis value (from top to bottom) than the feet.
    # So then now parts[0:3] are 2 arms and body. x-axis wise, body is assumed
    # to be in the middle value.
    # print('b', parts)
    parts = sorted(parts , key=lambda k: [k[1], k[0]])

    # hand 1, 2
    h1x, h1y = parts[0]
    h2x, h2y = parts[2]
    # body
    bx, by = parts[1]
    #head
    headx = (bx-120) if (bx-120) >= 0 else 0
    heady = by-(person_face.shape[1] // 2)

    # Draw head
    for i in range(person_face.shape[0]):
        for j in range(person_face.shape[1]):
            if person_face[i, j, 0] > 200:
                img[i+headx, j+heady] = person_face[i, j]

    # Draw body
    cv2.rectangle(img, (by-20, bx-40), (by+20, bx+40), (255,255,255), -1)

    # Connect hands and legs with body
    cv2.line(img, (h1y, h1x), (by, bx), (255,255,255), 12)
    cv2.line(img, (h2y, h2x), (by, bx), (255,255,255), 12)
    cv2.line(img, (l1y, l1x), (by, bx), (255,255,255), 12)
    cv2.line(img, (l2y, l2x), (by, bx), (255,255,255), 12)
    cv2.line(img, (heady+50, headx+100), (by, bx), (255,255,255), 20)

    return img



person_face = cv2.imread('face.jpg')
print(person_face.shape)
bg_frames = load_custom_background(320, 568)
bgctr = 0
tot_frame = len(glob.glob('frames/*.tif')) # No. of tif files in the directory
cur_frame = 0
red = 150

fourcc = cv2.VideoWriter_fourcc(*'MP4V')
out = cv2.VideoWriter('composite.mp4', fourcc, 30, (568,320))

while cur_frame < tot_frame:
    bg_frame = bg_frames[bgctr].copy()
    frame = cv2.imread('frames/%d.tif' % cur_frame)
    print('Processing frame: %d, overall progress: %.2f %%' % (cur_frame, cur_frame/tot_frame*100))
    clear_output(wait=True)
    
    # Replace blue screen background with custom background
    # frame = replace_bluescreen(frame, bg_frame)

    # Find the red markers on the monkey and segment them into parts.
    redmap = find_markers(frame)
    parts = find_parts(redmap)
    # Draw the circles and lines on new background
    frame = draw_shapes(bg_frame, parts)

    # Update the dynamic background every 3 frames
    if cur_frame % 3 == 0:
        bgctr = (bgctr + 1) if (bgctr < 14) else 0

    cv2.imwrite('composite/composite%d.tif' % cur_frame, bg_frame)
    out.write(frame)
    cv2.imshow('frame', bg_frame)
    if cv2.waitKey(30) & 0xff == ord('q'):
        break
    cur_frame += 1


out.release()
cv2.destroyAllWindows()