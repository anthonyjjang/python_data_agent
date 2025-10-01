#!/usr/bin/env python3
"""
app.py의 함수들을 직접 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import llm_call, check_ollama_connection, get_available_ollama_models, llm_call_ollama

def test_ollama_functions():
    print("🧪 Ollama 함수 테스트")
    print("=" * 40)
    
    # 1. 연결 테스트
    print("1. Ollama 연결 테스트...")
    connection = check_ollama_connection()
    print(f"   결과: {'✅ 연결됨' if connection else '❌ 연결 실패'}")
    
    if not connection:
        print("❌ Ollama 서버가 실행되지 않았습니다.")
        return False
    
    # 2. 모델 목록 테스트
    print("\n2. 모델 목록 조회...")
    models = get_available_ollama_models()
    print(f"   사용 가능한 모델: {models}")
    
    if not models:
        print("❌ 사용 가능한 모델이 없습니다.")
        return False
    
    # 3. 직접 Ollama 호출 테스트
    print("\n3. Ollama 직접 호출 테스트...")
    try:
        test_prompt = "안녕하세요. 간단한 테스트입니다. '테스트 성공'이라고 한국어로 답해주세요."
        response = llm_call_ollama(test_prompt)
        print(f"   응답: {response[:100]}...")
        print("   ✅ Ollama 직접 호출 성공")
    except Exception as e:
        print(f"   ❌ Ollama 직접 호출 실패: {e}")
        return False
    
    # 4. 통합 llm_call 함수 테스트
    print("\n4. 통합 llm_call 함수 테스트...")
    try:
        response = llm_call(test_prompt)
        print(f"   응답: {response[:100]}...")
        print("   ✅ 통합 함수 호출 성공")
        return True
    except Exception as e:
        print(f"   ❌ 통합 함수 호출 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama_functions()
    
    if success:
        print("\n🎉 모든 테스트 통과!")
        print("이제 Streamlit 앱을 실행할 수 있습니다.")
    else:
        print("\n❌ 테스트 실패")
        print("Ollama 설정을 확인해주세요.")