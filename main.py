import csv
import argparse
import io
import math
from datetime import datetime

import cv2
import imagehash
from PIL import Image, ImageChops

INPUT_FPS = 12  # When set to None the fps will be inferred using opencv.

FRAME_SAMPLE_INTERVAL = 5
HASH_LIST_WINDOW_SIZE_IN_SECONDS = 60
LOOP_CHECK_INTERVAL_IN_SECONDS = 5

IMAGE_HASH_SIZE = 12

LOOP_MIN_OCCURRENCES = 5
LOOP_MIN_DURATION_IN_SECONDS = 3
LOOP_DIFF_MARGIN_ERROR = 3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stream", type=str, help="The input stream. Can be any opencv supported video capture input.")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.stream)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    fps = INPUT_FPS if INPUT_FPS else cap.get(cv2.CAP_PROP_FPS)
    print(f"Frame rate: {fps}")

    output_file_name = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
    print(f'Writing output to: {output_file_name}')

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

        if frame_count % FRAME_SAMPLE_INTERVAL != 0:
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
            check_date = datetime.now().isoformat()
            has_loop = has_looped_item(frames_diff_hashes, loop_min_size, LOOP_MIN_OCCURRENCES, LOOP_DIFF_MARGIN_ERROR)

            with open(output_file_name, mode='a', newline='') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow([check_date, has_loop])

            print(f'Check date: {check_date}, Has loop: {has_loop}')

        previous_frame_pil = frame_pil

        if len(frames_diff_hashes) > hash_list_size:
            frames_diff_hashes.pop(0)


def has_looped_item(input_list: list, loop_min_size: float, min_occurrences: int, margin_error: int) -> bool:
    for tested_item in input_list:
        item_indices = [index for index, item in enumerate(input_list) if item == tested_item]

        if len(item_indices) < min_occurrences:
            continue

        differences = [item_indices[i + 1] - item_indices[i] for i in range(len(item_indices) - 1)]
        if not all(difference > loop_min_size for difference in differences):
            continue

        if all(math.fabs(differences[0] - difference) < margin_error for difference in differences):
            return True

    return False


if __name__ == '__main__':
    main()
