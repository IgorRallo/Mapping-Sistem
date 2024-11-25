import cv2
import numpy as np
import matplotlib.pyplot as plt
import imutils

class ImageStitcher:
    def __init__(self, feature_extractor_method='sift', lowe_ratio=0.4, ransac_reproj_thresh=1.5,
                 result_size_multiplier_homography=4, result_size_multiplier_affine=4,
                 transformation_type='affine', frame_interval=100):
        self.feature_extractor_method = feature_extractor_method
        self.lowe_ratio = lowe_ratio  # Приймає значення з GUI
        self.ransac_reproj_thresh = ransac_reproj_thresh  # Приймає значення з GUI
        self.result_size_multiplier_homography = result_size_multiplier_homography
        self.result_size_multiplier_affine = result_size_multiplier_affine
        self.transformation_type = transformation_type
        self.frame_interval = frame_interval


    def detect_and_describe(self, image):
        if self.feature_extractor_method == 'sift':
            descriptor = cv2.SIFT_create()
        (kps, features) = descriptor.detectAndCompute(image, None)
        return (kps, features)

    def match_keypoints_knn(self, featuresA, featuresB):
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        raw_matches = flann.knnMatch(featuresA, featuresB, k=2)
        matches = [m for m, n in raw_matches if m.distance < n.distance * self.lowe_ratio]
        return matches

    def get_transformation(self, kpsA, kpsB, matches):
        kpsA = np.float32([kp.pt for kp in kpsA])
        kpsB = np.float32([kp.pt for kp in kpsB])

        if len(matches) > 4:
            ptsA = np.float32([kpsA[m.queryIdx] for m in matches])
            ptsB = np.float32([kpsB[m.trainIdx] for m in matches])

            if self.transformation_type == 'affine' and len(matches) >= 3:
                (H, status) = cv2.estimateAffinePartial2D(ptsA, ptsB)
            else:
                (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, self.ransac_reproj_thresh)

            return (matches, H, status)
        else:
            return None

    def stitch_images(self, imageA, imageB):
        imageA_gray = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        imageB_gray = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

        kpsA, featuresA = self.detect_and_describe(imageA_gray)
        kpsB, featuresB = self.detect_and_describe(imageB_gray)

        if kpsA is None or featuresA is None or kpsB is None or featuresB is None:
            print("Помилка: неможливо знайти ключові точки та дескриптори.")
            return None

        matches = self.match_keypoints_knn(featuresA, featuresB)

        if len(matches) >= 4:
            M = self.get_transformation(kpsA, kpsB, matches)
            if M is None:
                print("Помилка: недостатньо відповідностей для обчислення трансформації.")
                return None
            else:
                (matches, H, status) = M
                if self.transformation_type == 'homography':
                    width = int(imageA.shape[1] * self.result_size_multiplier_homography)
                    height = int(imageA.shape[0] * self.result_size_multiplier_homography)
                    result = np.zeros((height, width, 3), dtype=np.uint8)
                    offset_x = width // 4
                    offset_y = height // 4
                    H[0, 2] += offset_x
                    H[1, 2] += offset_y

                    result = cv2.warpPerspective(imageA, H, (width, height), dst=result, borderMode=cv2.BORDER_TRANSPARENT)
                    result[offset_y:offset_y + imageB.shape[0], offset_x:offset_x + imageB.shape[1]] = imageB

                elif self.transformation_type == 'affine':
                    width = int(imageA.shape[1] * self.result_size_multiplier_affine)
                    height = int(imageA.shape[0] * self.result_size_multiplier_affine)
                    result = np.zeros((height, width, 3), dtype=np.uint8)
                    offset_x = width // 4
                    offset_y = height // 4
                    H[0, 2] += offset_x
                    H[1, 2] += offset_y
                    result = cv2.warpAffine(imageA, H, (width, height), dst=result, borderMode=cv2.BORDER_TRANSPARENT)
                    result[offset_y:offset_y + imageB.shape[0], offset_x:offset_x + imageB.shape[1]] = imageB

                gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
                thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)
                c = max(cnts, key=cv2.contourArea)
                (x, y, w, h) = cv2.boundingRect(c)
                result = result[y:y + h, x:x + w]

                return result
        else:
            print("Помилка: недостатньо відповідностей для обчислення трансформації.")
            return None

    def stitch_video_frames(self, video_path):
        cap = cv2.VideoCapture(video_path)
        success, prev_frame = cap.read()
        if not success:
            print("Помилка: неможливо завантажити відео.")
            return None

        frame_count = 0
        result = prev_frame

        while success:
            success, frame = cap.read()
            frame_count += 1

            if frame_count % self.frame_interval == 0 and success:
                result = self.stitch_images(result, frame)
                if result is None:
                    print("Зшивання завершено через помилку.")
                    break

        cap.release()
        return result

    def save_result(self, image, path):
        cv2.imwrite(path, image)
        print(f"Зображення збережено як {path}")

    def visualize_result(self, image):
        plt.figure(figsize=(20, 10))
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()