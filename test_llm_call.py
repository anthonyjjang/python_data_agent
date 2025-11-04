#!/usr/bin/env python3
"""
LLM 호출 테스트 스크립트
app.py의 llm_call_ollama 함수를 직접 테스트
"""

import sys
import os
import requests
import json
import re
import traceback

# 로깅 설정
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_ollama_connection() -> bool:
    """Ollama 서버 연결 상태 확인"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_available_ollama_models() -> list:
    """사용 가능한 Ollama 모델 목록 조회"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()["models"]
            return [model["name"] for model in models]
        return []
    except:
        return []

def remove_think_tags(text: str) -> str:
    """<think> 태그 제거"""
    patterns = [
        r"<think>.*?</think>",
        r"<think>[\s\S]*?</think>",
        r"<think>.*",
    ]
    
    cleaned_text = text
    for pattern in patterns:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.DOTALL | re.IGNORECASE)
    
    cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
    cleaned_text = re.sub(r'^\s+', '', cleaned_text, flags=re.MULTILINE)
    
    return cleaned_text.strip()

def test_llm_call_ollama(prompt: str, model: str = None) -> str:
    """
    Ollama LLM 호출 테스트 (app.py의 llm_call_ollama와 동일)
    """
    logging.info("=" * 60)
    logging.info("🦙 Ollama 함수 호출 시작")
    logging.info("=" * 60)
    logging.info(f"📝 요청 모델: {model if model else '자동 선택'}")
    logging.info(f"📏 프롬프트 길이: {len(prompt)} 문자")

    # 1. 서버 연결 확인
    logging.info("🔍 1단계: Ollama 서버 연결 확인 중...")
    if not check_ollama_connection():
        logging.error("❌ Ollama 서버 연결 실패")
        raise Exception("Ollama 서버에 연결할 수 없습니다. 'ollama serve' 명령으로 서버를 시작해주세요.")
    logging.info("✅ Ollama 서버 연결 성공 (http://localhost:11434)")
    
    # 2. 사용 가능한 모델 확인
    logging.info("🔍 2단계: 사용 가능한 모델 확인 중...")
    available_models = get_available_ollama_models()
    logging.info(f"🦙 사용 가능한 Ollama 모델 목록:")
    for idx, m in enumerate(available_models, 1):
        logging.info(f"   {idx}. {m}")
    
    if not available_models:
        logging.error("❌ 설치된 Ollama 모델 없음")
        raise Exception("설치된 Ollama 모델이 없습니다.")
    
    # 3. 모델 선택
    logging.info("🔍 3단계: 모델 선택 중...")
    if model and model in available_models:
        selected_model = model
        logging.info(f"✅ 사용자 지정 모델 사용: {selected_model}")
    else:
        if model and model not in available_models:
            logging.warning(f"⚠️ 요청한 모델 '{model}'을(를) 찾을 수 없음")
            logging.warning(f"💡 사용 가능한 모델: {', '.join(available_models)}")
        
        preferred_models = ["qwen2.5:3b", "qwen2.5:7b", "qwen3:latest", "gpt-oss:latest", "llama3.2:3b"]
        selected_model = None
        
        for preferred_model in preferred_models:
            if preferred_model in available_models:
                selected_model = preferred_model
                logging.info(f"✅ 우선순위 모델 선택: {selected_model}")
                break
        
        if not selected_model:
            selected_model = available_models[0]
            logging.info(f"⚠️ 우선순위 모델 없음 - 첫 번째 모델 사용: {selected_model}")
    
    # 4. API 호출
    logging.info("🔍 4단계: Ollama API 호출 준비...")
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 2048
        }
    }
    
    logging.info(f"📡 요청 URL: {url}")
    logging.info(f"🤖 최종 선택 모델: {selected_model}")
    logging.info(f"🎛️ 파라미터: temperature=0.7, top_p=0.9")
    
    try:
        logging.info(f"⏳ Ollama API 호출 시작 (timeout: 120초)...")
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
        
        logging.info(f"📨 HTTP 응답 수신 - 상태 코드: {response.status_code}")
        
        if response.status_code != 200:
            error_detail = response.text if response.text else "알 수 없는 오류"
            logging.error(f"❌ HTTP 오류 {response.status_code}")
            logging.error(f"📋 오류 상세: {error_detail}")
            raise Exception(f"Ollama API 호출 실패 (HTTP {response.status_code}): {error_detail}")

        result = response.json()
        logging.info(f"📦 JSON 응답 파싱 성공")
        logging.info(f"📋 응답 키: {list(result.keys())}")
        
        if "response" not in result:
            logging.error(f"❌ 응답 형식 오류 - 'response' 키 없음")
            raise Exception(f"Ollama 응답 형식 오류: {result}")
        
        response_text = result["response"]
        logging.info(f"✅ Ollama 호출 성공!")
        logging.info(f"📏 응답 길이: {len(response_text)} 문자")
        logging.info(f"📝 응답 샘플 (처음 300자):")
        logging.info(f"   {response_text[:300]}...")
        
        # <think> 태그 제거
        cleaned_response = remove_think_tags(response_text)
        if len(cleaned_response) != len(response_text):
            logging.info(f"🧹 <think> 태그 제거 완료")
            logging.info(f"   변경 전: {len(response_text)} 문자")
            logging.info(f"   변경 후: {len(cleaned_response)} 문자")
        
        logging.info("=" * 60)
        return cleaned_response
        
    except requests.exceptions.Timeout:
        logging.error("❌ Ollama 응답 시간 초과 (120초)")
        raise Exception("Ollama 응답 시간 초과")
    except Exception as e:
        logging.error("❌ 예상치 못한 오류")
        logging.error(f"📋 오류 유형: {type(e).__name__}")
        logging.error(f"📋 오류 메시지: {str(e)}")
        logging.error(traceback.format_exc())
        logging.error("=" * 60)
        raise e

