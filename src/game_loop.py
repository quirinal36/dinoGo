"""
T-13: 메인 게임 루프 통합

모든 모듈을 통합하여 T-Rex Runner 자동 플레이를 구현합니다.

EPIC-01: Phase 1 - MVP
- 목표: 고정된 속도에서 선인장 10개 이상 통과
- 성공 기준: 기본 장애물 감지 및 점프 명령 전송 성공
"""

import time
import signal
import sys
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

import numpy as np

from capture.screen_capture import ScreenCapture
from preprocessing.image_processor import ImageProcessor
from detection.obstacle_detector import ObstacleDetector, ObstacleType
from control.keyboard_controller import KeyboardController, InputAction


class GameState(Enum):
    """게임 상태"""
    IDLE = 'idle'
    RUNNING = 'running'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'


@dataclass
class GameStats:
    """게임 통계"""
    frames_processed: int = 0
    obstacles_detected: int = 0
    jumps_executed: int = 0
    ducks_executed: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    avg_fps: float = 0.0
    avg_latency_ms: float = 0.0
    max_distance_survived: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'frames_processed': self.frames_processed,
            'obstacles_detected': self.obstacles_detected,
            'jumps_executed': self.jumps_executed,
            'ducks_executed': self.ducks_executed,
            'duration_seconds': self.end_time - self.start_time if self.end_time else 0,
            'avg_fps': self.avg_fps,
            'avg_latency_ms': self.avg_latency_ms
        }


@dataclass
class GameConfig:
    """게임 설정"""
    # 캡처 영역 (Chrome T-Rex 게임 기준, 조정 필요)
    capture_region: Dict[str, int] = field(default_factory=lambda: {
        'left': 0,
        'top': 150,
        'width': 600,
        'height': 150
    })

    # 탐지 ROI
    detection_roi: Dict[str, int] = field(default_factory=lambda: {
        'x': 90,
        'y': 80,
        'width': 200,
        'height': 70
    })

    # 점프 파라미터
    jump_distance_threshold: int = 100  # 이 거리 이하면 점프
    jump_cooldown: float = 0.3

    # 이진화 임계값
    binary_threshold: int = 100

    # FPS 제한 (0 = 무제한)
    target_fps: int = 60


