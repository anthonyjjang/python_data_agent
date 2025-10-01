#!/usr/bin/env python3
"""
app.py와 동일한 로깅 설정으로 강제 로그 생성 테스트
"""

import os
import logging
import sys

# app.py와 동일한 로깅 설정
def setup_logging():
    """로깅 설정 함수"""
    # 현재 스크립트 디렉토리 기준으로 로그 파일 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(current_dir, 'app.log')
    
    # 기존 핸들러 제거 (중복 방지)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler()
        ],
        force=True  # 기존 설정 강제 덮어쓰기
    )
    
    # 로그 파일 생성 확인
    try:
        logging.info("🚀 로깅 시스템 초기화 완료")
        logging.info(f"📁 로그 파일 경로: {log_file_path}")
        print(f"📁 로그 파일 위치: {log_file_path}")
        return log_file_path
    except Exception as e:
        print(f"❌ 로그 파일 생성 실패: {e}")
        # 파일 로깅 실패 시 콘솔만 사용
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()],
            force=True
        )
        return None

def main():
    print("🔥 app.py 로깅 설정 강제 테스트")
    print("=" * 40)
    
    # 로깅 초기화
    log_file_path = setup_logging()
    
    if log_file_path:
        # 다양한 로그 메시지 생성
        logging.info("🚀 애플리케이션 시작")
        logging.info("🔑 API 키 확인: 테스트")
        logging.info("🤖 사용 모델: gpt-4o-mini")
        logging.warning("⚠️ 테스트 경고 메시지")
        logging.error("❌ 테스트 오류 메시지")
        logging.info("✅ 로깅 테스트 완료")
        
        # 파일 확인
        if os.path.exists(log_file_path):
            file_size = os.path.getsize(log_file_path)
            print(f"\n✅ app.log 파일 생성 성공!")
            print(f"📊 파일 크기: {file_size} bytes")
            
            # 파일 내용 출력
            with open(log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"\n📄 로그 파일 내용:")
                print("-" * 40)
                print(content)
                print("-" * 40)
        else:
            print("❌ app.log 파일이 생성되지 않았습니다.")
    else:
        print("❌ 로깅 설정에 실패했습니다.")

if __name__ == "__main__":
    main()