def test_simple_question():
    """간단한 질문 테스트"""
    print("\n" + "=" * 60)
    print("📝 테스트 1: 간단한 질문")
    print("=" * 60)
    
    prompt = "안녕하세요! 당신의 이름은 무엇인가요? 간단히 한 문장으로 답해주세요."
    
    try:
        response = test_llm_call_ollama(prompt, model="gpt-oss:latest")
        print("\n✅ 테스트 1 성공!")
        print(f"📋 응답: {response}")
        return True
    except Exception as e:
        print(f"\n❌ 테스트 1 실패: {e}")
        return False

def test_code_generation():
    """코드 생성 테스트 (app.py와 동일한 형식)"""
    print("\n" + "=" * 60)
    print("📝 테스트 2: 코드 생성")
    print("=" * 60)
    
    prompt = """
다음은 pandas DataFrame(df)의 미리보기입니다:
{"0": {"정산월": "202503", "확정": 100}, "1": {"정산월": "202504", "확정": 200}}

각 컬럼의 데이터 타입은 다음과 같습니다:
{"정산월": "object", "확정": "int64"}

다음 사용자 질의에 기반하여 Python 코드를 생성하세요:
"202503 정산월의 데이터만 필터링해줘"

코드는 <result></result> XML 태그 안에 작성해주세요.
최종 결과는 새로운 DataFrame `final_df`로 반환되어야 합니다.

예시:
<result>
final_df = df[df['정산월'] == '202503']
</result>

현재 질문에 대한 코드만 <result> 태그 안에 작성해주세요.
"""
    
    try:
        response = test_llm_call_ollama(prompt, model="gpt-oss:latest")
        print("\n✅ 테스트 2 성공!")
        print(f"📋 응답 전체:\n{response}")
        
        # <result> 태그 확인
        if "<result>" in response and "</result>" in response:
            print("\n✅ <result> 태그 발견!")
            match = re.search(r"<result>(.*?)</result>", response, re.DOTALL)
            if match:
                code = match.group(1).strip()
                print(f"📋 추출된 코드:\n{code}")
                return True
            else:
                print("⚠️ <result> 태그는 있지만 추출 실패")
                return False
        else:
            print("❌ <result> 태그 없음 - 코드 생성 형식 문제")
            return False
            
    except Exception as e:
        print(f"\n❌ 테스트 2 실패: {e}")
        return False

def test_with_different_models():
    """여러 모델로 테스트"""
    print("\n" + "=" * 60)
    print("📝 테스트 3: 다양한 모델 테스트")
    print("=" * 60)
    
    available_models = get_available_ollama_models()
    prompt = "1 + 1은 무엇인가요? 숫자만 답해주세요."
    
    test_models = []
    for model in ["gpt-oss:latest", "qwen3:latest", "qwen3:1.7b"]:
        if model in available_models:
            test_models.append(model)
    
    if not test_models:
        test_models = [available_models[0]]
    
    results = []
    for model in test_models[:3]:  # 최대 3개 모델만 테스트
        print(f"\n🤖 모델: {model}")
        try:
            response = test_llm_call_ollama(prompt, model=model)
            print(f"✅ 성공: {response[:100]}")
            results.append(True)
        except Exception as e:
            print(f"❌ 실패: {e}")
            results.append(False)
    
    return any(results)

def main():
    """메인 테스트 실행"""
    print("\n" + "🧪 " * 20)
    print("LLM 호출 테스트 스크립트")
    print("🧪 " * 20)
    
    # 전제 조건 확인
    if not check_ollama_connection():
        print("\n❌ Ollama 서버가 실행되지 않았습니다")
        print("💡 해결 방법: 터미널에서 'ollama serve' 실행")
        sys.exit(1)
    
    available_models = get_available_ollama_models()
    if not available_models:
        print("\n❌ 설치된 Ollama 모델이 없습니다")
        print("💡 해결 방법: 'ollama pull gpt-oss:latest' 실행")
        sys.exit(1)
    
    print(f"\n✅ Ollama 서버 실행 중")
    print(f"✅ 설치된 모델 수: {len(available_models)}")
    
    # 테스트 실행
    results = []
    
    # 테스트 1: 간단한 질문
    results.append(("간단한 질문", test_simple_question()))
    
    # 테스트 2: 코드 생성
    results.append(("코드 생성", test_code_generation()))
    
    # 테스트 3: 다양한 모델
    results.append(("다양한 모델", test_with_different_models()))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 모든 테스트 통과!")
        print("\n💡 다음 단계:")
        print("  1. streamlit run app.py")
        print("  2. 정산요약.xlsx 업로드")
        print("  3. 질문 입력 및 테스트")
    else:
        print("⚠️ 일부 테스트 실패")
        print("\n💡 다음 단계:")
        print("  1. 로그 확인")
        print("  2. 다른 모델 시도 (ollama pull qwen2.5:3b)")
        print("  3. Ollama 재시작")
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()

