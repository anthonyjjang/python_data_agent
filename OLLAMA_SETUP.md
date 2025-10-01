# 🦙 Ollama 로컬 LLM 설정 가이드

OpenAI API 할당량 문제로 인해 로컬 LLM인 Ollama를 사용할 수 있습니다.

## 📦 Ollama 설치

### macOS
```bash
# Homebrew로 설치
brew install ollama

# 또는 공식 설치 프로그램 다운로드
# https://ollama.ai/download
```

### 다른 OS
- [공식 웹사이트](https://ollama.ai/download)에서 설치 프로그램 다운로드

## 🚀 Ollama 서버 시작

```bash
# Ollama 서버 시작
ollama serve
```

## 📥 모델 다운로드

새 터미널에서 실행:

```bash
# 한국어 지원이 좋은 경량 모델 (권장)
ollama pull qwen2.5:3b

# 또는 더 큰 모델 (성능 좋음, 용량 큼)
ollama pull qwen2.5:7b

# 영어 모델 (빠름)
ollama pull llama3.2:3b
```

## ✅ 설치 확인

```bash
# 설치된 모델 확인
ollama list

# 모델 테스트
ollama run qwen2.5:3b "안녕하세요"
```

## 🔧 앱에서 사용

1. **Ollama 서버 실행 상태 확인**
   ```bash
   ollama serve
   ```

2. **Excel Agent 실행**
   ```bash
   cd python_excel_agent
   uv run streamlit run app.py
   ```

3. **자동 전환**
   - OpenAI API 할당량 초과 시 자동으로 Ollama로 전환됩니다
   - Streamlit에서 경고 메시지가 표시됩니다

## 📊 모델 비교

| 모델 | 크기 | 속도 | 한국어 지원 | 메모리 사용량 |
|------|------|------|-------------|---------------|
| qwen2.5:3b | ~2GB | 빠름 | 우수 | ~4GB RAM |
| qwen2.5:7b | ~4GB | 보통 | 매우 우수 | ~8GB RAM |
| llama3.2:3b | ~2GB | 빠름 | 보통 | ~4GB RAM |

## 🚨 문제 해결

### "연결할 수 없습니다" 오류
```bash
# Ollama 서버가 실행 중인지 확인
ps aux | grep ollama

# 서버 재시작
ollama serve
```

### 모델 다운로드 실패
```bash
# 네트워크 확인 후 재시도
ollama pull qwen2.5:3b
```

### 메모리 부족
- 더 작은 모델 사용: `qwen2.5:1.5b`
- 다른 애플리케이션 종료

## 💡 팁

- **첫 실행**: 모델 로딩에 시간이 걸릴 수 있습니다
- **성능**: GPU가 있으면 자동으로 활용됩니다
- **업데이트**: `ollama pull <model>` 명령으로 모델 업데이트 가능

이제 OpenAI API 할당량 걱정 없이 로컬에서 Excel 데이터 분석을 할 수 있습니다! 🎉