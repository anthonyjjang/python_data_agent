# 🔧 문제 해결 가이드 (Troubleshooting Guide)

## AxiosError: Request failed with status code 400

### 증상
Excel 파일 업로드 후 질문을 입력하면 `AxiosError: Request failed with status code 400` 오류 발생

### 해결 방법

#### 1️⃣ 로그 파일 확인
```bash
# 로그 파일 위치
/Users/loveauden/Development/vibe_pandas_project/app.log

# 로그 실시간 확인
tail -f app.log
```

#### 2️⃣ Ollama 서버 확인
```bash
# Ollama 서버가 실행 중인지 확인
curl http://localhost:11434/api/tags

# 서버가 실행되지 않았다면 시작
ollama serve
```

#### 3️⃣ 설치된 모델 확인
```bash
# 설치된 모델 목록 확인
ollama list

# 추천 모델 설치
ollama pull qwen2.5:3b      # 가장 추천 (빠르고 정확)
ollama pull llama3.2:3b     # 대안 1
ollama pull gpt-oss:latest  # 대안 2
```

#### 4️⃣ 모델 테스트
```bash
# 간단한 테스트
ollama run qwen2.5:3b "안녕하세요"

# 응답이 정상적으로 나오면 OK
```

---

## 코드 추출 실패 (Code Extraction Failed)

### 증상
- "코드 추출 실패 - 응답에서 유효한 Python 코드를 찾을 수 없습니다"
- LLM이 코드 대신 설명만 반환

### 해결 방법

#### 1️⃣ 로그에서 LLM 응답 확인
`app.log`에서 다음 섹션 찾기:
```
📋 LLM 응답 전체:
   1| ...
   2| ...
```

#### 2️⃣ 프롬프트 개선
LLM이 설명만 하고 코드를 생성하지 않는 경우, 더 명확한 질문 사용:

**나쁜 예:**
- "데이터 분석해줘"
- "이 데이터 어때?"

**좋은 예:**
- "202503 정산월의 확정 금액을 보여줘"
- "MNP 유형별 개통 건수를 집계해줘"
- "인스코리아센터의 총 개통 건수는?"

#### 3️⃣ 다른 모델 시도
일부 모델이 코드 생성을 더 잘 수행합니다:

**코드 생성에 좋은 모델 (우선순위 순):**
1. `qwen2.5:3b` ⭐ 최고 추천
2. `qwen2.5:7b` (더 크고 정확하지만 느림)
3. `llama3.2:3b`
4. `deepseek-coder:6.7b` (코딩 특화)

```bash
# 다른 모델 설치 및 시도
ollama pull qwen2.5:7b
```

---

## 코드 실행 오류 (Code Execution Error)

### 증상
- 코드는 생성되었으나 실행 시 오류 발생
- "코드 실행 실패" 메시지

### 로그 확인 포인트

#### 1️⃣ 실행된 코드 확인
```
📝 실행할 코드:
   1| ...
   2| ...
```

#### 2️⃣ 오류 메시지 확인
```
❌ 코드 실행 실패 (시도 1/3)
📋 오류 유형: KeyError
📋 오류 메시지: 'column_name'
```

### 일반적인 오류와 해결

#### KeyError: 'column_name'
**원인**: 존재하지 않는 컬럼명 사용

**해결**:
1. 데이터프레임의 실제 컬럼명 확인
2. 정확한 컬럼명으로 질문 재시도

#### ValueError: could not convert string to float
**원인**: 데이터 타입 불일치

**해결**:
- 자동으로 3번까지 재시도하며 LLM이 코드를 수정함
- 재시도 후에도 실패하면 로그 확인 후 질문 재작성

---

## Ollama 서버 연결 실패

### 증상
```
❌ Ollama 서버 연결 실패
💡 해결 방법: 터미널에서 'ollama serve' 실행
```

### 해결 단계

#### 1️⃣ Ollama 설치 확인
```bash
# Ollama가 설치되어 있는지 확인
which ollama

# 설치되지 않았다면 설치
brew install ollama
```

#### 2️⃣ 서버 시작
```bash
# 새 터미널 창에서 실행 (백그라운드 실행)
ollama serve

# 또는 백그라운드로 직접 실행
nohup ollama serve > /dev/null 2>&1 &
```

#### 3️⃣ 서버 상태 확인
```bash
# 서버가 응답하는지 확인
curl http://localhost:11434/api/tags

# 정상이면 {"models": [...]} 응답
```

---

## Excel 파일 로드 실패

### 증상
- "파일을 읽을 수 없습니다"
- 인코딩 오류

### 해결 방법

#### 1️⃣ 파일 형식 확인
- Excel 파일: `.xlsx`, `.xls`
- CSV 파일: `.csv`

