import io

import cv2
import imagehash
from PIL import Image, ImageChops

from consts import IMAGE_HASH_SIZE, FRAME_SAMPLE_INTERVAL, HASH_LIST_WINDOW_SIZE_IN_SECONDS, \
    LOOP_CHECK_INTERVAL_IN_SECONDS, LOOP_MIN_OCCURRENCES, LOOP_MIN_DURATION_IN_SECONDS, LOOP_DIFF_MARGIN_ERROR, \
    INPUT_FPS
from utils import has_looped_item


def main() -> None:
    cap = cv2.VideoCapture('./looped-video.mp4')
    # cap = cv2.VideoCapture('rtsp://192.168.132.115:8080/h264_ulaw.sdp')

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    fps = INPUT_FPS if INPUT_FPS else cap.get(cv2.CAP_PROP_FPS)
    print(f"Frame rate: {fps}")

    effective_fps = fps / FRAME_SAMPLE_INTERVAL
    hash_list_size = effective_fps * HASH_LIST_WINDOW_SIZE_IN_SECONDS
    loop_check_interval = effective_fps * LOOP_CHECK_INTERVAL_IN_SECONDS
    loop_min_size = effective_fps * LOOP_MIN_DURATION_IN_SECONDS

    frame_count = 0
    frames_diff_hashes: list[str] = []
    previous_frame_pil: Image = None

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        if frame_count % FRAME_SAMPLE_INTERVAL:
            continue

        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img_bytes = io.BytesIO()
        frame_pil.save(img_bytes, format='PNG')

        if previous_frame_pil:
            diff = ImageChops.difference(frame_pil, previous_frame_pil)
            diff = diff.convert('L')  # Convert the difference to grayscale
            # diff.save(f'./frames/diff_{frame_count}.png')

            diff_hash = str(imagehash.average_hash(diff, hash_size=IMAGE_HASH_SIZE))
            frames_diff_hashes.append(diff_hash)

        if frame_count % loop_check_interval == 0:
            has_loop = has_looped_item(frames_diff_hashes, loop_min_size, LOOP_MIN_OCCURRENCES, LOOP_DIFF_MARGIN_ERROR)
            print(f'Has loop: {has_loop}')

        previous_frame_pil = frame_pil

        if len(frames_diff_hashes) > hash_list_size:
            frames_diff_hashes.pop(0)


if __name__ == '__main__':
    main()
