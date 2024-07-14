import cv2
import imagehash
from PIL import Image

FRAME_HASHES_WINDOW_SIZE = 30
SIMILAR_FRAMES_LOOP_THRESHOLD = 5


def main() -> None:
    cap = cv2.VideoCapture('./part_1.mp4')

    frames_hashes: dict[str, int] = {}

    last_frame_hash = ''
    frame_count = 0
    count_from_last_new_frame = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame_hash = str(imagehash.average_hash(frame_pil))

        if frame_hash == last_frame_hash:
            continue

        if frame_hash in frames_hashes:
            hash_count = frames_hashes.pop(frame_hash)
            frames_hashes[frame_hash] = hash_count + 1
            count_from_last_new_frame += 1
            print(f'Similar frame: {frame_hash}')
        else:
            frames_hashes[frame_hash] = 1
            count_from_last_new_frame = 0

        print(frames_hashes)

        if frame_count % FRAME_HASHES_WINDOW_SIZE == 0 and frame_count > 0:
            oldest_hash = next(iter(frames_hashes))
            frames_hashes.pop(oldest_hash)

        if count_from_last_new_frame > 10:
            if all(map(lambda x: x > 5, frames_hashes.values())):
                print('We\'re in a loop!')
                return

        last_frame_hash = frame_hash
        frame_count += 1


if __name__ == '__main__':
    main()