class DinoGameAutomator:
    """T-Rex Runner 자동 플레이어"""

    def __init__(self, config: Optional[GameConfig] = None):
        """
        자동 플레이어 초기화

        Args:
            config: 게임 설정 (None이면 기본값)
        """
        self.config = config or GameConfig()

        # 모듈 초기화
        self._capture = ScreenCapture(self.config.capture_region)
        self._processor = ImageProcessor()
        self._detector = ObstacleDetector(
            roi=self.config.detection_roi,
            dino_x_end=90
        )
        self._controller = KeyboardController()

        # 전처리 파이프라인 설정
        self._processor.create_obstacle_detection_pipeline()

        # 상태
        self._state = GameState.IDLE
        self._stats = GameStats()
        self._running = False

        # 시그널 핸들러 (Ctrl+C)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Ctrl+C 핸들러"""
        print("\n\n중단 신호 감지. 종료 중...")
        self._running = False

    @property
    def state(self) -> GameState:
        return self._state

    @property
    def stats(self) -> GameStats:
        return self._stats

    def start_game(self) -> None:
        """게임 시작"""
        print("게임 시작 중...")
        self._controller.start_game()
        time.sleep(0.5)
        self._state = GameState.RUNNING

    def run(
        self,
        auto_start: bool = True,
        debug: bool = False,
        max_frames: int = 0
    ) -> GameStats:
        """
        메인 게임 루프 실행

        Args:
            auto_start: 자동으로 게임 시작
            debug: 디버그 출력
            max_frames: 최대 프레임 수 (0 = 무제한)

        Returns:
            게임 통계
        """
        print("=" * 60)
        print("T-Rex Runner Automator - Phase 1 MVP")
        print("=" * 60)
        print(f"캡처 영역: {self.config.capture_region}")
        print(f"탐지 ROI: {self.config.detection_roi}")
        print(f"점프 거리 임계값: {self.config.jump_distance_threshold}px")
        print("-" * 60)
        print("Ctrl+C로 종료")
        print("-" * 60)

        if auto_start:
            print("\n3초 후 시작...")
            time.sleep(3)
            self.start_game()

        self._running = True
        self._stats = GameStats(start_time=time.perf_counter())

        frame_count = 0
        last_fps_time = time.perf_counter()
        fps_counter = 0

        try:
            while self._running:
                loop_start = time.perf_counter()

                # 1. 화면 캡처
                frame = self._capture.capture()

                # 2. 전처리 (그레이스케일 + 이진화)
                processed = self._processor.process(
                    frame,
                    grayscale=True,
                    blur=True,
                    threshold=self.config.binary_threshold
                )

                # 3. 장애물 탐지
                should_jump, obstacle = self._detector.should_jump(
                    processed,
                    self.config.jump_distance_threshold
                )

                # 4. 액션 실행
                if should_jump and obstacle:
                    self._stats.obstacles_detected += 1

                    # 장애물 타입에 따른 액션 결정
                    if obstacle.obstacle_type == ObstacleType.PTERODACTYL:
                        # 익룡: 높이에 따라 점프 또는 숙기 (Phase 2에서 개선)
                        timing = self._controller.jump()
                        if timing:
                            self._stats.jumps_executed += 1
                    else:
                        # 선인장: 점프
                        timing = self._controller.jump()
                        if timing:
                            self._stats.jumps_executed += 1

                    if debug and obstacle:
                        print(f"[{frame_count}] 장애물 감지! "
                              f"거리: {obstacle.distance}px, "
                              f"타입: {obstacle.obstacle_type.name}")

                # 통계 업데이트
                frame_count += 1
                fps_counter += 1
                self._stats.frames_processed = frame_count

                # FPS 계산 (1초마다)
                current_time = time.perf_counter()
                if current_time - last_fps_time >= 1.0:
                    self._stats.avg_fps = fps_counter / (current_time - last_fps_time)
                    fps_counter = 0
                    last_fps_time = current_time

                    if debug:
                        print(f"FPS: {self._stats.avg_fps:.1f}, "
                              f"프레임: {frame_count}, "
                              f"점프: {self._stats.jumps_executed}")

                # 최대 프레임 체크
                if max_frames > 0 and frame_count >= max_frames:
                    break

                # FPS 제한
                if self.config.target_fps > 0:
                    target_frame_time = 1.0 / self.config.target_fps
                    elapsed = time.perf_counter() - loop_start
                    if elapsed < target_frame_time:
                        time.sleep(target_frame_time - elapsed)

        except Exception as e:
            print(f"\n오류 발생: {e}")
            raise
        finally:
            self._stats.end_time = time.perf_counter()
            self._stats.avg_latency_ms = self._controller.get_average_latency()
            self._running = False
            self._state = GameState.IDLE

        return self._stats

    def stop(self) -> None:
        """게임 루프 중지"""
        self._running = False

    def calibrate_region(self) -> Dict[str, int]:
        """
        게임 영역 캘리브레이션

        Returns:
            감지된 게임 영역
        """
        print("게임 영역 자동 감지 중...")
        detected = self._capture.auto_detect_game_region()

        if detected:
            print(f"감지됨: {detected}")
            self.config.capture_region = detected
            self._capture.region = detected
            return detected
        else:
            print("자동 감지 실패. 수동 설정 필요.")
            return self.config.capture_region

    def print_stats(self) -> None:
        """통계 출력"""
        print("\n" + "=" * 60)
        print("게임 통계")
        print("=" * 60)
        stats = self._stats.to_dict()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print("=" * 60)


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='T-Rex Runner Automator')
    parser.add_argument('--debug', action='store_true', help='디버그 모드')
    parser.add_argument('--no-start', action='store_true', help='자동 시작 비활성화')
    parser.add_argument('--frames', type=int, default=0, help='최대 프레임 수')
    parser.add_argument('--calibrate', action='store_true', help='게임 영역 캘리브레이션')
    args = parser.parse_args()

    # 게임 설정
    config = GameConfig()

    # 자동 플레이어 생성
    automator = DinoGameAutomator(config)

    if args.calibrate:
        automator.calibrate_region()
        return

    # 게임 실행
    try:
        stats = automator.run(
            auto_start=not args.no_start,
            debug=args.debug,
            max_frames=args.frames
        )
        automator.print_stats()
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단됨")
        automator.print_stats()


if __name__ == "__main__":
    main()
