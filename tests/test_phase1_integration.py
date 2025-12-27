"""
T-14: 통합 테스트 및 버그 수정

Phase 1 MVP 모듈 통합 테스트
"""

import pytest
import numpy as np
import sys
import os

# src 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestScreenCapture:
    """T-01~T-03: 화면 캡처 모듈 테스트"""

    def test_import(self):
        """모듈 import 테스트"""
        from capture.screen_capture import ScreenCapture
        assert ScreenCapture is not None

    def test_capture_instance(self):
        """인스턴스 생성 테스트"""
        from capture.screen_capture import ScreenCapture
        capture = ScreenCapture()
        assert capture is not None
        assert capture.region is not None
        capture.close()

    def test_region_setting(self):
        """영역 설정 테스트"""
        from capture.screen_capture import ScreenCapture
        capture = ScreenCapture()

        # 좌표로 설정
        capture.set_region_by_coords(100, 200, 500, 400)
        region = capture.region
        assert region['left'] == 100
        assert region['top'] == 200
        assert region['width'] == 400
        assert region['height'] == 200
        capture.close()

    def test_capture_returns_numpy(self):
        """캡처 결과가 numpy 배열인지 테스트"""
        from capture.screen_capture import ScreenCapture
        with ScreenCapture() as capture:
            img = capture.capture()
            assert isinstance(img, np.ndarray)
            assert len(img.shape) == 3  # BGR
            assert img.shape[2] == 3


class TestImageProcessor:
    """T-04~T-06: 이미지 전처리 모듈 테스트"""

    def test_import(self):
        """모듈 import 테스트"""
        from preprocessing.image_processor import ImageProcessor
        assert ImageProcessor is not None

    def test_grayscale_conversion(self):
        """그레이스케일 변환 테스트"""
        from preprocessing.image_processor import ImageProcessor

        processor = ImageProcessor()
        test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        gray = processor.to_grayscale(test_img)

        assert len(gray.shape) == 2
        assert gray.shape == (100, 100)

    def test_edge_detection(self):
        """Canny Edge Detection 테스트"""
        from preprocessing.image_processor import ImageProcessor

        processor = ImageProcessor()
        test_img = np.zeros((100, 100), dtype=np.uint8)
        test_img[40:60, 40:60] = 255  # 흰색 사각형

        edges = processor.apply_canny_edge(test_img)
        assert edges.shape == test_img.shape
        assert np.any(edges > 0)  # 엣지가 감지됨

    def test_pipeline(self):
        """전처리 파이프라인 테스트"""
        from preprocessing.image_processor import ImageProcessor

        processor = ImageProcessor()
        processor.create_obstacle_detection_pipeline()

        test_img = np.full((100, 100, 3), 200, dtype=np.uint8)
        test_img[40:60, 40:60] = 50  # 어두운 장애물

        result = processor.process_pipeline(test_img)
        assert len(result.shape) == 2  # 이진화됨
        assert np.any(result > 0)  # 장애물 영역 존재


