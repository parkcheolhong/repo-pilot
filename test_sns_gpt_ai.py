#!/usr/bin/env python3
"""
SNS GPT AI 프로그램 - 명령줄 테스트 버전
GUI 환경이 없는 경우를 위한 기본 기능 테스트
"""

import os
import logging
import sys

# 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def test_core_functions():
    """핵심 기능들이 제대로 동작하는지 테스트"""
    print("=== SNS GPT AI 프로그램 테스트 ===")
    
    # 기본 Python 모듈 테스트
    modules_to_test = {
        'os': 'os',
        'logging': 'logging', 
        'threading': 'threading',
        'sys': 'sys'
    }
    
    print("\n1. 기본 모듈 테스트:")
    for name, module in modules_to_test.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError as e:
            print(f"  ✗ {name}: {e}")
    
    # 선택적 의존성 테스트
    optional_modules = {
        'MoviePy (영상 편집)': 'moviepy.editor',
        'OpenAI (GPT API)': 'openai',
        'Speech Recognition (음성 인식)': 'speech_recognition',
        'Pillow (이미지 처리)': 'PIL',
        'OpenCV (영상 처리)': 'cv2',
        'Pygame (오디오 재생)': 'pygame',
        'Tkinter (GUI)': 'tkinter'
    }
    
    print("\n2. 선택적 의존성 테스트:")
    available_modules = []
    missing_modules = []
    
    for name, module in optional_modules.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
            available_modules.append(name)
        except ImportError:
            print(f"  ✗ {name} (설치 필요)")
            missing_modules.append(name)
    
    # 시스템 정보
    print(f"\n3. 시스템 정보:")
    print(f"  Python 버전: {sys.version}")
    print(f"  운영체제: {os.name}")
    print(f"  현재 작업 디렉토리: {os.getcwd()}")
    
    # 테스트 결과 요약
    print(f"\n4. 테스트 결과:")
    print(f"  사용 가능한 모듈: {len(available_modules)}개")
    print(f"  누락된 모듈: {len(missing_modules)}개")
    
    if missing_modules:
        print(f"\n5. 설치 권장사항:")
        print("  다음 명령으로 누락된 패키지를 설치하세요:")
        print("  pip install -r requirements.txt")
        print("\n  주의: GUI 기능은 데스크톱 환경에서만 동작합니다.")
    
    # 기본 기능 테스트
    print("\n6. 기본 기능 테스트:")
    
    # 로깅 테스트
    try:
        logging.info("로깅 기능 테스트 성공")
        print("  ✓ 로깅 기능")
    except Exception as e:
        print(f"  ✗ 로깅 기능: {e}")
    
    # 파일 시스템 테스트
    try:
        test_file = "test_file.tmp"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("  ✓ 파일 시스템 접근")
    except Exception as e:
        print(f"  ✗ 파일 시스템 접근: {e}")
    
    return len(missing_modules) == 0

def mock_video_editing():
    """영상 편집 기능의 모의 실행"""
    print("\n=== 영상 편집 모의 실행 ===")
    print("입력: 가상의 영상 파일 (input.mp4)")
    print("편집 구간: 10초 ~ 60초")
    print("출력: 편집된 영상 파일 (output.mp4)")
    print("상태: 모의 실행 완료 ✓")

def mock_speech_recognition():
    """음성 인식 기능의 모의 실행"""
    print("\n=== 음성 인식 모의 실행 ===")
    print("입력: 영상 오디오 트랙")
    print("처리: Google Speech Recognition API")
    print("출력: '안녕하세요, 이것은 테스트 영상입니다.'")
    print("상태: 모의 실행 완료 ✓")

def mock_gpt_summary():
    """GPT 요약 기능의 모의 실행"""
    print("\n=== GPT 요약 모의 실행 ===")
    print("입력: '안녕하세요, 이것은 테스트 영상입니다.'")
    print("처리: OpenAI GPT-4 API")
    print("출력:")
    print("  제목: 테스트 영상 소개")
    print("  키워드: #테스트 #영상 #소개")
    print("  소개글: 간단한 테스트 영상으로 기본 기능을 확인합니다.")
    print("상태: 모의 실행 완료 ✓")

def run_demo():
    """전체 워크플로우 데모 실행"""
    print("\n" + "="*50)
    print("SNS GPT AI 프로그램 워크플로우 데모")
    print("="*50)
    
    mock_video_editing()
    mock_speech_recognition() 
    mock_gpt_summary()
    
    print("\n=== 최종 결과 ===")
    print("편집된 영상: output.mp4")
    print("썸네일: thumbnail.jpg")
    print("소개글: 완성된 SNS 포스팅용 텍스트")
    print("\n프로그램 워크플로우 데모 완료! 🎉")

if __name__ == "__main__":
    try:
        # 핵심 기능 테스트
        all_modules_available = test_core_functions()
        
        # 데모 실행
        run_demo()
        
        print(f"\n{'='*50}")
        print("테스트 완료!")
        
        if all_modules_available:
            print("모든 의존성이 준비되었습니다. GUI 버전을 실행할 수 있습니다.")
        else:
            print("일부 의존성이 누락되었지만 기본 구조는 정상입니다.")
            print("실제 사용을 위해서는 requirements.txt의 패키지들을 설치하세요.")
            
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        sys.exit(1)