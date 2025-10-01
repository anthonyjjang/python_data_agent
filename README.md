# 통합 데이터 분석 AI Agent

Streamlit 기반의 대화형 데이터 분석 도구와 CSV 데이터 분석 기능을 통합한 Python 프로그램입니다.

## 🚀 주요 기능

### 1. 대화형 데이터 분석 (Streamlit)
- **자연어 질의**: 데이터에 대해 자연어로 질문하고 AI가 답변
- **다중 LLM 지원**: OpenAI GPT와 OLLAMA 로컬 모델 지원
- **실시간 분석**: 업로드한 파일을 즉시 분석하고 시각화
- **코드 생성**: AI가 자동으로 분석 코드를 생성하고 실행

### 2. CSV 데이터 분석 (Jupyter Notebook)
- **통신사 데이터 분석**: M-2 가입자, M-1 신규 가입자, 요금제 정보 분석
- **자동 보고서 생성**: 분석 결과를 database.md 파일로 자동 저장
- **인터랙티브 시각화**: matplotlib, seaborn, plotly를 활용한 다양한 차트
- **컬럼 매핑**: 데이터 컬럼 정보를 체계적으로 정리

## 📁 프로젝트 구조

```
python_excel_agent/
├── app.py                    # Streamlit 메인 애플리케이션
├── csv_analyzer.py          # CSV 분석 프로그램
├── csv_analysis.ipynb       # Jupyter Notebook 분석 파일
├── column_mapper.py         # 컬럼 매핑 도구
├── requirements.txt         # 필요한 패키지 목록
├── pyproject.toml          # 프로젝트 설정
├── README.md               # 프로젝트 문서
├── CLAUDE.md               # Claude 사용 가이드
├── OLLAMA_SETUP.md         # OLLAMA 설정 가이드
└── doc/                    # 추가 문서
    └── guide.md
```

## 🛠️ 설치 방법

### 1. 필수 패키지 설치

```bash
# uv 사용 (권장)
uv add openai pandas streamlit python-dotenv openpyxl matplotlib seaborn plotly jupyter

# 또는 pip 사용
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 OpenAI API 키를 입력:

```env
OPENAI_API_KEY=여기에_발급받은_키_입력
```

### 3. OLLAMA 설정 (선택사항)

로컬 AI 모델을 사용하려면 OLLAMA를 설치하고 모델을 다운로드:

```bash
# OLLAMA 설치 후
ollama pull qwen2.5:3b
ollama serve
```

## 🚀 사용법

### 1. Streamlit 앱 실행 (대화형 분석)

```bash
uv run streamlit run app.py
```

**주요 기능:**
- 파일 업로드 (Excel, CSV)
- 자연어 질의 응답
- 실시간 데이터 시각화
- AI 코드 생성 및 실행

### 2. Jupyter Notebook 실행 (고급 분석)

```bash
jupyter notebook
# 브라우저에서 csv_analysis.ipynb 파일 열기
```

**주요 기능:**
- 단계별 데이터 분석
- 인터랙티브 시각화
- 상세한 통계 분석
- 보고서 자동 생성

### 3. 콘솔 프로그램 실행 (배치 분석)

```bash
python csv_analyzer.py
```

**주요 기능:**
- CSV 파일 자동 로드
- 기본 통계 정보 제공
- database.md 파일 자동 생성

## 📊 데이터 분석 기능

### Streamlit 앱 기능
- **파일 업로드**: Excel, CSV 파일 지원
- **자연어 질의**: "서울에서 가장 많은 상점이 있는 구는?" 같은 질문
- **AI 코드 생성**: 질문에 맞는 pandas 코드 자동 생성
- **실시간 시각화**: Plotly를 활용한 인터랙티브 차트
- **다중 LLM 지원**: OpenAI와 OLLAMA 모델 선택 가능

### Jupyter Notebook 기능
- **데이터 로드**: 다양한 인코딩 자동 감지
- **통계 분석**: 기본 통계, 결측값 분석
- **시각화**: matplotlib, seaborn, plotly 차트
- **보고서 생성**: 마크다운 형식의 분석 보고서
- **컬럼 매핑**: 데이터 구조 체계적 정리

## 🎯 샘플 데이터

샘플 파일 다운로드 출처:  
https://www.data.go.kr/data/15083033/fileData.do#tab-layer-openapi

## 📈 출력 정보

### Streamlit 앱 출력
- **실시간 답변**: AI가 생성한 자연어 답변
- **생성된 코드**: 실행된 pandas 코드 표시
- **필터링된 데이터**: 분석 결과 데이터프레임
- **시각화**: 인터랙티브 차트

### Jupyter Notebook 출력
- **콘솔 출력**: 파일 정보, 컬럼 정보, 샘플 데이터, 기본 통계
- **database.md**: 전체 요약, 파일별 상세 분석, 마크다운 형식
- **column_info.csv**: 컬럼 정보를 CSV로 저장

## ⚙️ 고급 설정

### OLLAMA 설정
- 로컬 AI 모델 사용으로 비용 절약
- 오프라인 분석 가능
- 다양한 오픈소스 모델 지원

### OpenAI 설정
- 고성능 GPT 모델 사용
- 클라우드 기반 빠른 응답
- API 키 필요

## 🔧 문제 해결

### 인코딩 문제
- CSV 파일: `encoding='utf-8'`, `encoding='cp949'` 자동 시도
- Excel 파일: openpyxl을 통한 자동 처리

### LLM 연결 문제
- OLLAMA: `ollama serve` 명령으로 서버 시작
- OpenAI: API 키 확인 및 할당량 확인

## 📚 추가 문서

- [CLAUDE.md](CLAUDE.md): Claude AI 사용 가이드
- [OLLAMA_SETUP.md](OLLAMA_SETUP.md): OLLAMA 설정 상세 가이드
- [doc/guide.md](doc/guide.md): 추가 사용 가이드

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/새기능`)
3. 변경사항을 커밋합니다 (`git commit -am '새 기능 추가'`)
4. 브랜치에 푸시합니다 (`git push origin feature/새기능`)
5. Pull Request를 생성합니다

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**통합 데이터 분석 AI Agent** - Streamlit과 Jupyter Notebook을 활용한 강력한 데이터 분석 도구