class TestObstacleDetector:
    """T-07~T-09: 장애물 탐지 모듈 테스트"""

    def test_import(self):
        """모듈 import 테스트"""
        from detection.obstacle_detector import ObstacleDetector
        assert ObstacleDetector is not None

    def test_roi_setting(self):
        """ROI 설정 테스트"""
        from detection.obstacle_detector import ObstacleDetector

        detector = ObstacleDetector()
        detector.set_roi(50, 60, 150, 80)
        roi = detector.roi

        assert roi['x'] == 50
        assert roi['y'] == 60
        assert roi['width'] == 150
        assert roi['height'] == 80

    def test_pixel_density(self):
        """픽셀 밀도 계산 테스트"""
        from detection.obstacle_detector import ObstacleDetector

        detector = ObstacleDetector()

        # 50% 흰색 이미지
        test_img = np.zeros((100, 100), dtype=np.uint8)
        test_img[0:50, :] = 255

        density = detector.calculate_pixel_density(test_img)
        assert 0.49 <= density <= 0.51

    def test_obstacle_detection(self):
        """장애물 감지 테스트"""
        from detection.obstacle_detector import ObstacleDetector

        detector = ObstacleDetector(roi={'x': 0, 'y': 0, 'width': 200, 'height': 100})

        # 장애물이 있는 이미지
        test_img = np.zeros((100, 200), dtype=np.uint8)
        test_img[60:100, 50:80] = 255  # 장애물

        obstacles = detector.detect_obstacles(test_img, min_area=50)
        assert len(obstacles) >= 1

    def test_distance_calculation(self):
        """거리 계산 테스트"""
        from detection.obstacle_detector import ObstacleDetector, Obstacle, ObstacleType

        detector = ObstacleDetector(dino_x_end=90)

        obstacle = Obstacle(
            x=150, y=100, width=30, height=40,
            distance=60, obstacle_type=ObstacleType.CACTUS_SMALL
        )

        distance = detector.calculate_distance(obstacle)
        assert distance == 60  # 150 - 90


class TestKeyboardController:
    """T-10~T-12: 키보드 컨트롤러 테스트"""

    def test_import(self):
        """모듈 import 테스트"""
        from control.keyboard_controller import KeyboardController
        assert KeyboardController is not None

    def test_backend_selection(self):
        """백엔드 선택 테스트"""
        from control.keyboard_controller import (
            KeyboardController,
            DIRECT_INPUT_AVAILABLE,
            PYAUTOGUI_AVAILABLE
        )

        if not DIRECT_INPUT_AVAILABLE and not PYAUTOGUI_AVAILABLE:
            pytest.skip("키보드 라이브러리 없음")

        controller = KeyboardController()
        assert controller.backend in ['pydirectinput', 'pyautogui']

    def test_action_enum(self):
        """액션 열거형 테스트"""
        from control.keyboard_controller import InputAction

        assert InputAction.JUMP.value == 'jump'
        assert InputAction.DUCK.value == 'duck'
        assert InputAction.NONE.value == 'none'


class TestIntegration:
    """통합 테스트"""

    def test_full_pipeline_simulation(self):
        """전체 파이프라인 시뮬레이션"""
        from capture.screen_capture import ScreenCapture
        from preprocessing.image_processor import ImageProcessor
        from detection.obstacle_detector import ObstacleDetector

        # 모듈 초기화
        processor = ImageProcessor()
        processor.create_obstacle_detection_pipeline()

        detector = ObstacleDetector(
            roi={'x': 90, 'y': 80, 'width': 200, 'height': 70}
        )

        # 시뮬레이션 이미지 (T-Rex 게임 배경)
        sim_img = np.full((150, 600, 3), 247, dtype=np.uint8)

        # 선인장 추가 (어두운 색)
        sim_img[100:150, 150:170] = 83

        # 전처리
        processed = processor.process_pipeline(sim_img)

        # 장애물 탐지
        should_jump, obstacle = detector.should_jump(processed, 100)

        # 장애물이 감지되어야 함
        assert obstacle is not None
        print(f"감지된 장애물: 거리={obstacle.distance}px")

    def test_performance_requirements(self):
        """성능 요구사항 테스트"""
        import time
        from capture.screen_capture import ScreenCapture
        from preprocessing.image_processor import ImageProcessor

        with ScreenCapture() as capture:
            # 캡처 성능 테스트 (30 FPS = ~33ms per frame)
            times = []
            for _ in range(30):
                start = time.perf_counter()
                capture.capture()
                times.append((time.perf_counter() - start) * 1000)

            avg_time = np.mean(times)
            fps = 1000 / avg_time

            print(f"평균 캡처 시간: {avg_time:.2f}ms")
            print(f"달성 FPS: {fps:.1f}")

            # 요구사항: 30 FPS 이상
            assert fps >= 30, f"FPS 부족: {fps:.1f} < 30"


def run_tests():
    """테스트 실행"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == "__main__":
    run_tests()
