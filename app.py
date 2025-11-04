from openai import OpenAI
import streamlit as st
import pandas as pd
import json
import re
from dotenv import load_dotenv
import os
import requests
import re
import logging
import traceback
load_dotenv()

# 로깅 설정
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

# 로깅 초기화
log_file_path = setup_logging()


#######################  llm 호출 함수 ########################

def llm_call_openai(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """
    주어진 프롬프트로 OpenAI LLM을 동기적으로 호출합니다.
    기본 모델: gpt-3.5-turbo (가장 안정적이고 경제적)
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # API 키 정리 (공백, 줄바꿈 제거)
    if openai_api_key:
        openai_api_key = openai_api_key.strip()
    
    logging.info(f"🔑 API 키 확인: {'설정됨' if openai_api_key else '없음'}")
    if openai_api_key:
        logging.info(f"🔑 API 키 길이: {len(openai_api_key)} 문자")
        logging.info(f"🔑 API 키 시작: {openai_api_key[:10]}...")
    
    logging.info(f"🤖 사용 모델: {model}")
    logging.info(f"📝 프롬프트 길이: {len(prompt)} 문자")
    
    if not openai_api_key:
        raise ValueError("OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    
    try:
        client = OpenAI(api_key=openai_api_key)
        messages = [{"role": "user", "content": prompt}]
        
        logging.info("📡 OpenAI API 호출 시작...")
        chat_completion = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        
        response_content = chat_completion.choices[0].message.content
        logging.info(f"✅ OpenAI API 호출 성공 - 응답 길이: {len(response_content)} 문자")
        print(model, "완료")
        return response_content
        
    except Exception as e:
        logging.error(f"❌ OpenAI API 호출 실패: {str(e)}")
        logging.error(f"📋 상세 오류: {traceback.format_exc()}")
        
        # 일반적인 오류 메시지 해석
        error_str = str(e)
        if "401" in error_str or "Unauthorized" in error_str:
            logging.error("🚨 인증 오류: API 키가 유효하지 않습니다.")
        elif "400" in error_str or "Bad Request" in error_str:
            logging.error("🚨 잘못된 요청: 모델명이나 요청 형식을 확인해주세요.")
        elif "429" in error_str:
            logging.error("🚨 요청 한도 초과: 잠시 후 다시 시도해주세요.")
        elif "500" in error_str:
            logging.error("🚨 서버 오류: OpenAI 서버에 문제가 있습니다.")
            
        raise e



# 만약 ollama를 이용할 경우 활용


def llm_call(prompt: str) -> str:
    """
    사용자가 선택한 LLM 서비스와 모델을 사용하여 호출
    """
    
    # 세션 상태에서 선택된 서비스와 모델 확인
    if not hasattr(st.session_state, 'llm_service') or not hasattr(st.session_state, 'selected_model'):
        # 기본값 설정 (Ollama 우선)
        if check_ollama_connection():
            st.session_state.llm_service = "ollama"
            models = get_available_ollama_models()
            st.session_state.selected_model = models[0] if models else "qwen3:latest"
        elif os.getenv("OPENAI_API_KEY"):
            st.session_state.llm_service = "openai"
            st.session_state.selected_model = "gpt-3.5-turbo"
        else:
            raise Exception("사용 가능한 LLM 서비스가 없습니다. Ollama를 설치하거나 OpenAI API 키를 설정해주세요.")
    
    service = st.session_state.llm_service
    model = st.session_state.selected_model
    
    logging.info(f"🎯 선택된 서비스: {service}, 모델: {model}")
    
    try:
        if service == "ollama":
            logging.info(f"🦙 Ollama 모델 호출: {model}")
            return llm_call_ollama(prompt, model)
        elif service == "openai":
            logging.info(f"🤖 OpenAI 모델 호출: {model}")
            return llm_call_openai(prompt, model)
        else:
            raise Exception(f"알 수 없는 서비스: {service}")
            
    except Exception as e:
        logging.error(f"❌ {service} 호출 실패: {str(e)}")
        
        # 사용자에게 오류 표시
        if service == "ollama":
            st.error(f"❌ Ollama 모델 '{model}' 호출 실패: {str(e)}")
            st.info("💡 해결 방법: 'ollama serve' 명령으로 서버를 시작하거나 다른 모델을 선택해주세요.")
        elif service == "openai":
            st.error(f"❌ OpenAI 모델 '{model}' 호출 실패: {str(e)}")
            if "insufficient_quota" in str(e) or "429" in str(e):
                st.info("💡 해결 방법: OpenAI 계정에 크레딧을 추가하거나 Ollama를 사용해주세요.")
        
        raise e

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
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        return []
    except:
        return []

def llm_call_ollama(prompt: str, model: str = None) -> str:
    """
    Ollama의 REST API를 사용하여 지정된 모델을 호출합니다.
    """
    logging.info("=" * 60)
    logging.info("🦙 Ollama 함수 호출 시작")
    logging.info("=" * 60)
    logging.info(f"📝 요청 모델: {model if model else '자동 선택'}")
    logging.info(f"📏 프롬프트 길이: {len(prompt)} 문자")

    def remove_think_tags(text: str) -> str:
        """
        Removes all content enclosed in <think>...</think> tags from the input text.
        """
        # 여러 패턴으로 <think> 태그 제거
        patterns = [
            r"<think>.*?</think>",  # 기본 패턴
            r"<think>[\s\S]*?</think>",  # 줄바꿈 포함
            r"<think>.*",  # 닫는 태그가 없는 경우
        ]
        
        cleaned_text = text
        for pattern in patterns:
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.DOTALL | re.IGNORECASE)
        
        # 추가 정리: 연속된 공백과 줄바꿈 정리
        cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)  # 연속된 빈 줄 제거
        cleaned_text = re.sub(r'^\s+', '', cleaned_text, flags=re.MULTILINE)  # 줄 시작 공백 제거
        
        return cleaned_text.strip()

    # 1. 서버 연결 확인
    logging.info("🔍 1단계: Ollama 서버 연결 확인 중...")
    if not check_ollama_connection():
        logging.error("❌ Ollama 서버 연결 실패")
        logging.error("💡 해결 방법: 터미널에서 'ollama serve' 실행")
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
        logging.error("💡 해결 방법:")
        logging.error("   1. ollama pull qwen2.5:3b")
        logging.error("   2. ollama pull llama3.2:3b")
        logging.error("   3. ollama pull gpt-oss:latest")
        raise Exception("설치된 Ollama 모델이 없습니다. 'ollama pull qwen2.5:3b' 명령으로 모델을 다운로드하세요.")
    
    # 3. 모델 선택
    logging.info("🔍 3단계: 모델 선택 중...")
    if model and model in available_models:
        selected_model = model
        logging.info(f"✅ 사용자 지정 모델 사용: {selected_model}")
    else:
        if model and model not in available_models:
            logging.warning(f"⚠️ 요청한 모델 '{model}'을(를) 찾을 수 없음")
            logging.warning(f"💡 사용 가능한 모델: {', '.join(available_models)}")
        
        # 지정된 모델이 없거나 사용 불가능한 경우 우선순위에 따라 선택
        preferred_models = ["qwen2.5:3b", "qwen2.5:7b", "qwen2.5:1.5b", "qwen3:latest", "llama3.2:3b", "llama3.1:latest", "llama3.1:8b", "gpt-oss:latest"]
        selected_model = None
        
        for preferred_model in preferred_models:
            if preferred_model in available_models:
                selected_model = preferred_model
                logging.info(f"✅ 우선순위 모델 선택: {selected_model}")
                break
        
        if not selected_model:
            # 우선순위 모델이 없으면 첫 번째 사용 가능한 모델 사용
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
        logging.info(f"⏳ Ollama API 호출 시작 (timeout: 180초)...")
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=180)
        
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
            logging.error(f"📋 받은 키: {list(result.keys())}")
            logging.error(f"📋 전체 응답: {str(result)[:500]}")
            raise Exception(f"Ollama 응답 형식 오류: {result}")
        
        response_text = result["response"]
        logging.info(f"✅ Ollama 호출 성공!")
        logging.info(f"📏 응답 길이: {len(response_text)} 문자")
        logging.info(f"📝 응답 샘플 (처음 200자):")
        logging.info(f"   {response_text[:200]}...")
        print(f"🦙 {selected_model} 응답 완료")
        
        # <think> 태그 제거
        cleaned_response = remove_think_tags(response_text)
        if len(cleaned_response) != len(response_text):
            logging.info(f"🧹 <think> 태그 제거 완료")
            logging.info(f"   변경 전: {len(response_text)} 문자")
            logging.info(f"   변경 후: {len(cleaned_response)} 문자")
        
        logging.info("=" * 60)
        return cleaned_response
        
    except requests.exceptions.Timeout:
        logging.error("❌ Ollama 응답 시간 초과 (180초)")
        logging.error("💡 가능한 원인:")
        logging.error("   1. 모델이 너무 큼 (30B 모델은 매우 느림)")
        logging.error("   2. 서버 과부하")
        logging.error("   3. 컴퓨터 리소스 부족")
        logging.error("💡 해결 방법:")
        logging.error("   1. 더 작은 모델 사용 (qwen3:1.7b, qwen3:latest)")
        logging.error("   2. 질문을 더 간단하게 작성")
        logging.error("   3. Ollama 재시작: pkill ollama && ollama serve")
        logging.error("=" * 60)
        raise Exception(f"Ollama 응답 시간 초과 (180초). 모델 '{selected_model}'이(가) 너무 크거나 서버가 과부하 상태입니다. 더 작은 모델(qwen3:1.7b)을 사용해보세요.")
    except requests.exceptions.ConnectionError as e:
        logging.error("❌ Ollama 서버 연결 끊김")
        logging.error(f"📋 상세 오류: {str(e)}")
        logging.error("💡 해결 방법: 터미널에서 'ollama serve' 실행")
        logging.error("=" * 60)
        raise Exception("Ollama 서버 연결 끊김. 서버가 실행 중인지 확인하세요.")
    except json.JSONDecodeError as e:
        logging.error("❌ JSON 파싱 오류")
        logging.error(f"📋 상세 오류: {str(e)}")
        logging.error(f"📋 받은 응답 (처음 500자): {response.text[:500]}")
        logging.error("=" * 60)
        raise Exception(f"Ollama 응답 JSON 파싱 실패: {str(e)}")
    except Exception as e:
        logging.error("❌ 예상치 못한 오류")
        logging.error(f"📋 오류 유형: {type(e).__name__}")
        logging.error(f"📋 오류 메시지: {str(e)}")
        logging.error(f"📋 스택 트레이스:")
        logging.error(traceback.format_exc())
        logging.error("=" * 60)
        raise e

#######################  파일 처리 유틸리티 ########################

def detect_file_encoding(uploaded_file):
    """업로드된 파일의 인코딩을 감지합니다"""
    try:
        # chardet 라이브러리가 있으면 사용
        import chardet
        
        # 파일의 일부를 읽어서 인코딩 감지
        uploaded_file.seek(0)
        raw_data = uploaded_file.read(10000)  # 처음 10KB만 읽기
        uploaded_file.seek(0)  # 파일 포인터 리셋
        
        result = chardet.detect(raw_data)
        detected_encoding = result.get('encoding', 'utf-8')
        confidence = result.get('confidence', 0)
        
        logging.info(f"🔍 감지된 인코딩: {detected_encoding} (신뢰도: {confidence:.2f})")
        return detected_encoding
        
    except ImportError:
        logging.info("📝 chardet 라이브러리가 없어 기본 인코딩 순서로 시도합니다.")
        return None
    except Exception as e:
        logging.warning(f"⚠️ 인코딩 감지 실패: {e}")
        return None

#######################  헬퍼 함수 : DataFrame을 텍스트 테이블로 변환 ########################

def df_to_text_table(df_preview: list, df_types: dict) -> tuple:
    """
    DataFrame 미리보기를 읽기 쉬운 텍스트 테이블로 변환
    
    Args:
        df_preview: DataFrame의 dict 형태 미리보기 (리스트)
        df_types: 각 컬럼의 데이터 타입 딕셔너리
        
    Returns:
        (type_text, preview_text): 타입 정보와 미리보기 텍스트
    """
    columns = list(df_types.keys())
    
    # 데이터 타입 텍스트
    type_lines = ["데이터 컬럼 정보:"]
    for col, dtype in df_types.items():
        type_lines.append(f"  - {col}: {dtype}")
    type_text = "\n".join(type_lines)
    
    # 데이터 미리보기 텍스트
    preview_lines = ["\n데이터 샘플 (처음 5행):"]
    if df_preview:
        # 헤더
        header = " | ".join(str(col) for col in columns)
        preview_lines.append("  " + header)
        preview_lines.append("  " + "-" * min(len(header), 100))
        
        # 데이터 행
        for row in df_preview:
            values = [str(row.get(col, ""))[:30] for col in columns]  # 각 값 최대 30자
            preview_lines.append("  " + " | ".join(values))
    
    preview_text = "\n".join(preview_lines)
    
    return type_text, preview_text


#######################  1단계 : code 생성 ########################
def generate_code_prompt(user_query: str, df_preview: dict, df_types: dict) -> str:
    """
    사용자 질문에 대한 코드 생성 프롬프트를 텍스트 형식으로 생성
    """
    # JSON 대신 텍스트 테이블로 변환
    type_text, preview_text = df_to_text_table(df_preview, df_types)
    
    prompt = f"""다음은 pandas DataFrame(df)에 대한 정보입니다:

{type_text}

{preview_text}

사용자 질문: "{user_query}"

위 데이터를 바탕으로 사용자 질문에 답하기 위한 Python 코드를 생성하세요.

요구사항:
1. df는 이미 로드되어 있다고 가정
2. 최종 결과는 final_df라는 DataFrame으로 반환
3. 단일 값이 아닌 관련된 전체 맥락 포함 (정렬, 비교, 비율 등)
   - 예: "가장 높은 층수는?" → 모든 행정구를 층수로 정렬한 DataFrame 반환
4. 생성된 코드는 반드시 <result></result> XML 태그 안에 작성
5. import문이나 print문은 포함하지 않음
6. 코드는 반드시 final_df = ... 형태로 끝남
7. <think> 태그나 설명 없이 실행 가능한 Python 코드만 작성

응답 예시:
<result>
sorted_df = df.groupby("행정구")["층수"].max().reset_index()
sorted_df = sorted_df.sort_values(by="층수", ascending=False)
final_df = sorted_df
</result>

현재 질문에 대한 코드만 <result> 태그 안에 작성해주세요.
"""
    return prompt

#######################  2단계 : code 추출 및 실행 ########################


def extract_code_from_response(response: str) -> str:
    """
    LLM 응답에서 Python 코드를 추출합니다.
    여러 패턴을 시도하여 가장 적합한 코드를 찾습니다.
    """
    
    logging.info("=" * 60)
    logging.info("🔍 코드 추출 단계 시작")
    logging.info("=" * 60)
    logging.info(f"📏 응답 길이: {len(response)} 문자")
    logging.info(f"📝 응답 샘플 (처음 300자):")
    logging.info(f"   {response[:300]}...")
    logging.info("-" * 60)
    
    # 1. <result> 태그 우선 추출
    result_patterns = [
        r"<result>(.*?)</result>",
        r"<code>(.*?)</code>",
        r"<python>(.*?)</python>"
    ]
    
    for pattern in result_patterns:
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            code_block = match.group(1)
            # 마크다운 코드블럭 표시 제거
            code_block = re.sub(r"```[a-zA-Z]*\n?", "", code_block)
            code_block = re.sub(r"```\n?", "", code_block)
            code_block = code_block.strip()
            
            if code_block:
                logging.info(f"✅ {pattern} 태그에서 코드 추출 성공 - 길이: {len(code_block)} 문자")
                return code_block

    # 2. 마크다운 코드블럭에서 추출
    markdown_patterns = [
        r"```python\n(.*?)```",
        r"```py\n(.*?)```", 
        r"```\n(.*?)```",
        r"```(.*?)```"
    ]
    
    for pattern in markdown_patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            code_block = match.group(1).strip()
            if code_block and any(keyword in code_block.lower() for keyword in ['df', 'final_df', 'pandas', 'groupby']):
                logging.info(f"✅ 마크다운 블럭에서 코드 추출 성공 - 길이: {len(code_block)} 문자")
                return code_block

    # 3. 직접 Python 코드 패턴 찾기
    # final_df가 포함된 라인들을 찾아서 코드 블럭 추정
    lines = response.split('\n')
    code_lines = []
    in_code_block = False
    
    for line in lines:
        line = line.strip()
        
        # Python 코드로 보이는 라인 감지
        if any(keyword in line for keyword in ['df[', 'df.', 'final_df', 'pd.', 'groupby', 'value_counts', 'reset_index']):
            in_code_block = True
            code_lines.append(line)
        elif in_code_block and (line.startswith('final_df') or 'final_df' in line):
            code_lines.append(line)
            break  # final_df 할당으로 끝
        elif in_code_block and line and not line.startswith('#') and '=' in line:
            code_lines.append(line)
        elif in_code_block and not line:
            continue  # 빈 줄은 건너뛰기
        elif in_code_block:
            break  # 코드 블럭 끝
    
    if code_lines:
        extracted_code = '\n'.join(code_lines)
        logging.info(f"✅ 직접 패턴 매칭으로 코드 추출 성공 - 길이: {len(extracted_code)} 문자")
        return extracted_code

    # 4. 마지막 시도: 전체 응답에서 Python 코드 같은 부분 찾기
    # 간단한 휴리스틱: df나 pandas 관련 키워드가 있는 라인들
    potential_code_lines = []
    for line in response.split('\n'):
        line = line.strip()
        if line and any(keyword in line for keyword in ['df', 'pd.', 'import pandas', 'final_df']):
            potential_code_lines.append(line)
    
    if potential_code_lines:
        fallback_code = '\n'.join(potential_code_lines)
        logging.warning(f"⚠️ 휴리스틱으로 코드 추출 시도 - 길이: {len(fallback_code)} 문자")
        logging.info("=" * 60)
        return fallback_code

    # 모든 시도 실패
    logging.error("=" * 60)
    logging.error("❌ 코드 추출 실패 - 모든 패턴 매칭 실패")
    logging.error("=" * 60)
    logging.error("📋 LLM 응답 전체:")
    for i, line in enumerate(response.split('\n')[:50], 1):  # 처음 50줄만
        logging.error(f"   {i:3d}| {line}")
    if len(response.split('\n')) > 50:
        logging.error(f"   ... (총 {len(response.split('\n'))} 줄)")
    logging.error("-" * 60)
    logging.error("💡 가능한 원인:")
    logging.error("   1. LLM이 <result> 태그를 사용하지 않음")
    logging.error("   2. 코드가 마크다운 형식이 아님")
    logging.error("   3. 'final_df' 변수가 없음")
    logging.error("   4. LLM이 설명만 하고 코드를 생성하지 않음")
    logging.error("=" * 60)
    return ""

def execute_generated_code(code: str, df: pd.DataFrame, max_retries: int = 3):
    logging.info("=" * 60)
    logging.info("⚙️ 코드 실행 단계 시작")
    logging.info("=" * 60)
    logging.info(f"📏 코드 길이: {len(code)} 문자")
    logging.info(f"🔁 최대 재시도 횟수: {max_retries}")
    logging.info(f"📊 입력 데이터: {len(df)}행 × {len(df.columns)}열")
    logging.info("-" * 60)
    logging.info("📝 실행할 코드:")
    for i, line in enumerate(code.split('\n'), 1):
        logging.info(f"   {i:3d}| {line}")
    logging.info("-" * 60)
    
    current_code = code
    error_history = []
    
    for attempt in range(max_retries):
        logging.info(f"🔄 시도 {attempt + 1}/{max_retries}")
        try:
            local_vars = {"df": df, "final_df": None}
            logging.info("⏳ exec() 실행 중...")
            exec(current_code, {}, local_vars)
            
            final_df = local_vars.get("final_df", None)
            if final_df is not None:
                logging.info("✅ 코드 실행 성공!")
                logging.info(f"📊 결과 데이터: {len(final_df)}행 × {len(final_df.columns)}열")
                logging.info(f"📋 결과 컬럼: {list(final_df.columns)}")
                logging.info("=" * 60)
            else:
                logging.warning("⚠️ 코드는 실행되었으나 final_df가 None입니다")
                logging.info("=" * 60)
            return final_df
        except Exception as e:
            error_message = str(e)
            error_history.append(f"Attempt {attempt + 1} failed: {error_message}")
            
            logging.error(f"❌ 코드 실행 실패 (시도 {attempt + 1}/{max_retries})")
            logging.error(f"📋 오류 유형: {type(e).__name__}")
            logging.error(f"📋 오류 메시지: {error_message}")
            logging.error(f"📋 스택 트레이스:")
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    logging.error(f"   {line}")
            
            if attempt < max_retries - 1:  # 마지막 시도에는 새로운 코드 생성하지 않음
                logging.info(f"🔄 재시도 {attempt + 2}/{max_retries} 준비 중...")
                # 코드 수정을 위한 새로운 프롬프트 생성
                error_prompt = f"""
                다음 코드에서 오류가 발생했습니다:
                {current_code}
                
                오류 메시지:
                {error_message}
                
                이전에 발생한 오류들:
                {chr(10).join(error_history[:-1])}
                
                1. 모든 데이터 타입 변환 문제 처리
                2. 누락되거나 유효하지 않은 값 처리
                3. 적절한 데이터 타입 처리 사용
                4. 'final_df'라는 이름의 필터링된 DataFrame 또는 피벗 테이블 반환
                5. 동일한 문제가 반복되지 않도록 이전 오류 고려
                
                수정된 코드는 <result></result> XML 태그 안에 작성해주세요.
                """
                
                # LLM에서 수정된 코드 추출
                corrected_response = llm_call(error_prompt)
                corrected_code = extract_code_from_response(corrected_response)
                
                if corrected_code:
                    current_code = corrected_code
                else:
                    return f"코드 수정에 실패했습니다. 오류 기록: {chr(10).join(error_history)}"
            else:
                return f"최대 시도 횟수({max_retries})에 도달했습니다. 오류 기록: {chr(10).join(error_history)}"
    
    return f"예상치 못한 오류: {chr(10).join(error_history)}"


#######################  3단계 : 답변 생성 ########################


def generate_final_prompt(user_query: str, filtered_df: pd.DataFrame) -> str:
    """
    필터링된 데이터를 일반 텍스트 형태로 변환하여 최종 답변 생성 프롬프트 작성
    """
    # DataFrame을 읽기 쉬운 텍스트로 변환
    data_text_lines = [f"분석 결과 데이터 (총 {len(filtered_df)}개 행):"]
    data_text_lines.append("")
    
    # 데이터가 적으면 전체 표시, 많으면 상위 10개만
    display_df = filtered_df.head(10) if len(filtered_df) > 10 else filtered_df
    
    if len(display_df) > 0:
        # 컬럼명
        columns = list(display_df.columns)
        max_col_width = 20  # 각 컬럼 최대 너비
        
        # 헤더
        header = " | ".join(str(col)[:max_col_width] for col in columns)
        data_text_lines.append(header)
        data_text_lines.append("-" * min(len(header), 100))
        
        # 데이터 행
        for idx, row in display_df.iterrows():
            values = [str(row[col])[:max_col_width] for col in columns]
            data_text_lines.append(" | ".join(values))
        
        if len(filtered_df) > 10:
            data_text_lines.append(f"\n... (총 {len(filtered_df)}개 행 중 상위 10개만 표시)")
    else:
        data_text_lines.append("(데이터 없음)")
    
    data_text = "\n".join(data_text_lines)
    
    prompt = f"""다음은 사용자 질문에 대한 데이터 분석 결과입니다:

사용자 질문: {user_query}

{data_text}

위 데이터를 바탕으로 질문에 대한 명확하고 간결한 답변을 한국어로 작성해주세요.

답변 작성 가이드:
- 핵심 정보를 먼저 제시
- 데이터에서 확인된 구체적인 수치나 사실 포함
- 필요시 추가 인사이트나 비교 정보 제공
- 자연스러운 문장으로 작성 (불필요한 포맷팅 없이)
"""
    return prompt


def test_logging():
    """로깅 테스트 함수"""
    try:
        logging.info("🧪 로깅 테스트 메시지")
        logging.warning("⚠️ 경고 테스트 메시지")
        logging.error("❌ 오류 테스트 메시지")
        return True
    except Exception as e:
        print(f"로깅 테스트 실패: {e}")
        return False

def main():
    st.title("내 엑셀데이터와 대화하기")
    
    # 페이지 로드 시 로깅 테스트 및 환경 확인
    if 'logging_tested' not in st.session_state:
        st.session_state.logging_tested = True
        test_logging()
        
        # OpenAI API 키 상태 로깅
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            openai_key = openai_key.strip()
            logging.info("=" * 60)
            logging.info("🔑 OpenAI API 키 확인")
            logging.info("=" * 60)
            logging.info(f"✅ API 키 존재: 예")
            logging.info(f"📏 API 키 길이: {len(openai_key)} 문자")
            logging.info(f"🔤 API 키 시작: {openai_key[:10]}...")
            logging.info(f"🔤 API 키 끝: ...{openai_key[-4:]}")
            
            # API 키 형식 검증
            if openai_key.startswith('sk-'):
                logging.info("✅ API 키 형식: 올바름 (sk-로 시작)")
            else:
                logging.warning("⚠️ API 키 형식: 의심스러움 (sk-로 시작하지 않음)")
            
            # 공백이나 특수문자 확인
            if ' ' in openai_key:
                logging.warning("⚠️ API 키에 공백이 포함되어 있습니다!")
            if '\n' in openai_key or '\r' in openai_key:
                logging.warning("⚠️ API 키에 줄바꿈 문자가 포함되어 있습니다!")
            
            logging.info("=" * 60)
        else:
            logging.warning("=" * 60)
            logging.warning("⚠️ OpenAI API 키 확인")
            logging.warning("=" * 60)
            logging.warning("❌ API 키 존재: 아니오")
            logging.warning("💡 .env 파일에 OPENAI_API_KEY를 설정해주세요")
            logging.warning("=" * 60)
    
    # 사이드바에 모델 선택 옵션 추가
    with st.sidebar:
        st.header("🤖 모델 설정")
        
        # LLM 서비스 상태 확인
        ollama_available = check_ollama_connection()
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            openai_key = openai_key.strip()
        openai_available = bool(openai_key and len(openai_key) > 0)
        
        # API 키 상태 표시
        st.write("---")
        st.write("**🔑 API 키 상태**")
        if openai_available:
            # API 키가 있는 경우
            st.success(f"✅ OpenAI API 키: 설정됨")
            with st.expander("🔍 API 키 정보"):
                st.code(f"키 길이: {len(openai_key)} 문자")
                st.code(f"시작: {openai_key[:10]}...")
                st.code(f"끝: ...{openai_key[-4:]}")
                
                # 키 형식 검증
                if openai_key.startswith('sk-'):
                    st.success("✅ 형식: 올바름 (sk-로 시작)")
                else:
                    st.warning("⚠️ 형식: 의심스러움 (sk-로 시작하지 않음)")
                
                # 문제 감지
                issues = []
                if ' ' in openai_key:
                    issues.append("공백 포함")
                if '\n' in openai_key or '\r' in openai_key:
                    issues.append("줄바꿈 포함")
                
                if issues:
                    st.warning(f"⚠️ 문제 감지: {', '.join(issues)}")
                else:
                    st.success("✅ 문제 없음")
        else:
            # API 키가 없는 경우
            st.warning("⚠️ OpenAI API 키: 미설정")
            st.info("💡 .env 파일에 OPENAI_API_KEY를 추가하세요")
            
            # API 키 설정 가이드
            with st.expander("📝 API 키 설정 방법"):
                st.markdown("""
                **1. OpenAI API 키 발급**
                - https://platform.openai.com/api-keys
                - 계정 생성 및 로그인
                - "Create new secret key" 클릭
                
                **2. .env 파일 생성**
                ```bash
                # 프로젝트 루트에 .env 파일 생성
                cd /Users/loveauden/Development/vibe_pandas_project
                echo "OPENAI_API_KEY=your-api-key-here" > .env
                ```
                
                **3. Streamlit 재시작**
                - Ctrl+C로 종료 후 다시 실행
                """)
        
        # Ollama 상태 표시
        st.write("---")
        st.write("**🦙 Ollama 상태**")
        if ollama_available:
            st.success("✅ Ollama: 사용 가능")
        else:
            st.warning("⚠️ Ollama: 사용 불가")
            with st.expander("📝 Ollama 설치 방법"):
                st.markdown("""
                **1. Ollama 설치**
                ```bash
                brew install ollama
                ```
                
                **2. 모델 다운로드**
                ```bash
                ollama pull qwen2.5:3b
                ```
                
                **3. Ollama 서버 시작**
                ```bash
                ollama serve
                ```
                """)
        
        st.write("---")
        
        # 사용 가능한 서비스 옵션 생성 (우선순위: Ollama > OpenAI)
        service_options = []
        default_service = None
        
        # API 키가 없으면 Ollama를 우선으로
        if not openai_available and ollama_available:
            service_options.append("🦙 Ollama (로컬)")
            default_service = "ollama"
            st.info("💡 OpenAI API 키가 없어 Ollama를 사용합니다")
            logging.info("🦙 OpenAI API 키 없음 - Ollama로 자동 전환")
        else:
            # 두 서비스 모두 사용 가능한 경우
            if ollama_available:
                service_options.append("🦙 Ollama (로컬)")
            if openai_available:
                service_options.append("🤖 OpenAI (클라우드)")
        
        if not service_options:
            st.error("❌ 사용 가능한 LLM 서비스가 없습니다!")
            st.warning("⚠️ 다음 중 하나를 설정해주세요:")
            st.info("1. Ollama 설치 및 실행 (무료)")
            st.info("2. OpenAI API 키 설정 (유료)")
            return
        
        # LLM 서비스 선택
        selected_service = st.selectbox(
            "LLM 서비스 선택:",
            service_options,
            index=0
        )
        
        # 선택된 서비스에 따른 모델 옵션
        if "Ollama" in selected_service and ollama_available:
            available_models = get_available_ollama_models()
            if available_models:
                st.write("**사용 가능한 Ollama 모델:**")
                
                # 빠른 모델을 기본값으로 설정
                fast_models = ["qwen3:1.7b", "qwen3:latest", "qwen2.5:3b", "llama3.2:3b"]
                default_index = 0
                for i, model in enumerate(available_models):
                    if model in fast_models:
                        default_index = i
                        break
                
                selected_model = st.selectbox(
                    "모델 선택:",
                    available_models,
                    index=default_index,
                    help="⚡ 빠른 모델 추천: qwen3:1.7b, qwen3:latest, llama3.2:3b"
                )
                
                # 모델 정보 표시
                model_size_info = {
                    "qwen3:1.7b": "⚡⚡⚡ 매우 빠름 (2B) - 추천!",
                    "qwen3:latest": "⚡⚡ 빠름 (8B) - 균형잡힌 선택",
                    "qwen2.5:3b": "⚡⚡ 빠름 (3B)",
                    "llama3.2:3b": "⚡⚡ 빠름 (3B)",
                    "gpt-oss:latest": "⚡ 보통 (21B) - 정확하지만 느림",
                    "qwen3:30b": "🐢 느림 (30B) - 복잡한 작업용",
                    "qwen3-coder:30b": "🐢 느림 (30B) - 코딩 특화"
                }
                model_info = model_size_info.get(selected_model, "")
                if model_info:
                    st.success(f"선택된 모델: {selected_model}\n{model_info}")
                else:
                    st.info(f"선택된 모델: {selected_model}")
                
                # 세션 상태에 저장
                st.session_state.llm_service = "ollama"
                st.session_state.selected_model = selected_model
                
                # 큰 모델 경고
                if "30b" in selected_model.lower() or ("gpt-oss" in selected_model.lower()):
                    st.warning("⚠️ 큰 모델을 선택하셨습니다. 응답 시간이 수 분 걸릴 수 있습니다.")
                    st.info("💡 빠른 응답을 원하시면 qwen3:1.7b 또는 qwen3:latest를 추천합니다.")
            else:
                st.error("❌ 설치된 Ollama 모델이 없습니다.")
                st.info("💡 다음 명령으로 모델을 다운로드하세요:")
                st.code("ollama pull qwen2.5:3b", language="bash")
                st.info("또는 다른 모델:")
                st.code("ollama pull llama3.2:3b\nollama pull qwen2.5:7b", language="bash")
                return
                
        elif "OpenAI" in selected_service and openai_available:
            openai_models = [
                "gpt-3.5-turbo",      # 가장 저렴하고 빠름
                "gpt-4-turbo",        # GPT-4의 빠른 버전
                "gpt-4",              # 가장 강력
                "gpt-4o",             # 최신 모델 (존재 시)
            ]
            
            selected_model = st.selectbox(
                "OpenAI 모델 선택:",
                openai_models,
                index=0,
                help="gpt-3.5-turbo를 권장합니다 (빠르고 저렴)"
            )
            
            # 모델별 정보 표시
            model_info = {
                "gpt-3.5-turbo": "💰 저렴 | ⚡ 빠름 | 👍 권장",
                "gpt-4-turbo": "💰💰 보통 | ⚡ 빠름 | 🎯 정확",
                "gpt-4": "💰💰💰 비쌈 | 🐢 느림 | 🎯🎯 매우 정확",
                "gpt-4o": "💰💰 보통 | ⚡⚡ 매우 빠름 | 🆕 최신"
            }
            
            st.info(f"선택된 모델: {selected_model}")
            if selected_model in model_info:
                st.info(f"특징: {model_info[selected_model]}")
            st.warning("⚠️ OpenAI 사용 시 요금이 발생합니다")
            
            # 세션 상태에 저장
            st.session_state.llm_service = "openai"
            st.session_state.selected_model = selected_model
        
        # 모델 상태 표시
        st.write("---")
        st.write("**현재 설정:**")
        if hasattr(st.session_state, 'llm_service'):
            service_name = "Ollama" if st.session_state.llm_service == "ollama" else "OpenAI"
            st.success(f"서비스: {service_name}")
            st.success(f"모델: {st.session_state.selected_model}")
        
        # 로그 파일 상태 표시
        st.write("---")
        st.write("**로그 상태**")
        if log_file_path and os.path.exists(log_file_path):
            file_size = os.path.getsize(log_file_path)
            st.success(f"📝 로그: {file_size} bytes")
            
            # 로그 파일 다운로드 버튼
            if st.button("📥 로그 다운로드"):
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                st.download_button(
                    label="💾 app.log 다운로드",
                    data=log_content,
                    file_name="app.log",
                    mime="text/plain"
                )
        else:
            st.warning("📝 로그: 파일 없음")
    
    # 파일 업로드
    uploaded_file = st.file_uploader("파일 업로드", type=["xls", "xlsx", "csv"])
    if uploaded_file:
        logging.info("=" * 60)
        logging.info("📁 파일 업로드 시작")
        logging.info("=" * 60)
        logging.info(f"📄 파일명: {uploaded_file.name}")
        logging.info(f"📦 파일 크기: {uploaded_file.size:,} bytes")
        
        file_type = uploaded_file.name.split('.')[-1].lower()
        logging.info(f"📝 파일 타입: {file_type}")
        
        if file_type == 'csv':
            # CSV 파일 인코딩 자동 감지 및 처리
            logging.info("🔍 CSV 파일 인코딩 감지 시작...")
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
                logging.info("✅ CSV 파일을 UTF-8로 성공적으로 로드했습니다.")
            except UnicodeDecodeError as e:
                logging.warning(f"⚠️ UTF-8 인코딩 실패: {str(e)}")
                try:
                    # 한국어 CSV 파일의 경우 EUC-KR 또는 CP949 시도
                    uploaded_file.seek(0)  # 파일 포인터 리셋
                    df = pd.read_csv(uploaded_file, encoding='euc-kr')
                    logging.info("✅ CSV 파일을 EUC-KR로 성공적으로 로드했습니다.")
                except UnicodeDecodeError as e:
                    logging.warning(f"⚠️ EUC-KR 인코딩 실패: {str(e)}")
                    try:
                        uploaded_file.seek(0)  # 파일 포인터 리셋
                        df = pd.read_csv(uploaded_file, encoding='cp949')
                        logging.info("✅ CSV 파일을 CP949로 성공적으로 로드했습니다.")
                    except UnicodeDecodeError as e:
                        logging.warning(f"⚠️ CP949 인코딩 실패: {str(e)}")
                        try:
                            uploaded_file.seek(0)  # 파일 포인터 리셋
                            df = pd.read_csv(uploaded_file, encoding='latin1')
                            logging.info("✅ CSV 파일을 Latin1로 성공적으로 로드했습니다.")
                        except Exception as e:
                            logging.error(f"❌ 모든 인코딩 시도 실패: {str(e)}")
                            logging.error(f"📋 상세 오류: {traceback.format_exc()}")
                            st.error(f"❌ CSV 파일 인코딩을 인식할 수 없습니다: {str(e)}")
                            st.info("💡 해결 방법: CSV 파일을 UTF-8 인코딩으로 저장해주세요.")
                            return
        else:
            logging.info("🔍 Excel 파일 로드 시작...")
            try:
                df = pd.read_excel(uploaded_file)
                logging.info("✅ Excel 파일을 성공적으로 로드했습니다.")
            except Exception as e:
                logging.error(f"❌ Excel 파일 로드 실패: {str(e)}")
                logging.error(f"📋 상세 오류: {traceback.format_exc()}")
                st.error(f"❌ Excel 파일을 읽을 수 없습니다: {str(e)}")
                st.info("💡 해결 방법: 파일이 손상되지 않았는지 확인해주세요.")
                return

        # 데이터프레임 정보 로깅
        logging.info("📊 데이터프레임 정보:")
        logging.info(f"  - 행 수: {len(df):,}")
        logging.info(f"  - 열 수: {len(df.columns)}")
        logging.info(f"  - 컬럼: {list(df.columns)[:10]}{'...' if len(df.columns) > 10 else ''}")
        logging.info(f"  - 메모리 사용량: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        logging.info("=" * 60)

        # 파일 정보 표시
        st.success(f"✅ 파일 업로드 성공: {uploaded_file.name}")
        st.info(f"📊 데이터 크기: {len(df)}행 × {len(df.columns)}열")
        
        with st.expander("데이터 미리보기(사람용)"):
            st.dataframe(df.head(5))

        df_preview = df.head(5).to_dict(orient="records")
        with st.expander("데이터 미리보기(LLM용)"):
            st.json(df_preview)
        
        df_types = df.dtypes.apply(lambda x: str(x)).to_dict()
        with st.expander("데이터타입 미리보기(LLM용)"):
            st.json(df_types)
        
        questions = [
            "서울에서 업종별(대분류)로 가장 많은 상점이 있는 구는 어디인가요?",
            "서울에서 카페가 위치한 평균 층수가 가장 높은 구는 어디인가요?", 
            "서울에서 부동산 중개업이 전체 상가에서 차지하는 비중이 가장 높은 지역은 어디인가요?",
            "성동구에서 업종별(중분류) 상점 비중은 어떻게 되나요?",
        ]

        if "user_query" not in st.session_state:
            st.session_state["user_query"] = ""

        user_input = st.text_input(
            "데이터에 대해 질문해주세요:",
            key="input_box"
        )

        if not user_input:
            sample = st.selectbox("또는 예시 질문을 선택해주세요:", questions, key="sample_box")
            user_query = sample
        else:
            user_query = user_input

        if st.button("질문하기"):
            st.session_state["user_query"] = user_query
            if user_query:
                try:
                    logging.info("=" * 60)
                    logging.info("💬 질문 처리 시작")
                    logging.info("=" * 60)
                    logging.info(f"❓ 사용자 질문: {user_query}")
                    logging.info(f"📊 데이터 크기: {len(df)}행 × {len(df.columns)}열")
                    
                    # LLM 서비스 확인
                    service = st.session_state.get('llm_service', 'openai')
                    model = st.session_state.get('selected_model', 'gpt-4o-mini')
                    logging.info(f"🤖 사용할 서비스: {service}")
                    logging.info(f"🤖 사용할 모델: {model}")
                    
                    # 1단계: 코드 생성 프롬프트 생성
                    logging.info("📋 1단계: 코드 생성 프롬프트 생성 중...")
                    code_prompt = generate_code_prompt(user_query, df_preview, df_types)
                    logging.info(f"📏 프롬프트 길이: {len(code_prompt)} 문자")
                    
                    # 2단계: LLM 호출로 코드 생성
                    logging.info("🤖 2단계: LLM 호출로 코드 생성 중...")
                    logging.info(f"📡 API 호출 준비 중... (서비스: {service}, 모델: {model})")
                    generated_response = llm_call(code_prompt)
                    logging.info(f"✅ LLM 응답 수신 완료 (길이: {len(generated_response)} 문자)")
                    
                    # 3단계: 코드 추출
                    logging.info("🔍 3단계: 생성된 응답에서 코드 추출 중...")
                    generated_code = extract_code_from_response(generated_response)
                    logging.info(f"📝 추출된 코드 길이: {len(generated_code) if generated_code else 0} 문자")
                    
                    # 4단계: 코드 실행
                    logging.info("⚙️ 4단계: 생성된 코드 실행 중...")
                    filtered_df = execute_generated_code(generated_code, df)
                    
                    if isinstance(filtered_df, pd.DataFrame):
                        logging.info("✅ 코드 실행 성공 - DataFrame 생성됨")
                        
                        # 5단계: 최종 답변 생성
                        logging.info("📝 5단계: 최종 답변 생성 중...")
                        final_prompt = generate_final_prompt(user_query, filtered_df)
                        final_response = llm_call(final_prompt)
                        
                        logging.info("🎉 모든 단계 완료!")
                        
                        st.write("### 답변")
                        st.write(final_response)
                        
                        with st.expander("답변 근거"):
                            st.write("### 생성된 코드")
                            st.code(generated_code, language="python")

                            st.write("### 필터링된 데이터") 
                            st.dataframe(filtered_df)
                                                    
                            st.write("### 최종 질문 프롬프트")
                            st.code(final_prompt, language="json")

                    else:
                        logging.error(f"❌ 코드 실행 실패: {filtered_df}")
                        st.error(f"코드 실행 중 오류가 발생했습니다: {filtered_df}")
                        
                except Exception as e:
                    logging.error("=" * 60)
                    logging.error("💥 전체 프로세스 오류 발생")
                    logging.error("=" * 60)
                    logging.error(f"❌ 오류 유형: {type(e).__name__}")
                    logging.error(f"❌ 오류 메시지: {str(e)}")
                    logging.error(f"📋 상세 스택 트레이스:")
                    logging.error(traceback.format_exc())
                    
                    # 오류 유형별 상세 분석
                    error_str = str(e).lower()
                    if '400' in error_str or 'bad request' in error_str:
                        logging.error("🚨 AxiosError 400 감지!")
                        logging.error("📌 가능한 원인:")
                        logging.error("  1. 잘못된 모델명 (gpt-4o-mini는 존재하지 않을 수 있음)")
                        logging.error("  2. API 키 형식 오류")
                        logging.error("  3. 프롬프트 형식 문제")
                        logging.error("  4. 요청 페이로드 문제")
                        
                        # 현재 설정 확인
                        service = st.session_state.get('llm_service', '미설정')
                        model = st.session_state.get('selected_model', '미설정')
                        logging.error(f"📊 현재 설정: 서비스={service}, 모델={model}")
                        
                        st.error(f"❌ API 요청 오류 (400 Bad Request): {str(e)}")
                        st.warning("⚠️ 가능한 해결 방법:")
                        st.info("1. 다른 모델을 선택해보세요 (예: gpt-3.5-turbo)")
                        st.info("2. .env 파일의 OPENAI_API_KEY를 확인해보세요")
                        st.info("3. Ollama를 사용해보세요 (무료)")
                    elif '401' in error_str or 'unauthorized' in error_str:
                        logging.error("🚨 인증 오류 (401) 감지!")
                        st.error(f"❌ API 키 인증 오류: {str(e)}")
                        st.info("💡 .env 파일의 OPENAI_API_KEY를 확인해주세요")
                    elif '429' in error_str or 'rate limit' in error_str:
                        logging.error("🚨 요청 한도 초과 (429) 감지!")
                        st.error(f"❌ API 요청 한도 초과: {str(e)}")
                        st.info("💡 잠시 후 다시 시도하거나 Ollama를 사용해주세요")
                    else:
                        st.error(f"❌ 처리 중 오류가 발생했습니다: {str(e)}")
                    
                    logging.error("=" * 60)
                    
            else:
                st.warning("질문을 입력해주세요.")

if __name__ == "__main__":
    main()
