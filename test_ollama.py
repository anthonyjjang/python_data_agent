#!/usr/bin/env python3
"""
Ollama 설치 및 연결 테스트 스크립트
"""

import requests
import json
import subprocess
import sys

def check_ollama_installed():
    """Ollama가 설치되어 있는지 확인"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama 설치됨: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama가 설치되지 않았습니다.")
            return False
    except FileNotFoundError:
        print("❌ Ollama가 설치되지 않았습니다.")
        return False

def check_ollama_server():
    """Ollama 서버가 실행 중인지 확인"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama 서버 실행 중")
            return True
        else:
            print(f"❌ Ollama 서버 응답 오류: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama 서버에 연결할 수 없습니다.")
        return False
    except Exception as e:
        print(f"❌ Ollama 서버 확인 실패: {e}")
        return False

def get_installed_models():
    """설치된 모델 목록 조회"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print("📦 설치된 모델:")
                for model in models:
                    name = model.get("name", "Unknown")
                    size = model.get("size", 0)
                    size_gb = size / (1024**3) if size > 0 else 0
                    print(f"   - {name} ({size_gb:.1f}GB)")
                return [model["name"] for model in models]
            else:
                print("📦 설치된 모델이 없습니다.")
                return []
        else:
            print("❌ 모델 목록 조회 실패")
            return []
    except Exception as e:
        print(f"❌ 모델 목록 조회 오류: {e}")
        return []

def test_model(model_name):
    """특정 모델 테스트"""
    print(f"\n🧪 모델 테스트: {model_name}")
    
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "prompt": "안녕하세요. 간단한 테스트입니다. '테스트 성공'이라고 한국어로 답해주세요.",
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            print(f"✅ {model_name} 테스트 성공!")
            print(f"📝 응답: {response_text[:100]}...")
            return True
        else:
            print(f"❌ {model_name} 테스트 실패: HTTP {response.status_code}")
            print(f"   오류: {response.text}")
            return False
    except Exception as e:
        print(f"❌ {model_name} 테스트 오류: {e}")
        return False

def install_recommended_model():
    """권장 모델 설치"""
    print("\n📥 권장 모델 설치 중...")
    recommended_model = "qwen2.5:3b"
    
    try:
        print(f"모델 다운로드 시작: {recommended_model}")
        print("⏳ 다운로드에 시간이 걸릴 수 있습니다...")
        
        result = subprocess.run(['ollama', 'pull', recommended_model], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {recommended_model} 설치 완료!")
            return True
        else:
            print(f"❌ 모델 설치 실패: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 모델 다운로드 시간 초과")
        return False
    except Exception as e:
        print(f"❌ 모델 설치 오류: {e}")
        return False

def main():
    print("🦙 Ollama 설치 및 연결 테스트")
    print("=" * 40)
    
    # 1. Ollama 설치 확인
    if not check_ollama_installed():
        print("\n💡 Ollama 설치 방법:")
        print("   macOS: brew install ollama")
        print("   기타: https://ollama.ai/download")
        return
    
    # 2. 서버 실행 확인
    if not check_ollama_server():
        print("\n💡 Ollama 서버 시작 방법:")
        print("   터미널에서 실행: ollama serve")
        return
    
    # 3. 설치된 모델 확인
    models = get_installed_models()
    
    # 4. 모델이 없으면 설치 제안
    if not models:
        print("\n💡 권장 모델을 설치하시겠습니까?")
        response = input("qwen2.5:3b 모델을 설치하려면 'y'를 입력하세요: ")
        if response.lower() in ['y', 'yes', '예']:
            if install_recommended_model():
                models = get_installed_models()
    
    # 5. 모델 테스트
    if models:
        print(f"\n🧪 첫 번째 모델 테스트: {models[0]}")
        if test_model(models[0]):
            print("\n🎉 Ollama 설정이 완료되었습니다!")
            print("이제 Excel Agent를 실행할 수 있습니다:")
            print("   uv run streamlit run app.py")
        else:
            print("\n❌ 모델 테스트에 실패했습니다.")
    else:
        print("\n❌ 사용 가능한 모델이 없습니다.")
        print("다음 명령으로 모델을 설치하세요:")
        print("   ollama pull qwen2.5:3b")

if __name__ == "__main__":
    main()