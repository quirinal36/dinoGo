"""
T-01: MSS 라이브러리 설정 및 화면 캡처 모듈 구현
T-02: 캡처 영역 좌표 설정 로직 구현
T-03: FPS 측정 및 최적화

US-01: 화면 캡처 기능
- 초당 30프레임 이상 캡처 가능
- 게임 캔버스 영역만 정확히 추출
- 캡처 지연 시간 10ms 이하
"""

import time
from typing import Optional, Tuple, Dict, Any
import numpy as np

try:
    import mss
    import mss.tools
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False


class ScreenCapture:
    """고성능 화면 캡처 클래스 (MSS 기반)"""

    # 기본 게임 캔버스 영역 (Chrome T-Rex 게임 기준)
    DEFAULT_GAME_REGION = {
        'left': 0,
        'top': 0,
        'width': 600,
        'height': 150
    }

    def __init__(self, region: Optional[Dict[str, int]] = None):
        """
        화면 캡처 초기화

        Args:
            region: 캡처 영역 {'left', 'top', 'width', 'height'}
                   None이면 자동 감지 시도 후 기본값 사용
        """
        if not MSS_AVAILABLE:
            raise ImportError("mss 라이브러리가 필요합니다: pip install mss")

        self._sct = mss.mss()
        self._region = region or self.DEFAULT_GAME_REGION.copy()

        # FPS 측정용
        self._frame_count = 0
        self._start_time = time.perf_counter()
        self._fps = 0.0
        self._last_capture_time = 0.0

    @property
    def region(self) -> Dict[str, int]:
        """현재 캡처 영역 반환"""
        return self._region.copy()

    @region.setter
    def region(self, value: Dict[str, int]) -> None:
        """캡처 영역 설정"""
        required_keys = {'left', 'top', 'width', 'height'}
        if not all(k in value for k in required_keys):
            raise ValueError(f"region은 {required_keys} 키가 필요합니다")
        self._region = value.copy()

    def set_region_by_coords(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """좌표로 캡처 영역 설정 (T-02)"""
        self._region = {
            'left': x1,
            'top': y1,
            'width': x2 - x1,
            'height': y2 - y1
        }

    def capture(self) -> np.ndarray:
        """
        화면 캡처 수행

        Returns:
            np.ndarray: BGR 형식의 이미지 배열
        """
        capture_start = time.perf_counter()

        # MSS로 화면 캡처
        screenshot = self._sct.grab(self._region)

        # numpy 배열로 변환 (BGRA -> BGR)
        img = np.array(screenshot)[:, :, :3]

        # 캡처 시간 및 FPS 계산
        self._last_capture_time = (time.perf_counter() - capture_start) * 1000  # ms
        self._update_fps()

        return img

    def capture_gray(self) -> np.ndarray:
        """그레이스케일로 직접 캡처 (최적화)"""
        screenshot = self._sct.grab(self._region)
        img = np.array(screenshot)
        # 빠른 그레이스케일 변환: 0.299*R + 0.587*G + 0.114*B
        gray = (0.299 * img[:, :, 2] +
                0.587 * img[:, :, 1] +
                0.114 * img[:, :, 0]).astype(np.uint8)
        self._update_fps()
        return gray

    def _update_fps(self) -> None:
        """FPS 업데이트 (T-03)"""
        self._frame_count += 1
        elapsed = time.perf_counter() - self._start_time

        if elapsed >= 1.0:  # 1초마다 FPS 갱신
            self._fps = self._frame_count / elapsed
            self._frame_count = 0
            self._start_time = time.perf_counter()

    @property
    def fps(self) -> float:
        """현재 FPS 반환"""
        return self._fps

    @property
    def last_capture_time_ms(self) -> float:
        """마지막 캡처 소요 시간 (ms)"""
        return self._last_capture_time

    def get_stats(self) -> Dict[str, Any]:
        """캡처 통계 반환"""
        return {
            'fps': self._fps,
            'last_capture_ms': self._last_capture_time,
            'region': self._region,
            'meets_requirements': self._fps >= 30 and self._last_capture_time <= 10
        }

    def benchmark(self, frames: int = 100) -> Dict[str, float]:
        """
        캡처 성능 벤치마크 (T-03)

        Args:
            frames: 테스트할 프레임 수

        Returns:
            성능 측정 결과
        """
        times = []

        for _ in range(frames):
            start = time.perf_counter()
            self.capture()
            times.append((time.perf_counter() - start) * 1000)

        return {
            'avg_ms': np.mean(times),
            'min_ms': np.min(times),
            'max_ms': np.max(times),
            'std_ms': np.std(times),
            'fps': 1000 / np.mean(times),
            'frames_tested': frames
        }

    def auto_detect_game_region(self) -> Optional[Dict[str, int]]:
        """
        게임 영역 자동 감지 시도 (Chrome T-Rex 게임)

        Returns:
            감지된 영역 또는 None
        """
        # 전체 화면 캡처
        monitor = self._sct.monitors[1]  # 주 모니터
        full_screen = np.array(self._sct.grab(monitor))

        # T-Rex 게임의 특징적인 배경색 (연회색: #f7f7f7)
        target_color = np.array([247, 247, 247])

        # 색상 매칭으로 게임 영역 찾기
        mask = np.all(np.abs(full_screen[:, :, :3] - target_color) < 10, axis=2)

        if np.any(mask):
            rows = np.any(mask, axis=1)
            cols = np.any(mask, axis=0)

            if np.any(rows) and np.any(cols):
                y_min, y_max = np.where(rows)[0][[0, -1]]
                x_min, x_max = np.where(cols)[0][[0, -1]]

                detected = {
                    'left': int(x_min),
                    'top': int(y_min),
                    'width': int(x_max - x_min),
                    'height': int(y_max - y_min)
                }

                # 합리적인 크기인지 확인
                if detected['width'] > 200 and detected['height'] > 50:
                    self._region = detected
                    return detected

        return None

    def close(self) -> None:
        """리소스 정리"""
        self._sct.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


def main():
    """테스트 및 벤치마크"""
    print("=" * 50)
    print("T-01: MSS 화면 캡처 모듈 테스트")
    print("=" * 50)

    with ScreenCapture() as capture:
        print(f"\n캡처 영역: {capture.region}")

        # 단일 캡처 테스트
        img = capture.capture()
        print(f"캡처된 이미지 크기: {img.shape}")
        print(f"캡처 시간: {capture.last_capture_time_ms:.2f}ms")

        # 벤치마크
        print("\n벤치마크 실행 중 (100 frames)...")
        stats = capture.benchmark(100)

        print(f"\n결과:")
        print(f"  평균 캡처 시간: {stats['avg_ms']:.2f}ms")
        print(f"  최소 캡처 시간: {stats['min_ms']:.2f}ms")
        print(f"  최대 캡처 시간: {stats['max_ms']:.2f}ms")
        print(f"  달성 FPS: {stats['fps']:.1f}")

        # 요구사항 충족 여부
        print(f"\n요구사항 충족:")
        print(f"  ✓ FPS >= 30: {'✓' if stats['fps'] >= 30 else '✗'} ({stats['fps']:.1f})")
        print(f"  ✓ 지연 <= 10ms: {'✓' if stats['avg_ms'] <= 10 else '✗'} ({stats['avg_ms']:.2f}ms)")


if __name__ == "__main__":
    main()
