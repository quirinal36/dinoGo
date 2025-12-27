"""
T-07: 공룡 앞 ROI 영역 정의
T-08: 픽셀 밀도 기반 장애물 감지 알고리즘
T-09: 거리 계산 함수 구현

US-03: 기본 장애물 탐지
- ROI(Region of Interest) 영역 설정
- 검은색 픽셀 감지 로직 구현
- 장애물과의 수평 거리 계산
"""

from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class ObstacleType(Enum):
    """장애물 종류"""
    NONE = 0
    CACTUS_SMALL = 1
    CACTUS_LARGE = 2
    CACTUS_GROUP = 3
    PTERODACTYL = 4


@dataclass
class Obstacle:
    """감지된 장애물 정보"""
    x: int  # 좌측 x 좌표
    y: int  # 상단 y 좌표
    width: int
    height: int
    distance: int  # 공룡으로부터의 거리 (픽셀)
    obstacle_type: ObstacleType = ObstacleType.NONE
    confidence: float = 1.0

    @property
    def center_x(self) -> int:
        return self.x + self.width // 2

    @property
    def center_y(self) -> int:
        return self.y + self.height // 2

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height


class ObstacleDetector:
    """장애물 탐지기"""

    # T-Rex 게임 기본 레이아웃 (600x150 기준)
    # 공룡 위치: 약 x=50~90 영역
    DINO_X_END = 90

    # 기본 ROI 설정 (공룡 앞 영역)
    DEFAULT_ROI = {
        'x': 90,       # 공룡 오른쪽부터
        'y': 80,       # 지면 근처
        'width': 200,  # 탐지 범위
        'height': 70   # 높이 범위
    }

    # 픽셀 밀도 임계값
    DEFAULT_DENSITY_THRESHOLD = 0.02  # 2% 이상이면 장애물로 판단

    def __init__(
        self,
        roi: Optional[Dict[str, int]] = None,
        density_threshold: float = DEFAULT_DENSITY_THRESHOLD,
        dino_x_end: int = DINO_X_END
    ):
        """
        장애물 탐지기 초기화

        Args:
            roi: 탐지 ROI 영역
            density_threshold: 픽셀 밀도 임계값
            dino_x_end: 공룡 끝 x 좌표 (거리 계산 기준)
        """
        self._roi = roi or self.DEFAULT_ROI.copy()
        self._density_threshold = density_threshold
        self._dino_x_end = dino_x_end

        # 연속 프레임 분석용
        self._last_obstacles: List[Obstacle] = []

    @property
    def roi(self) -> Dict[str, int]:
        """현재 ROI 영역"""
        return self._roi.copy()

    def set_roi(
        self,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> None:
        """ROI 영역 설정 (T-07)"""
        self._roi = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }

    def set_roi_from_dino(
        self,
        dino_x: int,
        dino_y: int,
        search_distance: int = 200,
        search_height: int = 70
    ) -> None:
        """공룡 위치 기준으로 ROI 설정 (T-07)"""
        self._roi = {
            'x': dino_x,
            'y': dino_y - search_height,
            'width': search_distance,
            'height': search_height
        }
        self._dino_x_end = dino_x

    def extract_roi(self, img: np.ndarray) -> np.ndarray:
        """이미지에서 ROI 영역 추출"""
        roi = self._roi
        return img[
            roi['y']:roi['y'] + roi['height'],
            roi['x']:roi['x'] + roi['width']
        ]

    def calculate_pixel_density(self, binary_img: np.ndarray) -> float:
        """
        픽셀 밀도 계산 (T-08)

        Args:
            binary_img: 이진화된 이미지 (흰색=장애물)

        Returns:
            0~1 사이의 밀도 값
        """
        total_pixels = binary_img.size
        obstacle_pixels = np.sum(binary_img > 0)
        return obstacle_pixels / total_pixels

    def detect_obstacle_simple(self, binary_img: np.ndarray) -> bool:
        """
        단순 장애물 감지 (밀도 기반) (T-08)

        Args:
            binary_img: 이진화된 이미지

        Returns:
            장애물 존재 여부
        """
        roi_img = self.extract_roi(binary_img)
        density = self.calculate_pixel_density(roi_img)
        return density >= self._density_threshold

    def detect_obstacles(
        self,
        binary_img: np.ndarray,
        min_area: int = 100,
        max_obstacles: int = 5
    ) -> List[Obstacle]:
        """
        장애물 감지 및 위치 추출 (T-08, T-09)

        Args:
            binary_img: 이진화된 이미지 (흰색=장애물)
            min_area: 최소 장애물 면적
            max_obstacles: 최대 감지 개수

        Returns:
            감지된 장애물 목록
        """
        if not CV2_AVAILABLE:
            # OpenCV 없이 단순 감지만 수행
            if self.detect_obstacle_simple(binary_img):
                return [Obstacle(
                    x=self._roi['x'],
                    y=self._roi['y'],
                    width=50,
                    height=50,
                    distance=self._roi['x'] - self._dino_x_end
                )]
            return []

        # ROI 영역 추출
        roi_img = self.extract_roi(binary_img)

        # 컨투어 찾기
        contours, _ = cv2.findContours(
            roi_img,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        obstacles = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue

            # 바운딩 박스
            x, y, w, h = cv2.boundingRect(contour)

            # 전체 이미지 좌표로 변환
            abs_x = x + self._roi['x']
            abs_y = y + self._roi['y']

            # 거리 계산 (T-09)
            distance = abs_x - self._dino_x_end

            # 장애물 타입 추정
            obs_type = self._classify_obstacle(w, h, abs_y)

            obstacle = Obstacle(
                x=abs_x,
                y=abs_y,
                width=w,
                height=h,
                distance=distance,
                obstacle_type=obs_type,
                confidence=min(1.0, area / 500)  # 면적 기반 신뢰도
            )
            obstacles.append(obstacle)

        # 거리순 정렬
        obstacles.sort(key=lambda o: o.distance)

        # 최대 개수 제한
        obstacles = obstacles[:max_obstacles]

        self._last_obstacles = obstacles
        return obstacles

    def _classify_obstacle(self, width: int, height: int, y: int) -> ObstacleType:
        """장애물 타입 분류"""
        # 높이/너비 비율로 분류
        aspect_ratio = height / max(width, 1)

        # y 위치로 익룡 구분 (나중에 Phase 2에서 개선)
        if y < 60:  # 상단에 있으면 익룡일 가능성
            return ObstacleType.PTERODACTYL

        if width > 50:
            return ObstacleType.CACTUS_GROUP
        elif height > 40:
            return ObstacleType.CACTUS_LARGE
        else:
            return ObstacleType.CACTUS_SMALL

    def get_nearest_obstacle(
        self,
        binary_img: np.ndarray
    ) -> Optional[Obstacle]:
        """가장 가까운 장애물 반환"""
        obstacles = self.detect_obstacles(binary_img)
        return obstacles[0] if obstacles else None

    def calculate_distance(self, obstacle: Obstacle) -> int:
        """
        공룡과 장애물 사이 거리 계산 (T-09)

        Args:
            obstacle: 장애물 객체

        Returns:
            거리 (픽셀)
        """
        return obstacle.x - self._dino_x_end

    def should_jump(
        self,
        binary_img: np.ndarray,
        jump_distance_threshold: int = 80
    ) -> Tuple[bool, Optional[Obstacle]]:
        """
        점프 필요 여부 판단

        Args:
            binary_img: 이진화된 이미지
            jump_distance_threshold: 점프 거리 임계값

        Returns:
            (점프 여부, 가장 가까운 장애물)
        """
        nearest = self.get_nearest_obstacle(binary_img)

        if nearest is None:
            return False, None

        should_jump = nearest.distance <= jump_distance_threshold
        return should_jump, nearest

    def get_stats(self) -> Dict[str, Any]:
        """탐지 통계 반환"""
        return {
            'roi': self._roi,
            'density_threshold': self._density_threshold,
            'dino_x_end': self._dino_x_end,
            'last_obstacles_count': len(self._last_obstacles)
        }


def main():
    """테스트"""
    print("=" * 50)
    print("T-07~T-09: 장애물 탐지 모듈 테스트")
    print("=" * 50)

    if not CV2_AVAILABLE:
        print("경고: OpenCV가 설치되지 않았습니다")
        return

    # 테스트 이미지 생성
    test_img = np.zeros((150, 600), dtype=np.uint8)

    # 장애물 시뮬레이션 (흰색 = 장애물)
    cv2.rectangle(test_img, (150, 100), (170, 150), 255, -1)  # 선인장 1
    cv2.rectangle(test_img, (250, 80), (280, 150), 255, -1)   # 선인장 2

    detector = ObstacleDetector()

    # T-07: ROI 확인
    print(f"\nROI 설정: {detector.roi}")

    # T-08: 장애물 감지
    obstacles = detector.detect_obstacles(test_img)
    print(f"\n감지된 장애물 수: {len(obstacles)}")

    for i, obs in enumerate(obstacles):
        print(f"\n장애물 {i+1}:")
        print(f"  위치: ({obs.x}, {obs.y})")
        print(f"  크기: {obs.width}x{obs.height}")
        print(f"  거리: {obs.distance}px")
        print(f"  타입: {obs.obstacle_type.name}")

    # T-09: 점프 판단
    should_jump, nearest = detector.should_jump(test_img, 100)
    print(f"\n점프 필요: {should_jump}")
    if nearest:
        print(f"가장 가까운 장애물 거리: {nearest.distance}px")

    print("\n✓ 모든 장애물 탐지 테스트 완료")


if __name__ == "__main__":
    main()
