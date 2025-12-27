"""
T-10: PyDirectInput 환경 설정
T-11: 점프 명령 전송 함수 구현
T-12: 입력 지연 측정 및 최적화

US-04: 키보드 입력 제어
- PyDirectInput 기반 입력 시스템
- Space 키 점프 명령 구현
- 입력 지연 5ms 이하
"""

import time
import platform
from typing import Optional, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass

# 플랫폼별 입력 모듈 로드
PLATFORM = platform.system()

if PLATFORM == 'Windows':
    try:
        import pydirectinput
        DIRECT_INPUT_AVAILABLE = True
    except ImportError:
        DIRECT_INPUT_AVAILABLE = False
        pydirectinput = None
else:
    DIRECT_INPUT_AVAILABLE = False
    pydirectinput = None

# 크로스 플랫폼 대안
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None


class InputAction(Enum):
    """입력 액션 타입"""
    JUMP = 'jump'
    DUCK = 'duck'
    NONE = 'none'


@dataclass
class InputTiming:
    """입력 타이밍 측정 결과"""
    action: InputAction
    requested_time: float
    executed_time: float
    latency_ms: float


class KeyboardController:
    """저지연 키보드 입력 컨트롤러"""

    # 키 매핑
    KEY_JUMP = 'space'
    KEY_DUCK = 'down'
    KEY_START = 'space'

    # 기본 설정
    DEFAULT_JUMP_DURATION = 0.05  # 점프 키 유지 시간
    DEFAULT_DUCK_DURATION = 0.3   # 숙기 키 유지 시간

    def __init__(
        self,
        use_direct_input: bool = True,
        jump_duration: float = DEFAULT_JUMP_DURATION,
        duck_duration: float = DEFAULT_DUCK_DURATION
    ):
        """
        키보드 컨트롤러 초기화 (T-10)

        Args:
            use_direct_input: Windows에서 DirectInput 사용 여부
            jump_duration: 점프 키 유지 시간 (초)
            duck_duration: 숙기 키 유지 시간 (초)
        """
        self._jump_duration = jump_duration
        self._duck_duration = duck_duration
        self._use_direct_input = use_direct_input and DIRECT_INPUT_AVAILABLE

        # 입력 함수 선택
        self._setup_input_backend()

        # 쿨다운 관리
        self._last_jump_time = 0.0
        self._last_duck_time = 0.0
        self._jump_cooldown = 0.3  # 점프 쿨다운 (초)
        self._duck_cooldown = 0.5  # 숙기 쿨다운 (초)

        # 지연 시간 측정
        self._latency_samples: list = []
        self._max_samples = 100

    def _setup_input_backend(self) -> None:
        """입력 백엔드 설정 (T-10)"""
        if self._use_direct_input and DIRECT_INPUT_AVAILABLE:
            # PyDirectInput (Windows, 저지연)
            pydirectinput.PAUSE = 0  # 명령 간 대기 제거
            self._press = pydirectinput.press
            self._keyDown = pydirectinput.keyDown
            self._keyUp = pydirectinput.keyUp
            self._backend = 'pydirectinput'
        elif PYAUTOGUI_AVAILABLE:
            # PyAutoGUI (크로스플랫폼)
            pyautogui.PAUSE = 0
            pyautogui.FAILSAFE = False  # 안전 장치 비활성화 (성능)
            self._press = pyautogui.press
            self._keyDown = pyautogui.keyDown
            self._keyUp = pyautogui.keyUp
            self._backend = 'pyautogui'
        else:
            raise ImportError(
                "키보드 입력 라이브러리가 필요합니다: "
                "pip install pyautogui (또는 Windows: pip install pydirectinput)"
            )

    @property
    def backend(self) -> str:
        """현재 사용 중인 입력 백엔드"""
        return self._backend

    def jump(self) -> Optional[InputTiming]:
        """
        점프 명령 전송 (T-11)

        Returns:
            입력 타이밍 정보 또는 None (쿨다운 중)
        """
        current_time = time.perf_counter()

        # 쿨다운 체크
        if current_time - self._last_jump_time < self._jump_cooldown:
            return None

        # 타이밍 측정 시작
        requested_time = current_time

        # 점프 키 입력
        self._press(self.KEY_JUMP)

        # 타이밍 측정 완료
        executed_time = time.perf_counter()
        latency_ms = (executed_time - requested_time) * 1000

        self._last_jump_time = executed_time
        self._record_latency(latency_ms)

        return InputTiming(
            action=InputAction.JUMP,
            requested_time=requested_time,
            executed_time=executed_time,
            latency_ms=latency_ms
        )

    def duck(self, duration: Optional[float] = None) -> Optional[InputTiming]:
        """
        숙기(Duck) 명령 전송

        Args:
            duration: 숙기 유지 시간 (None이면 기본값)

        Returns:
            입력 타이밍 정보 또는 None (쿨다운 중)
        """
        current_time = time.perf_counter()

        if current_time - self._last_duck_time < self._duck_cooldown:
            return None

        requested_time = current_time
        duck_time = duration or self._duck_duration

        # 숙기 키 유지
        self._keyDown(self.KEY_DUCK)
        time.sleep(duck_time)
        self._keyUp(self.KEY_DUCK)

        executed_time = time.perf_counter()
        latency_ms = (executed_time - requested_time - duck_time) * 1000

        self._last_duck_time = executed_time
        self._record_latency(latency_ms)

        return InputTiming(
            action=InputAction.DUCK,
            requested_time=requested_time,
            executed_time=executed_time,
            latency_ms=latency_ms
        )

    def start_game(self) -> None:
        """게임 시작 (스페이스바)"""
        self._press(self.KEY_START)

    def _record_latency(self, latency_ms: float) -> None:
        """지연 시간 기록 (T-12)"""
        self._latency_samples.append(latency_ms)
        if len(self._latency_samples) > self._max_samples:
            self._latency_samples.pop(0)

    def get_average_latency(self) -> float:
        """평균 입력 지연 시간 (ms)"""
        if not self._latency_samples:
            return 0.0
        return sum(self._latency_samples) / len(self._latency_samples)

    def benchmark(self, iterations: int = 50) -> Dict[str, Any]:
        """
        입력 지연 벤치마크 (T-12)

        Args:
            iterations: 테스트 반복 횟수

        Returns:
            벤치마크 결과
        """
        latencies = []

        for _ in range(iterations):
            start = time.perf_counter()
            # 실제 키 입력 없이 함수 호출 시간만 측정
            self._press(self.KEY_JUMP)
            latencies.append((time.perf_counter() - start) * 1000)
            time.sleep(0.05)  # 너무 빠른 입력 방지

        import numpy as np
        latencies = np.array(latencies)

        return {
            'backend': self._backend,
            'iterations': iterations,
            'avg_ms': float(np.mean(latencies)),
            'min_ms': float(np.min(latencies)),
            'max_ms': float(np.max(latencies)),
            'std_ms': float(np.std(latencies)),
            'meets_requirement': float(np.mean(latencies)) <= 5
        }

    def get_stats(self) -> Dict[str, Any]:
        """컨트롤러 통계"""
        return {
            'backend': self._backend,
            'jump_duration': self._jump_duration,
            'duck_duration': self._duck_duration,
            'jump_cooldown': self._jump_cooldown,
            'duck_cooldown': self._duck_cooldown,
            'avg_latency_ms': self.get_average_latency(),
            'latency_samples': len(self._latency_samples)
        }

    def execute_action(self, action: InputAction) -> Optional[InputTiming]:
        """
        액션 실행

        Args:
            action: 실행할 액션

        Returns:
            타이밍 정보 또는 None
        """
        if action == InputAction.JUMP:
            return self.jump()
        elif action == InputAction.DUCK:
            return self.duck()
        return None


