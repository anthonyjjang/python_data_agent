#!/usr/bin/env python3
"""
OpenAI API 디버깅 테스트 스크립트
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import logging
import traceback

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_openai_connection():
    """OpenAI API 연결 테스트"""
    
    print("=" * 50)
    print("🔍 OpenAI API 디버깅 테스트 시작")
    print("=" * 50)
    
    # 1. 환경 변수 로드
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    print(f"📁 현재 작업 디렉토리: {os.getcwd()}")
    print(f"📄 .env 파일 존재: {os.path.exists('.env')}")
    
    if api_key:
        api_key = api_key.strip()
        print(f"🔑 API 키 설정됨: 길이 {len(api_key)} 문자")
        print(f"🔑 API 키 시작: {api_key[:15]}...")
        print(f"🔑 API 키 끝: ...{api_key[-10:]}")
    else:
        print("❌ API 키가 설정되지 않음!")
        return False
    
    # 2. OpenAI 클라이언트 생성 테스트
    try:
        print("\n🤖 OpenAI 클라이언트 생성 중...")
        client = OpenAI(api_key=api_key)
        print("✅ 클라이언트 생성 성공")
    except Exception as e:
        print(f"❌ 클라이언트 생성 실패: {e}")
        return False
    
    # 3. 간단한 API 호출 테스트
    test_models = ["gpt-4o-mini", "gpt-3.5-turbo"]
    
    for model in test_models:
        print(f"\n🧪 모델 테스트: {model}")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "안녕하세요. 간단한 테스트입니다. '테스트 성공'이라고 답해주세요."}
                ],
                max_tokens=50
            )
            
            result = response.choices[0].message.content
            print(f"✅ {model} 테스트 성공!")
            print(f"📝 응답: {result}")
            return True
            
        except Exception as e:
            print(f"❌ {model} 테스트 실패: {e}")
            print(f"📋 상세 오류:")
            print(traceback.format_exc())
            
            # HTTP 상태 코드 확인
            if hasattr(e, 'response'):
                print(f"🌐 HTTP 상태 코드: {e.response.status_code}")
                print(f"🌐 응답 내용: {e.response.text}")
    
    return False

# 4. API 키 유효성 직접 확인
def validate_api_key():
    """API 키 유효성 직접 확인"""
    print("\n" + "=" * 50)
    print("🔐 API 키 유효성 검증")
    print("=" * 50)
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ API 키가 없습니다.")
        return False
    
    api_key = api_key.strip()
    
    # API 키 형식 검증
    if not api_key.startswith('sk-'):
        print(f"❌ API 키 형식이 잘못되었습니다. 'sk-'로 시작해야 합니다.")
        return False
    
    if len(api_key) < 50:
        print(f"❌ API 키가 너무 짧습니다. 길이: {len(api_key)}")
        return False
    
    print("✅ API 키 형식이 올바릅니다.")
    
    # 실제 API 호출로 유효성 확인
    try:
        client = OpenAI(api_key=api_key)
        
        # 가장 간단한 API 호출
        response = client.models.list()
        print("✅ API 키가 유효합니다!")
        print(f"📊 사용 가능한 모델 수: {len(response.data)}")
        
        # gpt-4o-mini 모델 사용 가능 여부 확인
        available_models = [model.id for model in response.data]
        if "gpt-4o-mini" in available_models:
            print("✅ gpt-4o-mini 모델 사용 가능")
        else:
            print("⚠️ gpt-4o-mini 모델을 찾을 수 없습니다.")
            print("📋 사용 가능한 GPT 모델들:")
            gpt_models = [m for m in available_models if 'gpt' in m.lower()]
            for model in gpt_models[:5]:  # 처음 5개만 표시
                print(f"   - {model}")
        
        return True
        
    except Exception as e:
        print(f"❌ API 키 검증 실패: {e}")
        print(f"📋 상세 오류:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("🚀 OpenAI API 디버깅 시작\n")
    
    # API 키 검증
    if validate_api_key():
        # 연결 테스트
        test_openai_connection()
    else:
        print("\n❌ API 키 검증에 실패했습니다. 먼저 API 키를 확인해주세요.")
    
    print("\n🏁 디버깅 완료")