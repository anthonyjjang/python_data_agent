#!/usr/bin/env python3
"""
AxiosError 400 진단 스크립트
"""

import requests
import json
import pandas as pd
import os

def test_ollama_server():
    """Ollama 서버 테스트"""
    print("=" * 60)
    print("🦙 Ollama 서버 테스트")
    print("=" * 60)
    
    try:
        # 1. 서버 연결 확인
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama 서버 연결 성공")
            models = response.json()["models"]
            print(f"📋 설치된 모델 수: {len(models)}")
            for i, model in enumerate(models[:5], 1):
                print(f"   {i}. {model['name']}")
            return True
        else:
            print(f"❌ Ollama 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama 서버 연결 실패: {e}")
        print("💡 해결 방법: 터미널에서 'ollama serve' 실행")
        return False

def test_ollama_generation():
    """Ollama 코드 생성 테스트"""
    print("\n" + "=" * 60)
    print("🤖 Ollama 코드 생성 테스트")
    print("=" * 60)
    
    try:
        # 간단한 코드 생성 요청
        prompt = """
        다음은 pandas DataFrame(df)의 미리보기입니다:
        {"0": {"col1": 1, "col2": "A"}, "1": {"col1": 2, "col2": "B"}}
        
        다음 사용자 질의에 기반하여 Python 코드를 생성하세요:
        "col1이 1인 행을 필터링해줘"
        
        코드는 <result></result> XML 태그 안에 작성해주세요.
        
        예시:
        <result>
        final_df = df[df['col1'] == 1]
        </result>
        """
        
        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "gpt-oss:latest",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 2048
            }
        }
        
        print("📡 API 요청 전송 중...")
        print(f"🤖 모델: gpt-oss:latest")
        print(f"📏 프롬프트 길이: {len(prompt)} 문자")
        
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
        
        print(f"📨 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            print(f"✅ 코드 생성 성공!")
            print(f"📏 응답 길이: {len(response_text)} 문자")
            print(f"\n📝 생성된 응답:")
            print("-" * 60)
            print(response_text[:500])
            if len(response_text) > 500:
                print(f"... (총 {len(response_text)} 문자)")
            print("-" * 60)
            
            # <result> 태그 확인
            if "<result>" in response_text and "</result>" in response_text:
                print("✅ <result> 태그 발견!")
                import re
                match = re.search(r"<result>(.*?)</result>", response_text, re.DOTALL)
                if match:
                    code = match.group(1).strip()
                    print(f"\n📋 추출된 코드:")
                    print("-" * 60)
                    print(code)
                    print("-" * 60)
            else:
                print("⚠️ <result> 태그가 없습니다 - 코드 추출 실패 가능성")
            
            return True
        else:
            print(f"❌ API 호출 실패: HTTP {response.status_code}")
            print(f"📋 응답 내용: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 응답 시간 초과 (120초)")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_file_loading():
    """파일 로딩 테스트"""
    print("\n" + "=" * 60)
    print("📁 파일 로딩 테스트")
    print("=" * 60)
    
    file_path = "csv/excel/정산요약.xlsx"
    
    try:
        df = pd.read_excel(file_path)
        print(f"✅ 파일 로드 성공: {file_path}")
        print(f"📊 데이터 크기: {len(df)}행 × {len(df.columns)}열")
        print(f"📋 컬럼: {list(df.columns)[:5]}...")
        print(f"💾 메모리: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        # 데이터 미리보기 생성 테스트
        preview = df.head(5).to_dict()
        types = {col: str(df[col].dtype) for col in df.columns}
        
        preview_json = json.dumps(preview, ensure_ascii=False, default=str)
        types_json = json.dumps(types, ensure_ascii=False)
        
        print(f"\n📋 미리보기 JSON 크기: {len(preview_json):,} 문자")
        print(f"📋 타입 JSON 크기: {len(types_json):,} 문자")
        
        return True
    except Exception as e:
        print(f"❌ 파일 로드 실패: {e}")
        return False

def check_environment():
    """환경 확인"""
    print("\n" + "=" * 60)
    print("🔧 환경 확인")
    print("=" * 60)
    
    # Python 버전
    import sys
    print(f"🐍 Python 버전: {sys.version.split()[0]}")
    
    # 필수 패키지 버전
    try:
        import streamlit as st_module
        print(f"✅ Streamlit: {st_module.__version__}")
    except:
        print("❌ Streamlit: 설치되지 않음")
    
    try:
        print(f"✅ Pandas: {pd.__version__}")
    except:
        print("❌ Pandas: 설치되지 않음")
    
    try:
        import requests as req_module
        print(f"✅ Requests: {req_module.__version__}")
    except:
        print("❌ Requests: 설치되지 않음")
    
    # .env 파일 확인
    if os.path.exists(".env"):
        print("✅ .env 파일: 존재함")
        with open(".env", "r") as f:
            content = f.read()
            if "OPENAI_API_KEY" in content:
                print("   - OPENAI_API_KEY: 설정됨")
            else:
                print("   - OPENAI_API_KEY: 미설정")
    else:
        print("⚠️ .env 파일: 없음 (Ollama 사용)")

def main():
    """메인 진단 실행"""
    print("\n" + "🔍 " * 20)
    print("AxiosError 400 진단 스크립트")
    print("🔍 " * 20 + "\n")
    
    # 1. 환경 확인
    check_environment()
    
    # 2. Ollama 서버 테스트
    ollama_ok = test_ollama_server()
    
    # 3. 파일 로딩 테스트
    file_ok = test_file_loading()
    
    # 4. Ollama 코드 생성 테스트
    if ollama_ok:
        generation_ok = test_ollama_generation()
    else:
        generation_ok = False
        print("\n⚠️ Ollama 서버가 실행되지 않아 코드 생성 테스트를 건너뜁니다")
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("📊 진단 결과 요약")
    print("=" * 60)
    print(f"Ollama 서버: {'✅ 정상' if ollama_ok else '❌ 오류'}")
    print(f"파일 로딩: {'✅ 정상' if file_ok else '❌ 오류'}")
    print(f"코드 생성: {'✅ 정상' if generation_ok else '❌ 오류'}")
    
    print("\n💡 다음 단계:")
    if not ollama_ok:
        print("  1. 터미널에서 'ollama serve' 실행")
        print("  2. 다시 진단 스크립트 실행")
    elif not generation_ok:
        print("  1. gpt-oss:latest 모델이 <result> 태그를 제대로 생성하는지 확인")
        print("  2. 다른 모델 시도 (qwen2.5:3b 추천)")
        print("  3. 'ollama pull qwen2.5:3b' 실행")
    else:
        print("  1. Streamlit 앱 실행: streamlit run app.py")
        print("  2. 파일 업로드 후 질문")
        print("  3. app.log 파일 확인")
        print("  4. 여전히 AxiosError 400 발생하면 app.log 내용 공유")
    
    print("=" * 60)
    print("\n📝 로그 파일 위치: app.log")
    print("📝 실시간 로그 확인: tail -f app.log")
    print()

if __name__ == "__main__":
    main()