def main():
    """테스트"""
    print("=" * 50)
    print("T-10~T-12: 키보드 컨트롤러 테스트")
    print("=" * 50)

    print(f"\n플랫폼: {PLATFORM}")
    print(f"DirectInput 사용 가능: {DIRECT_INPUT_AVAILABLE}")
    print(f"PyAutoGUI 사용 가능: {PYAUTOGUI_AVAILABLE}")

    try:
        controller = KeyboardController()
        print(f"\n사용 중인 백엔드: {controller.backend}")

        print("\n주의: 이 테스트는 실제 키 입력을 전송합니다!")
        print("3초 후 테스트 시작...")
        time.sleep(3)

        # 벤치마크
        print("\n벤치마크 실행 중...")
        results = controller.benchmark(20)

        print(f"\n결과:")
        print(f"  백엔드: {results['backend']}")
        print(f"  평균 지연: {results['avg_ms']:.2f}ms")
        print(f"  최소 지연: {results['min_ms']:.2f}ms")
        print(f"  최대 지연: {results['max_ms']:.2f}ms")
        print(f"  요구사항 충족 (≤5ms): {'✓' if results['meets_requirement'] else '✗'}")

    except ImportError as e:
        print(f"\n오류: {e}")
        print("필요한 라이브러리를 설치하세요.")


if __name__ == "__main__":
    main()
