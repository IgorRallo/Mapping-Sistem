import cv2
import numpy as np
import torch
import sys

from models.matching import Matching
from models.utils import frame2tensor


class SuperPointStitcher:
    def __init__(self, result_size_multiplier_homography=5.0, result_size_multiplier_affine=5.0,
                 transformation_type='affine', frame_interval=13, batch_size=2, use_batch_norm=False):
        self.result_size_multiplier_homography = result_size_multiplier_homography
        self.result_size_multiplier_affine = result_size_multiplier_affine
        self.transformation_type = transformation_type
        self.frame_interval = frame_interval
        self.batch_size = batch_size
        self.use_batch_norm = use_batch_norm

        # Config for SuperPoint and SuperGlue
        config = {
            'superpoint': {
                'nms_radius': 4,
                'keypoint_threshold': 0.01,
                'max_keypoints': 1024
            },
            'superglue': {
                'weights': 'outdoor'
            }
        }
        self.matching = Matching(config).eval().to('cuda' if torch.cuda.is_available() else 'cpu')

    def detect_and_match(self, imageA, imageB):
        with torch.no_grad():
            imageA_gray = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
            imageB_gray = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

            imageA_tensor = frame2tensor(imageA_gray, 'cuda' if torch.cuda.is_available() else 'cpu')
            imageB_tensor = frame2tensor(imageB_gray, 'cuda' if torch.cuda.is_available() else 'cpu')

            pred = self.matching({'image0': imageA_tensor, 'image1': imageB_tensor})

            kpsA = pred['keypoints0'][0].cpu().numpy()
            kpsB = pred['keypoints1'][0].cpu().numpy()
            matches = pred['matches0'][0].cpu().numpy()

            valid_matches = matches > -1
            kpsA_matched = kpsA[valid_matches]
            kpsB_matched = kpsB[matches[valid_matches]]

            del pred  # Звільнення пам'яті GPU
            torch.cuda.empty_cache()

            return kpsA_matched, kpsB_matched

    def stitch_images(self, imageA, imageB):
        kpsA, kpsB = self.detect_and_match(imageA, imageB)

        if len(kpsA) >= 3 and len(kpsB) >= 3:
            if self.transformation_type == 'homography' and len(kpsA) >= 4:
                H, status = cv2.findHomography(kpsA, kpsB, cv2.RANSAC, 2.0)
                if H is not None:
                    width = int(imageA.shape[1] * self.result_size_multiplier_homography)
                    height = int(imageA.shape[0] * self.result_size_multiplier_homography)
                    result = np.zeros((height, width, 3), dtype=np.uint8)
                    offset_x = width // 4
                    offset_y = height // 4
                    H[0, 2] += offset_x
                    H[1, 2] += offset_y

                    result = cv2.warpPerspective(imageA, H, (width, height), dst=result, borderMode=cv2.BORDER_TRANSPARENT)
                    result[offset_y:offset_y + imageB.shape[0], offset_x:offset_x + imageB.shape[1]] = imageB
                    return self.crop_black_borders(result)
            elif self.transformation_type == 'affine':
                H, status = cv2.estimateAffinePartial2D(kpsA, kpsB)
                if H is not None:
                    width = int(imageA.shape[1] * self.result_size_multiplier_affine)
                    height = int(imageA.shape[0] * self.result_size_multiplier_affine)
                    result = np.zeros((height, width, 3), dtype=np.uint8)
                    offset_x = width // 4
                    offset_y = height // 4
                    H[0, 2] += offset_x
                    H[1, 2] += offset_y

                    result = cv2.warpAffine(imageA, H, (width, height), dst=result, borderMode=cv2.BORDER_TRANSPARENT)
                    result[offset_y:offset_y + imageB.shape[0], offset_x:offset_x + imageB.shape[1]] = imageB
                    return self.crop_black_borders(result)

        print("Помилка: недостатньо відповідностей для обчислення трансформації.")
        return None

    def crop_black_borders(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            return image[y:y+h, x:x+w]
        return image

    def stitch_video_frames(self, video_path):
        cap = cv2.VideoCapture(video_path)
        success, prev_frame = cap.read()
        if not success:
            print("Помилка: неможливо завантажити відео.")
            return None

        frame_count = 0
        result = prev_frame
        batch = []

        while success:
            success, frame = cap.read()
            frame_count += 1

            if frame_count % self.frame_interval == 0 and success:
                batch.append(frame)

                if len(batch) == self.batch_size:
                    result = self.process_batch(result, batch)
                    batch = []

        if batch:
            result = self.process_batch(result, batch)

        cap.release()
        return result

    def process_batch(self, base_frame, batch):
        for frame in batch:
            base_frame = self.stitch_images(base_frame, frame)
            if base_frame is None:
                print("Зшивання завершено через помилку.")
                break

            torch.cuda.empty_cache()  # Очищення пам'яті GPU після кожного зшивання

        return base_frame

    def save_result(self, image, path):
        cv2.imwrite(path, image)
        print(f"Зображення збережено як {path}")

    def visualize_result(self, image):
        pass

