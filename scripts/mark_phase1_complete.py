#!/usr/bin/env python3
"""
Phase 1 MVP 완료 - Jira 작업 상태 업데이트 스크립트

모든 T-01 ~ T-14 작업을 "Done" 상태로 전환합니다.
"""

import sys
import os

# 스크립트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jira_automation_manager import JiraAutomationManager


def main():
    """Phase 1 작업들을 완료 처리"""

    print("=" * 60)
    print("Phase 1 MVP 완료 - Jira 상태 업데이트")
    print("=" * 60)

    # 완료된 작업 목록 (T-01 ~ T-14)
    completed_tasks = [
        ("T-01", "MSS 라이브러리 설정 및 화면 캡처 모듈 구현"),
        ("T-02", "캡처 영역 좌표 설정 로직 구현"),
        ("T-03", "FPS 측정 및 최적화"),
        ("T-04", "OpenCV 그레이스케일 변환 구현"),
        ("T-05", "Canny Edge Detection 적용"),
        ("T-06", "전처리 파이프라인 통합"),
        ("T-07", "공룡 앞 ROI 영역 정의"),
        ("T-08", "픽셀 밀도 기반 장애물 감지 알고리즘"),
        ("T-09", "거리 계산 함수 구현"),
        ("T-10", "PyDirectInput 환경 설정"),
        ("T-11", "점프 명령 전송 함수 구현"),
        ("T-12", "입력 지연 측정 및 최적화"),
        ("T-13", "메인 게임 루프 통합"),
        ("T-14", "통합 테스트 및 버그 수정"),
    ]

    # Jira 매니저 초기화
    try:
        manager = JiraAutomationManager(project_key='DIN')
    except Exception as e:
        print(f"❌ Jira 연결 실패: {e}")
        return 1

    # 현재 프로젝트의 모든 서브태스크 검색
    print("\n🔍 Jira에서 Phase 1 작업 검색 중...")

    # JQL로 서브태스크 검색
    jql = 'project = DIN AND issuetype = Sub-task ORDER BY created ASC'
    issues = manager.search_issues(jql, max_results=50)

    if not issues:
        print("⚠️ 서브태스크를 찾을 수 없습니다.")
        print("수동으로 Jira에서 작업 상태를 업데이트해주세요.")
        return 0

    # 작업 이름과 Jira 이슈 매칭
    task_issue_map = {}
    for issue in issues:
        summary = issue['fields']['summary']
        key = issue['key']

        # T-XX 패턴 매칭
        for task_id, task_name in completed_tasks:
            if task_id in summary or task_name in summary:
                task_issue_map[task_id] = {
                    'key': key,
                    'summary': summary,
                    'status': issue['fields']['status']['name']
                }
                break

    print(f"\n📋 매칭된 작업: {len(task_issue_map)}/{len(completed_tasks)}")

    # 상태 전환
    success_count = 0
    failed_tasks = []

    for task_id, task_name in completed_tasks:
        if task_id in task_issue_map:
            issue_info = task_issue_map[task_id]
            issue_key = issue_info['key']
            current_status = issue_info['status']

            if current_status == 'Done':
                print(f"✓ {task_id} ({issue_key}): 이미 완료됨")
                success_count += 1
            else:
                print(f"🔄 {task_id} ({issue_key}): {current_status} → Done")

                # Done으로 전환 시도
                if manager.transition_issue(issue_key, 'Done'):
                    print(f"  ✅ 성공")
                    success_count += 1

                    # 완료 코멘트 추가
                    comment = f"✅ {task_id} 구현 완료\n\n구현된 파일:\n- src/ 디렉토리 참조"
                    manager.add_comment(issue_key, comment)
                else:
                    # In Progress 먼저 시도
                    if manager.transition_issue(issue_key, 'In Progress'):
                        if manager.transition_issue(issue_key, 'Done'):
                            print(f"  ✅ 성공 (In Progress 경유)")
                            success_count += 1
                        else:
                            print(f"  ❌ 실패")
                            failed_tasks.append(task_id)
                    else:
                        print(f"  ❌ 실패")
                        failed_tasks.append(task_id)
        else:
            print(f"⚠️ {task_id}: Jira 이슈를 찾을 수 없음")
            failed_tasks.append(task_id)

    # 결과 요약
    print("\n" + "=" * 60)
    print("결과 요약")
    print("=" * 60)
    print(f"✅ 완료: {success_count}/{len(completed_tasks)}")

    if failed_tasks:
        print(f"❌ 실패: {failed_tasks}")
        print("\n수동으로 Jira에서 상태를 업데이트해주세요:")
        print("https://letscoding.atlassian.net/jira/software/projects/DIN")

    return 0 if not failed_tasks else 1


if __name__ == '__main__':
    sys.exit(main())
