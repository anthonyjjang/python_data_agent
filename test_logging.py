#!/usr/bin/env python3
"""
로깅 시스템 테스트 스크립트
"""

import os
import logging
import sys

def test_logging_setup():
    """로깅 설정 테스트"""
    print("🧪 로깅 시스템 테스트 시작")
    print("=" * 40)
    
    # 현재 디렉토리 확인
    current_dir = os.getcwd()
    print(f"📁 현재 디렉토리: {current_dir}")
    
    # 로그 파일 경로 설정
    log_file_path = os.path.join(current_dir, 'test_app.log')
    print(f"📝 로그 파일 경로: {log_file_path}")
    
    # 디렉토리 쓰기 권한 확인
    try:
        test_file = os.path.join(current_dir, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ 디렉토리 쓰기 권한: 정상")
    except Exception as e:
        print(f"❌ 디렉토리 쓰기 권한 오류: {e}")
        return False
    
    # 로깅 설정
    try:
        # 기존 핸들러 제거
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # 새 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path, encoding='utf-8'),
                logging.StreamHandler()
            ],
            force=True
        )
        
        print("✅ 로깅 설정: 완료")
        
    except Exception as e:
        print(f"❌ 로깅 설정 오류: {e}")
        return False
    
    # 로그 메시지 테스트
    try:
        logging.info("🚀 테스트 INFO 메시지")
        logging.warning("⚠️ 테스트 WARNING 메시지")
        logging.error("❌ 테스트 ERROR 메시지")
        
        print("✅ 로그 메시지 전송: 완료")
        
    except Exception as e:
        print(f"❌ 로그 메시지 전송 오류: {e}")
        return False
    
    # 로그 파일 생성 확인
    if os.path.exists(log_file_path):
        file_size = os.path.getsize(log_file_path)
        print(f"✅ 로그 파일 생성: 성공 ({file_size} bytes)")
        
        # 로그 파일 내용 확인
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.strip().split('\n')
                print(f"📄 로그 파일 내용: {len(lines)}줄")
                
                # 마지막 몇 줄 출력
                print("📋 최근 로그:")
                for line in lines[-3:]:
                    print(f"   {line}")
                    
        except Exception as e:
            print(f"❌ 로그 파일 읽기 오류: {e}")
            
        return True
    else:
        print("❌ 로그 파일 생성: 실패")
        return False

def test_streamlit_logging():
    """Streamlit 환경에서의 로깅 테스트"""
    print("\n🎯 Streamlit 로깅 테스트")
    print("=" * 40)
    
    # Streamlit 모듈 확인
    try:
        import streamlit as st
        print("✅ Streamlit 모듈: 사용 가능")
    except ImportError:
        print("❌ Streamlit 모듈: 없음")
        return False
    
    # app.py에서 사용하는 것과 동일한 로깅 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(current_dir, 'streamlit_test.log')
    
    try:
        # 기존 핸들러 제거
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Streamlit 호환 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path, encoding='utf-8'),
                logging.StreamHandler()
            ],
            force=True
        )
        
        # 테스트 로그
        logging.info("🎯 Streamlit 환경 테스트 로그")
        
        if os.path.exists(log_file_path):
            print(f"✅ Streamlit 로그 파일 생성: 성공")
            print(f"📁 파일 위치: {log_file_path}")
            return True
        else:
            print("❌ Streamlit 로그 파일 생성: 실패")
            return False
            
    except Exception as e:
        print(f"❌ Streamlit 로깅 테스트 오류: {e}")
        return False

def main():
    print("🔍 로깅 시스템 진단 도구")
    print("=" * 50)
    
    # 기본 로깅 테스트
    basic_test = test_logging_setup()
    
    # Streamlit 로깅 테스트
    streamlit_test = test_streamlit_logging()
    
    print("\n📊 테스트 결과 요약")
    print("=" * 40)
    print(f"기본 로깅: {'✅ 성공' if basic_test else '❌ 실패'}")
    print(f"Streamlit 로깅: {'✅ 성공' if streamlit_test else '❌ 실패'}")
    
    if basic_test and streamlit_test:
        print("\n🎉 모든 로깅 테스트 통과!")
        print("이제 app.py를 실행하면 로그 파일이 정상적으로 생성됩니다.")
    else:
        print("\n⚠️ 로깅 문제가 발견되었습니다.")
        print("권한 설정이나 파일 시스템을 확인해주세요.")

if __name__ == "__main__":
    main()