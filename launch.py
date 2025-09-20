#!/usr/bin/env python3
"""
SNS GPT AI 런처 스크립트
의존성 확인 후 메인 프로그램을 실행합니다.
"""

import sys
import subprocess

def check_dependencies():
    """필요한 의존성이 설치되어 있는지 확인"""
    required_modules = [
        ('moviepy', 'moviepy'),
        ('openai', 'openai'),
        ('speech_recognition', 'SpeechRecognition'),
        ('PIL', 'Pillow'),
        ('cv2', 'opencv-python'),
        ('pygame', 'pygame'),
        ('tkinter', 'tkinter (usually pre-installed)')
    ]
    
    missing_modules = []
    
    for module, package in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(package)
    
    return missing_modules

def install_dependencies():
    """누락된 의존성 설치"""
    print("필요한 패키지를 설치하고 있습니다...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("=== SNS GPT AI 프로그램 런처 ===")
    
    # 의존성 확인
    missing = check_dependencies()
    
    if missing:
        print(f"\n누락된 패키지가 {len(missing)}개 있습니다:")
        for package in missing:
            print(f"  - {package}")
        
        response = input("\n자동으로 설치하시겠습니까? (y/n): ").lower()
        
        if response == 'y':
            if install_dependencies():
                print("✓ 패키지 설치 완료!")
                missing = check_dependencies()  # 재확인
            else:
                print("✗ 패키지 설치 실패!")
                print("수동으로 설치해주세요: pip install -r requirements.txt")
                return
        else:
            print("의존성을 먼저 설치해주세요: pip install -r requirements.txt")
            return
    
    if not missing:
        print("✓ 모든 의존성이 준비되었습니다!")
        
        # GUI 환경 확인
        try:
            import tkinter
            print("✓ GUI 환경 사용 가능")
            print("\nSNS GPT AI 프로그램을 시작합니다...")
            
            # 메인 프로그램 실행
            import sns_gpt_ai
            
        except ImportError:
            print("✗ GUI 환경을 사용할 수 없습니다.")
            print("테스트 모드로 실행합니다...")
            subprocess.run([sys.executable, 'test_sns_gpt_ai.py'])

if __name__ == "__main__":
    main()