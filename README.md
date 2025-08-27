# CSV 데이터 분석 프로그램

통신사 가입자 정보 및 요금제 데이터를 분석하는 Python 프로그램입니다.

## 프로젝트 개요

이 프로그램은 CSV 파일에 저장된 통신사 데이터를 pandas를 사용하여 로드하고 분석합니다.

### 데이터 파일 정보

- **M-2 가입자 정보**: 기존 가입자의 요금제 정보
- **M-1 신규 가입자 정보**: 신규 가입자의 요금제 정보  
- **요금제 정보**: 정책 관련 지원금 등 요금제 상세 정보

## 기능

- CSV 파일 자동 로드
- 컬럼 정보 출력
- 샘플 데이터 10개 조회
- 데이터 기본 통계 정보 제공
- **분석 결과를 database.md 파일로 자동 저장**

## 설치 요구사항

### 가상환경 설정 (권장)
```bash
# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 개별 설치
```bash
pip install pandas jupyter matplotlib seaborn plotly
```

## 사용법

### 1. 콘솔 프로그램 실행
```bash
python csv_analyzer.py
```

### 2. Jupyter Notebook 실행
```bash
# Jupyter Notebook 서버 시작
jupyter notebook

# 브라우저에서 csv_analysis.ipynb 파일 열기
```

### 3. Jupyter Lab 실행 (선택사항)
```bash
# Jupyter Lab 설치 및 실행
pip install jupyterlab
jupyter lab
```

## 파일 구조

```
├── README.md
├── csv_analyzer.py          # 콘솔 분석 프로그램
├── csv_analysis.ipynb       # Jupyter Notebook 분석 파일
├── requirements.txt         # 필요한 패키지 목록
├── database.md             # 분석 결과 저장 파일
├── venv/                   # 가상환경 (생성 후)
└── csv/
    ├── ENTR_BY_INS.csv     # M-2 가입자 정보
    ├── ENTR_INT_INS.csv    # M-1 신규 가입자 정보
    └── MVNO_PRD_PLC.csv    # 요금제 정보
```

## 출력 정보

### 콘솔 출력
1. **파일 정보**: 로드된 CSV 파일명과 크기
2. **컬럼 정보**: 전체 컬럼명과 데이터 타입
3. **샘플 데이터**: 상위 10개 행 데이터
4. **기본 통계**: 데이터 요약 통계

### database.md 파일 저장
- **전체 요약**: 모든 파일의 통합 정보
- **파일별 상세 분석**: 각 CSV 파일의 완전한 분석 결과
- **마크다운 형식**: 읽기 쉬운 구조화된 문서
- **분석 일시**: 언제 분석했는지 기록

## 주의사항

- CSV 파일은 `csv/` 폴더에 위치해야 합니다
- 한글 인코딩 문제가 있을 경우 `encoding='utf-8'` 또는 `encoding='cp949'`를 사용합니다

## Jupyter Notebook 기능

### 📊 인터랙티브 분석
- **시각화**: matplotlib, seaborn, plotly를 활용한 다양한 차트
- **실시간 분석**: 코드 수정 후 즉시 결과 확인
- **데이터 탐색**: 단계별로 데이터를 탐색하고 분석

### 🎯 주요 분석 내용
1. **데이터 로드 및 기본 정보**
2. **M-2 가입자 정보 분석** (수납금액, 요금제별 분포)
3. **M-1 신규 가입자 분석** (개통유형, 요금제별 신규 가입)
4. **요금제 정보 분석** (기본료, 정책 정보)
5. **데이터 간 관계 분석**
6. **인터랙티브 시각화** (Plotly 차트)
7. **종합 인사이트 도출**

### 💡 Jupyter Notebook 장점
- **단계별 실행**: 셀 단위로 코드 실행 가능
- **시각화 최적화**: 차트가 노트북 내에서 바로 표시
- **문서화**: 마크다운과 코드를 함께 작성
- **공유 용이**: HTML, PDF로 내보내기 가능

## 빠른 시작 가이드

```bash
# 1. 가상환경 설정
python3 -m venv venv
source venv/bin/activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. Jupyter Notebook 실행
jupyter notebook

# 4. 브라우저에서 csv_analysis.ipynb 열기
```