#### 2️⃣ 파일 손상 확인
Excel에서 파일을 열어 확인:
- 데이터가 정상적으로 보이는가?
- 수식 오류는 없는가?
- 병합된 셀이나 특수 포맷이 많지 않은가?

#### 3️⃣ CSV로 변환 시도
Excel 파일 로드 실패 시 CSV로 변환:
1. Excel에서 "다른 이름으로 저장"
2. 형식: "CSV UTF-8 (쉼표로 분리) (*.csv)"
3. 저장 후 CSV 파일 업로드

#### 4️⃣ 로그 확인
```
📁 파일 업로드 시작
📄 파일명: example.xlsx
📦 파일 크기: 1,234,567 bytes
📝 파일 타입: xlsx
```

---

## 로그 분석 팁

### 로그 파일 위치
```bash
/Users/loveauden/Development/vibe_pandas_project/app.log
```

### 주요 로그 섹션

#### 1️⃣ 앱 초기화
```
🚀 로깅 시스템 초기화 완료
🔑 OpenAI API 키 확인
🦙 OpenAI API 키 없음 - Ollama로 자동 전환
```

#### 2️⃣ 파일 업로드
```
📁 파일 업로드 시작
✅ 성공 또는 ❌ 실패
```

#### 3️⃣ Ollama 호출
```
🦙 Ollama 함수 호출 시작
🔍 1단계: Ollama 서버 연결 확인 중...
🔍 2단계: 사용 가능한 모델 확인 중...
🔍 3단계: 모델 선택 중...
🔍 4단계: Ollama API 호출 준비...
```

#### 4️⃣ 코드 생성 및 실행
```
🔍 코드 추출 단계 시작
⚙️ 코드 실행 단계 시작
✅ 성공 또는 ❌ 실패
```

### 로그 필터링
```bash
# 오류만 보기
grep "❌" app.log

# 특정 시간대 로그 보기
grep "2025-11-04 13:" app.log

# 마지막 100줄
tail -100 app.log

# 실시간 로그 보기
tail -f app.log
```

---

## 성능 최적화

### 느린 응답 속도

#### 원인
1. 모델이 너무 큼
2. 데이터가 너무 큼
3. 복잡한 질문

#### 해결

**1. 작은 모델 사용**
```bash
# 빠른 모델 (추천)
ollama pull qwen2.5:1.5b  # 가장 빠름
ollama pull qwen2.5:3b    # 속도와 정확도 균형
```

**2. 데이터 필터링**
- 전체 데이터 대신 필요한 열/행만 업로드
- Excel에서 미리 필터링 후 CSV로 저장

**3. 질문 단순화**
- 복잡한 다단계 분석 → 단계별로 나눠 질문
- "모든 통계 분석해줘" → "202503 정산월 합계는?"

---

## 디버그 모드 실행

### 자세한 로그 보기
```bash
cd /Users/loveauden/Development/vibe_pandas_project
source venv/bin/activate
streamlit run app.py --logger.level=debug
```

### Python 테스트 스크립트
```bash
# Excel 로드 및 API 테스트
python test_excel_upload.py

# 로그 확인
cat app.log
```

---

## 추가 도움말

### 공식 문서
- **Ollama**: https://ollama.ai/
- **Streamlit**: https://docs.streamlit.io/
- **Pandas**: https://pandas.pydata.org/docs/

### 자주 하는 질문

**Q: OpenAI API 키 없이 사용 가능한가요?**  
A: 네! Ollama를 사용하면 완전히 무료로 로컬에서 실행 가능합니다.

**Q: 어떤 모델이 가장 좋나요?**  
A: `qwen2.5:3b`를 추천합니다. 속도와 정확도의 균형이 좋습니다.

**Q: 여러 Excel 파일을 동시에 분석할 수 있나요?**  
A: 현재는 한 번에 하나의 파일만 가능합니다. 파일을 합쳐서 업로드하세요.

**Q: 데이터가 너무 크면 어떻게 하나요?**  
A: Excel에서 필요한 부분만 필터링 후 CSV로 저장하여 업로드하세요.

---

## 여전히 문제가 해결되지 않는다면

1. **로그 파일 전체 확인**
   ```bash
   cat app.log
   ```

2. **테스트 스크립트 실행**
   ```bash
   python test_excel_upload.py
   ```

3. **환경 재설정**
   ```bash
   # 가상환경 삭제 및 재생성
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Ollama 재설치**
   ```bash
   brew uninstall ollama
   brew install ollama
   ollama pull qwen2.5:3b
   ollama serve
   ```

이 문서에서 답을 찾지 못했다면 `app.log` 파일의 내용과 함께 개발자에게 문의하세요.

