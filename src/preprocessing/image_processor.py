"""
T-04: OpenCV 그레이스케일 변환 구현
T-05: Canny Edge Detection 적용
T-06: 전처리 파이프라인 통합

US-02: 이미지 전처리 기능
- 컬러 → 흑백 변환 구현
- 노이즈 제거 필터 적용
- 윤곽선(Edge) 추출 기능
"""

from typing import Optional, Tuple, Callable, List
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class ImageProcessor:
    """이미지 전처리 파이프라인"""

    # Canny Edge Detection 기본 파라미터
    DEFAULT_CANNY_LOW = 50
    DEFAULT_CANNY_HIGH = 150

    # 가우시안 블러 기본 커널 크기
    DEFAULT_BLUR_KERNEL = (5, 5)

    def __init__(self):
        if not CV2_AVAILABLE:
            raise ImportError("opencv-python 라이브러리가 필요합니다: pip install opencv-python")

        self._pipeline: List[Callable[[np.ndarray], np.ndarray]] = []

    def to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """
        컬러 이미지를 그레이스케일로 변환 (T-04)

        Args:
            img: BGR 형식의 컬러 이미지

        Returns:
            그레이스케일 이미지
        """
        if len(img.shape) == 2:
            return img  # 이미 그레이스케일
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def apply_gaussian_blur(
        self,
        img: np.ndarray,
        kernel_size: Tuple[int, int] = DEFAULT_BLUR_KERNEL
    ) -> np.ndarray:
        """
        가우시안 블러 적용 (노이즈 제거)

        Args:
            img: 입력 이미지
            kernel_size: 블러 커널 크기

        Returns:
            블러 적용된 이미지
        """
        return cv2.GaussianBlur(img, kernel_size, 0)

    def apply_bilateral_filter(
        self,
        img: np.ndarray,
        d: int = 9,
        sigma_color: int = 75,
        sigma_space: int = 75
    ) -> np.ndarray:
        """
        양방향 필터 적용 (엣지 보존 노이즈 제거)

        Args:
            img: 입력 이미지
            d: 필터 직경
            sigma_color: 색상 공간 시그마
            sigma_space: 좌표 공간 시그마

        Returns:
            필터 적용된 이미지
        """
        return cv2.bilateralFilter(img, d, sigma_color, sigma_space)

    def apply_canny_edge(
        self,
        img: np.ndarray,
        low_threshold: int = DEFAULT_CANNY_LOW,
        high_threshold: int = DEFAULT_CANNY_HIGH
    ) -> np.ndarray:
        """
        Canny Edge Detection 적용 (T-05)

        Args:
            img: 그레이스케일 이미지
            low_threshold: 저임계값
            high_threshold: 고임계값

        Returns:
            엣지 이미지
        """
        return cv2.Canny(img, low_threshold, high_threshold)

    def apply_threshold(
        self,
        img: np.ndarray,
        threshold: int = 127,
        max_value: int = 255,
        threshold_type: int = cv2.THRESH_BINARY
    ) -> np.ndarray:
        """
        이진화 (Thresholding)

        Args:
            img: 그레이스케일 이미지
            threshold: 임계값
            max_value: 최대값
            threshold_type: 임계값 타입

        Returns:
            이진화된 이미지
        """
        _, binary = cv2.threshold(img, threshold, max_value, threshold_type)
        return binary

    def apply_adaptive_threshold(
        self,
        img: np.ndarray,
        max_value: int = 255,
        block_size: int = 11,
        c: int = 2
    ) -> np.ndarray:
        """
        적응형 이진화

        Args:
            img: 그레이스케일 이미지
            max_value: 최대값
            block_size: 블록 크기
            c: 상수

        Returns:
            이진화된 이미지
        """
        return cv2.adaptiveThreshold(
            img, max_value,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size, c
        )

    def apply_morphology(
        self,
        img: np.ndarray,
        operation: int = cv2.MORPH_CLOSE,
        kernel_size: Tuple[int, int] = (3, 3)
    ) -> np.ndarray:
        """
        모폴로지 연산 적용

        Args:
            img: 이진 이미지
            operation: 연산 종류 (MORPH_OPEN, MORPH_CLOSE, MORPH_ERODE, MORPH_DILATE)
            kernel_size: 커널 크기

        Returns:
            연산 적용된 이미지
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
        return cv2.morphologyEx(img, operation, kernel)

    def invert(self, img: np.ndarray) -> np.ndarray:
        """이미지 반전"""
        return cv2.bitwise_not(img)

    # 파이프라인 관련 메서드 (T-06)

    def add_to_pipeline(self, func: Callable[[np.ndarray], np.ndarray]) -> 'ImageProcessor':
        """파이프라인에 처리 함수 추가"""
        self._pipeline.append(func)
        return self

    def clear_pipeline(self) -> 'ImageProcessor':
        """파이프라인 초기화"""
        self._pipeline.clear()
        return self

    def process_pipeline(self, img: np.ndarray) -> np.ndarray:
        """파이프라인 실행"""
        result = img.copy()
        for func in self._pipeline:
            result = func(result)
        return result

    def create_obstacle_detection_pipeline(self) -> 'ImageProcessor':
        """
        장애물 탐지용 전처리 파이프라인 생성 (T-06)

        Pipeline:
        1. 그레이스케일 변환
        2. 가우시안 블러 (노이즈 제거)
        3. 이진화 (장애물 = 검은색)
        4. 모폴로지 클로징 (노이즈 제거)
        """
        self.clear_pipeline()
        self.add_to_pipeline(self.to_grayscale)
        self.add_to_pipeline(lambda img: self.apply_gaussian_blur(img, (3, 3)))
        self.add_to_pipeline(lambda img: self.apply_threshold(img, 100, 255, cv2.THRESH_BINARY_INV))
        self.add_to_pipeline(lambda img: self.apply_morphology(img, cv2.MORPH_CLOSE, (3, 3)))
        return self

    def create_edge_detection_pipeline(self) -> 'ImageProcessor':
        """
        엣지 탐지용 전처리 파이프라인 생성

        Pipeline:
        1. 그레이스케일 변환
        2. 가우시안 블러
        3. Canny Edge Detection
        """
        self.clear_pipeline()
        self.add_to_pipeline(self.to_grayscale)
        self.add_to_pipeline(lambda img: self.apply_gaussian_blur(img, (5, 5)))
        self.add_to_pipeline(lambda img: self.apply_canny_edge(img, 50, 150))
        return self

    def process(
        self,
        img: np.ndarray,
        grayscale: bool = True,
        blur: bool = True,
        edge: bool = False,
        threshold: Optional[int] = None
    ) -> np.ndarray:
        """
        단일 호출 전처리 (편의 메서드)

        Args:
            img: 입력 이미지
            grayscale: 그레이스케일 변환 여부
            blur: 블러 적용 여부
            edge: 엣지 탐지 적용 여부
            threshold: 이진화 임계값 (None이면 적용 안함)

        Returns:
            전처리된 이미지
        """
        result = img.copy()

        if grayscale and len(result.shape) == 3:
            result = self.to_grayscale(result)

        if blur:
            result = self.apply_gaussian_blur(result, (5, 5))

        if threshold is not None:
            result = self.apply_threshold(result, threshold, 255, cv2.THRESH_BINARY_INV)

        if edge:
            result = self.apply_canny_edge(result)

        return result


def main():
    """테스트"""
    print("=" * 50)
    print("T-04~T-06: 이미지 전처리 모듈 테스트")
    print("=" * 50)

    # 테스트 이미지 생성 (T-Rex 게임 시뮬레이션)
    test_img = np.full((150, 600, 3), 247, dtype=np.uint8)  # 배경 (연회색)

    # 선인장 (검은색 장애물)
    cv2.rectangle(test_img, (300, 100), (320, 150), (83, 83, 83), -1)

    # 공룡 (검은색)
    cv2.rectangle(test_img, (50, 100), (90, 150), (83, 83, 83), -1)

    processor = ImageProcessor()

    # T-04: 그레이스케일 변환
    gray = processor.to_grayscale(test_img)
    print(f"그레이스케일 변환: {test_img.shape} -> {gray.shape}")

    # T-05: Canny Edge Detection
    edges = processor.apply_canny_edge(gray)
    print(f"Canny Edge: {edges.shape}, 엣지 픽셀 수: {np.sum(edges > 0)}")

    # T-06: 파이프라인 테스트
    processor.create_obstacle_detection_pipeline()
    processed = processor.process_pipeline(test_img)
    print(f"파이프라인 처리: {processed.shape}")

    # 장애물 픽셀 카운트
    obstacle_pixels = np.sum(processed > 0)
    print(f"장애물 영역 픽셀 수: {obstacle_pixels}")

    print("\n✓ 모든 전처리 테스트 완료")


if __name__ == "__main__":
    main()
