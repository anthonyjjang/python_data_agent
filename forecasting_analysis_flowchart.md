# 📊 Forecasting Analysis 플로우 차트

## 전체 프로세스 개요

```mermaid
flowchart TD
    Start([시작]) --> Init[라이브러리 및 환경 설정]
    Init --> LoadData[데이터 로드]
    LoadData --> DataInfo[데이터 기본 정보 확인]
    DataInfo --> DefineFunc[월별 예상 금액 계산 함수 정의]
    DefineFunc --> MergeBy[ENTR_BY_INS + MVNO_PRD_PLC 병합]
    MergeBy --> MergeInt[ENTR_INT_INS + MVNO_PRD_PLC 병합]
    MergeInt --> CalcBy[ENTR_BY_INS 월별 예상 금액 계산]
    CalcBy --> CalcInt[ENTR_INT_INS 월별 예상 금액 계산]
    CalcInt --> Visualize[시각화]
    Visualize --> SaveResults[결과 저장]
    SaveResults --> End([종료])
    
    style Start fill:#e1f5e1
    style End fill:#ffe1e1
    style Init fill:#e3f2fd
    style LoadData fill:#fff3e0
    style MergeBy fill:#f3e5f5
    style MergeInt fill:#f3e5f5
    style CalcBy fill:#fff9c4
    style CalcInt fill:#fff9c4
    style Visualize fill:#e0f2f1
    style SaveResults fill:#fce4ec
```

---

## 1️⃣ 초기화 단계

```mermaid
flowchart LR
    A[라이브러리 Import] --> B[한글 폰트 설정]
    B --> C{한글 폰트<br/>찾기 성공?}
    C -->|예| D[선택된 폰트 적용]
    C -->|아니오| E[macOS 기본 폰트 시도]
    E --> F{폰트<br/>적용 성공?}
    F -->|예| D
    F -->|아니오| G[DejaVu Sans 사용]
    D --> H[환경 설정 완료]
    G --> H
    
    style A fill:#bbdefb
    style D fill:#c8e6c9
    style G fill:#ffccbc
    style H fill:#c8e6c9
```

### 사용 라이브러리
- `pandas` - 데이터 처리
- `numpy` - 수치 계산
- `matplotlib` - 시각화
- `seaborn` - 통계 시각화
- `datetime`, `dateutil.relativedelta` - 날짜 계산

---

## 2️⃣ 데이터 로드 단계

```mermaid
flowchart TD
    Start[데이터 로드 시작] --> LoadBy[ENTR_BY_INS.csv 로드]
    LoadBy --> CheckBy{로드 성공?}
    CheckBy -->|예| InfoBy[270,192행 × 111열]
    CheckBy -->|아니오| ErrorBy[❌ 에러 메시지 출력]
    
    InfoBy --> LoadInt[ENTR_INT_INS.csv 로드]
    ErrorBy --> LoadInt
    
    LoadInt --> CheckInt{로드 성공?}
    CheckInt -->|예| InfoInt[38,161행 × 106열]
    CheckInt -->|아니오| ErrorInt[❌ 에러 메시지 출력]
    
    InfoInt --> LoadPlan[MVNO_PRD_PLC.csv 로드]
    ErrorInt --> LoadPlan
    
    LoadPlan --> CheckPlan{로드 성공?}
    CheckPlan -->|예| InfoPlan[138행 × 9열]
    CheckPlan -->|아니오| ErrorPlan[❌ 에러 메시지 출력]
    
    InfoPlan --> Complete[✅ 데이터 로드 완료]
    ErrorPlan --> Complete
    
    style Start fill:#e3f2fd
    style Complete fill:#c8e6c9
    style ErrorBy fill:#ffcdd2
    style ErrorInt fill:#ffcdd2
    style ErrorPlan fill:#ffcdd2
```

### 데이터 파일 정보
| 파일명 | 인코딩 | 행 수 | 열 수 | 설명 |
|--------|--------|-------|-------|------|
| ENTR_BY_INS.csv | cp949 | 270,192 | 111 | M-2 정산내역 |
| ENTR_INT_INS.csv | utf-8 | 38,161 | 106 | M-1 신규 가입자 |
| MVNO_PRD_PLC.csv | utf-8 | 138 | 9 | 요금제 정보 |

---

## 3️⃣ 데이터 병합 단계

### ENTR_BY_INS 병합 프로세스

```mermaid
flowchart TD
    Start[병합 시작] --> Check1{MVNO상품코드 존재?}
    Check1 -->|예| Check2{요금제코드 존재?}
    Check1 -->|아니오| Error[❌ 병합 불가]
    Check2 -->|예| Merge[LEFT JOIN 수행]
    Check2 -->|아니오| Error
    
    Merge --> Result[270,192행 × 120열]
    Result --> Verify[매핑 결과 확인]
    Verify --> Stats[매핑 성공: 100%<br/>매핑 실패: 0%]
    Stats --> Success[✅ 병합 완료]
    
    Error --> End[종료]
    Success --> End
    
    style Start fill:#e3f2fd
    style Merge fill:#fff9c4
    style Success fill:#c8e6c9
    style Error fill:#ffcdd2
```

### ENTR_INT_INS 병합 프로세스

```mermaid
flowchart TD
    Start[병합 시작] --> Check1{개통요금제코드 존재?}
    Check1 -->|예| Check2{요금제코드 존재?}
    Check1 -->|아니오| Error[❌ 병합 불가]
    Check2 -->|예| Merge[LEFT JOIN 수행]
    Check2 -->|아니오| Error
    
    Merge --> Result[38,161행 × 115열]
    Result --> Verify[매핑 결과 확인]
    Verify --> Stats[매핑 성공: 99.5%<br/>매핑 실패: 0.5%]
    Stats --> Success[✅ 병합 완료]
    
    Error --> End[종료]
    Success --> End
    
    style Start fill:#e3f2fd
    style Merge fill:#fff9c4
    style Success fill:#c8e6c9
    style Error fill:#ffcdd2
```

### 병합 키 매핑

```mermaid
flowchart LR
    A[ENTR_BY_INS<br/>MVNO상품코드] -.->|매칭| C[MVNO_PRD_PLC<br/>요금제코드]
    B[ENTR_INT_INS<br/>개통요금제코드] -.->|매칭| C
    
    C --> D[요금제명]
    C --> E[기본료]
    C --> F[평생할인]
    C --> G[기간할인]
    C --> H[이벤트가]
    C --> I[정책금]
    C --> J[정책반영시작일]
    C --> K[정책반영종료일]
    
    style A fill:#bbdefb
    style B fill:#bbdefb
    style C fill:#fff9c4
    style D fill:#c8e6c9
    style E fill:#c8e6c9
    style F fill:#c8e6c9
    style G fill:#c8e6c9
    style H fill:#c8e6c9
    style I fill:#c8e6c9
    style J fill:#f8bbd0
    style K fill:#f8bbd0
```

---

## 4️⃣ 월별 예상 금액 계산 함수

### 함수 로직 플로우

```mermaid
flowchart TD
    Start([calculate_monthly_forecast]) --> Input[입력: row, months_ahead=12]
    Input --> GetBase{정책금 존재?}
    GetBase -->|예| UsePolicy[base_fee = 정책금]
    GetBase -->|아니오| UseBasic[base_fee = 기본료]
    
    UsePolicy --> GetDiscount[할인 정보 추출]
    UseBasic --> GetDiscount
    
    GetDiscount --> Extract[평생할인, 기간할인,<br/>이벤트가 추출]
    Extract --> GetPolicy[정책 반영 기간 확인]
    GetPolicy --> GetJoin[가입일 확인]
    
    GetJoin --> CheckJoin{가입일 유효?}
    CheckJoin -->|아니오| ReturnZero[0으로 채운<br/>12개월 리스트 반환]
    CheckJoin -->|예| LoopStart[월별 계산 시작]
    
    LoopStart --> ForMonth[for month in 0~11]
    ForMonth --> CalcDate[target_date = 가입일 + month개월]
    CalcDate --> CheckPolicyPeriod{정책 기간 내?}
    
    CheckPolicyPeriod -->|예| ApplyAll[기본료에서<br/>모든 할인 적용]
    CheckPolicyPeriod -->|아니오| ApplyLifetime[기본료에서<br/>평생할인만 적용]
    
    ApplyAll --> CalcAmount[월별 금액 = max0, base_fee - 할인]
    ApplyLifetime --> CalcAmount
    
    CalcAmount --> AddToList[monthly_forecasts에 추가]
    AddToList --> MoreMonths{더 계산할<br/>개월 있음?}
    MoreMonths -->|예| ForMonth
    MoreMonths -->|아니오| Return[monthly_forecasts 반환]
    
    ReturnZero --> End([종료])
    Return --> End
    
    style Start fill:#e1bee7
    style GetBase fill:#fff9c4
    style CheckJoin fill:#ffccbc
    style CheckPolicyPeriod fill:#ffccbc
    style ApplyAll fill:#c8e6c9
    style ApplyLifetime fill:#c8e6c9
    style Return fill:#c8e6c9
    style End fill:#e1bee7
```

### 할인 적용 로직 상세

```mermaid
flowchart TD
    Start[월별 금액 = 기본료] --> Step1[1. 평생할인 확인]
    Step1 --> Check1{평생할인 > 0?}
    Check1 -->|예| Apply1[월별 금액 -= 평생할인]
    Check1 -->|아니오| Step2
    Apply1 --> Step2[2. 기간할인 확인]
    
    Step2 --> Check2{기간할인 > 0<br/>AND 정책기간?}
    Check2 -->|예| Apply2[월별 금액 -= 기간할인]
    Check2 -->|아니오| Step3
    Apply2 --> Step3[3. 이벤트가 확인]
    
    Step3 --> Check3{이벤트가 > 0<br/>AND 정책기간?}
    Check3 -->|예| Apply3[월별 금액 -= 이벤트가]
    Check3 -->|아니오| Final
    Apply3 --> Final[4. 최종 금액 = max0, 월별 금액]
    
    Final --> Result[월별 예상 금액 확정]
    
    style Start fill:#e3f2fd
    style Apply1 fill:#c8e6c9
    style Apply2 fill:#c8e6c9
    style Apply3 fill:#c8e6c9
    style Result fill:#fff9c4
```

---

## 5️⃣ 예상 금액 계산 실행

### ENTR_BY_INS 계산 프로세스

```mermaid
flowchart TD
    Start[계산 시작] --> CheckData{병합 데이터 존재?}
    CheckData -->|아니오| Error[❌ 데이터 없음]
    CheckData -->|예| Filter[매핑된 데이터만 필터링]
    
    Filter --> Count[270,192건 확인]
    Count --> Setup[12개월 컬럼 생성<br/>M1, M2, ..., M12]
    Setup --> Loop[각 고객별 반복]
    
    Loop --> CalcRow[calculate_monthly_forecast 호출]
    CalcRow --> AddCol[예상 금액을 컬럼에 추가]
    AddCol --> MoreRows{더 처리할<br/>고객 있음?}
    MoreRows -->|예| Loop
    MoreRows -->|아니오| Stats[통계 계산]
    
    Stats --> Display[샘플 데이터 출력]
    Display --> ShowStats[월별 총액 및 평균 출력]
    ShowStats --> Success[✅ 계산 완료]
    
    Error --> End([종료])
    Success --> End
    
    style Start fill:#e3f2fd
    style Loop fill:#fff9c4
    style CalcRow fill:#ffe0b2
    style Success fill:#c8e6c9
    style Error fill:#ffcdd2
```

### ENTR_INT_INS 계산 프로세스

```mermaid
flowchart TD
    Start[계산 시작] --> CheckData{병합 데이터 존재?}
    CheckData -->|아니오| Error[❌ 데이터 없음]
    CheckData -->|예| Filter[매핑된 데이터만 필터링]
    
    Filter --> Count[37,959건 확인]
    Count --> Setup[12개월 컬럼 생성<br/>M1, M2, ..., M12]
    Setup --> Loop[각 고객별 반복]
    
    Loop --> CalcRow[calculate_monthly_forecast 호출]
    CalcRow --> AddCol[예상 금액을 컬럼에 추가]
    AddCol --> MoreRows{더 처리할<br/>고객 있음?}
    MoreRows -->|예| Loop
    MoreRows -->|아니오| Stats[통계 계산]
    
    Stats --> Display[샘플 데이터 출력]
    Display --> ShowStats[월별 총액 및 평균 출력]
    ShowStats --> Success[✅ 계산 완료]
    
    Error --> End([종료])
    Success --> End
    
    style Start fill:#e3f2fd
    style Loop fill:#fff9c4
    style CalcRow fill:#ffe0b2
    style Success fill:#c8e6c9
    style Error fill:#ffcdd2
```

---

## 6️⃣ 시각화 프로세스

```mermaid
flowchart TD
    Start[시각화 시작] --> CheckData{예상 금액<br/>데이터 존재?}
    CheckData -->|아니오| Error[❌ 데이터 없음]
    CheckData -->|예| Setup[Figure 생성<br/>15x10 크기, 2x2 서브플롯]
    
    Setup --> Plot1[1. 월별 총 예상 금액 비교<br/>라인 차트]
    Plot1 --> Plot2[2. 월별 평균 예상 금액 비교<br/>라인 차트]
    Plot2 --> Plot3[3. 요금제별 총 예상 금액<br/>ENTR_BY_INS 바 차트]
    Plot3 --> Plot4[4. 요금제별 총 예상 금액<br/>ENTR_INT_INS 바 차트]
    
    Plot4 --> Display[plt.show로 표시]
    Display --> Success[✅ 시각화 완료]
    
    Error --> End([종료])
    Success --> End
    
    style Start fill:#e3f2fd
    style Plot1 fill:#bbdefb
    style Plot2 fill:#bbdefb
    style Plot3 fill:#c8e6c9
    style Plot4 fill:#ffccbc
    style Success fill:#c8e6c9
    style Error fill:#ffcdd2
```

### 시각화 구성

```mermaid
graph TB
    subgraph "시각화 대시보드 (15x10)"
        A[📈 월별 총 예상 금액 비교]
        B[📊 월별 평균 예상 금액 비교]
        C[📊 상위 10개 요금제<br/>ENTR_BY_INS]
        D[📊 상위 10개 요금제<br/>ENTR_INT_INS]
    end
    
    A -.-> E[M1~M12 라인 그래프]
    B -.-> F[M1~M12 라인 그래프]
    C -.-> G[가로 막대 차트]
    D -.-> H[가로 막대 차트]
    
    style A fill:#e3f2fd
    style B fill:#e3f2fd
    style C fill:#c8e6c9
    style D fill:#ffccbc
```

---

## 7️⃣ 결과 저장 프로세스

```mermaid
flowchart TD
    Start[저장 시작] --> TrySave{저장 시도}
    
    TrySave --> SaveBy[ENTR_BY_INS_FORECASTING.csv 저장]
    SaveBy --> CheckBy{저장 성공?}
    CheckBy -->|예| InfoBy[✅ 파일 정보 출력<br/>크기, 행수, 열수]
    CheckBy -->|아니오| ErrorBy[⚠️ 스킵]
    
    InfoBy --> SaveInt[ENTR_INT_INS_FORECASTING.csv 저장]
    ErrorBy --> SaveInt
    
    SaveInt --> CheckInt{저장 성공?}
    CheckInt -->|예| InfoInt[✅ 파일 정보 출력<br/>크기, 행수, 열수]
    CheckInt -->|아니오| ErrorInt[⚠️ 스킵]
    
    InfoInt --> CreateSummary[요약 통계 생성]
    ErrorInt --> CreateSummary
    
    CreateSummary --> SummaryData[구분, 총고객수,<br/>12개월 총/평균 예상금액]
    SummaryData --> SaveSummary[FORECASTING_SUMMARY.csv 저장]
    SaveSummary --> CheckSummary{저장 성공?}
    CheckSummary -->|예| PrintSummary[✅ 요약 테이블 출력]
    CheckSummary -->|아니오| ErrorSummary[⚠️ 스킵]
    
    PrintSummary --> ListFiles[저장된 파일 목록 출력]
    ErrorSummary --> ListFiles
    
    ListFiles --> Complete[🎉 분석 완료!]
    Complete --> End([종료])
    
    TrySave -.->|예외 발생| Catch[❌ 에러 메시지 출력]
    Catch --> End
    
    style Start fill:#e3f2fd
    style SaveBy fill:#fff9c4
    style SaveInt fill:#fff9c4
    style SaveSummary fill:#fff9c4
    style Complete fill:#c8e6c9
    style Catch fill:#ffcdd2
```

### 출력 파일 구조

```mermaid
graph LR
    A[forecasting_analysis.ipynb] --> B[ENTR_BY_INS_FORECASTING.csv]
    A --> C[ENTR_INT_INS_FORECASTING.csv]
    A --> D[FORECASTING_SUMMARY.csv]
    
    B --> B1[원본 111열 +<br/>M1~M12 12열<br/>= 123열]
    C --> C1[원본 106열 +<br/>M1~M12 12열<br/>= 118열]
    D --> D1[구분, 총고객수,<br/>12개월 총/평균 예상금액]
    
    style A fill:#e1bee7
    style B fill:#c8e6c9
    style C fill:#c8e6c9
    style D fill:#fff9c4
```

---

## 8️⃣ 전체 데이터 흐름도

```mermaid
flowchart TB
    subgraph Input [입력 데이터]
        I1[(ENTR_BY_INS.csv<br/>270,192행)]
        I2[(ENTR_INT_INS.csv<br/>38,161행)]
        I3[(MVNO_PRD_PLC.csv<br/>138행)]
    end
    
    subgraph Process [처리 과정]
        P1[데이터 병합]
        P2[월별 예상 금액 계산]
        P3[통계 및 시각화]
    end
    
    subgraph Output [출력 결과]
        O1[ENTR_BY_INS_FORECASTING.csv<br/>270,192행 × 123열]
        O2[ENTR_INT_INS_FORECASTING.csv<br/>37,959행 × 118열]
        O3[FORECASTING_SUMMARY.csv<br/>요약 통계]
        O4[📊 시각화 차트 4개]
    end
    
    I1 --> P1
    I2 --> P1
    I3 --> P1
    
    P1 --> P2
    P2 --> P3
    
    P3 --> O1
    P3 --> O2
    P3 --> O3
    P3 --> O4
    
    style Input fill:#e3f2fd
    style Process fill:#fff9c4
    style Output fill:#c8e6c9
```

---

## 9️⃣ 핵심 계산 로직 요약

### 월별 예상 금액 계산 공식

```
월별_예상_금액 = MAX(0, 기본_금액 - 총_할인액)

where:
  기본_금액 = 정책금 (존재시) OR 기본료 (기본값)
  
  총_할인액 = 평생할인 + 기간할인(정책기간내) + 이벤트가(정책기간내)
  
  정책기간 = 정책반영시작일 <= 대상월 <= 정책반영종료일
```

### 시간 계산 로직

```mermaid
graph LR
    A[가입일] -->|+0개월| M1[M1]
    A -->|+1개월| M2[M2]
    A -->|+2개월| M3[M3]
    A -->|...| M11[...]
    A -->|+11개월| M12[M12]
    
    M1 -.->|정책기간 확인| P1{정책 적용?}
    M2 -.->|정책기간 확인| P2{정책 적용?}
    M3 -.->|정책기간 확인| P3{정책 적용?}
    M12 -.->|정책기간 확인| P12{정책 적용?}
    
    P1 -->|예| D1[모든 할인 적용]
    P1 -->|아니오| D2[평생할인만 적용]
    
    style A fill:#ffccbc
    style M1 fill:#c8e6c9
    style M2 fill:#c8e6c9
    style M3 fill:#c8e6c9
    style M12 fill:#c8e6c9
    style D1 fill:#bbdefb
    style D2 fill:#fff9c4
```

---

## 🔟 예외 처리 흐름

```mermaid
flowchart TD
    Start[함수 실행] --> Try{Try Block}
    
    Try -->|정상| Normal[정상 처리 흐름]
    Try -->|예외 발생| Catch[Exception 캐치]
    
    Normal --> Return[결과 반환]
    Catch --> Log[에러 메시지 출력]
    Log --> ReturnZero[0으로 채운 리스트 반환]
    
    Return --> End([종료])
    ReturnZero --> End
    
    style Start fill:#e3f2fd
    style Normal fill:#c8e6c9
    style Catch fill:#ffccbc
    style ReturnZero fill:#ffcdd2
    style End fill:#e1bee7
```

---

## 📊 성능 및 규모

### 처리 규모

| 구분 | ENTR_BY_INS | ENTR_INT_INS |
|------|-------------|--------------|
| **입력 행수** | 270,192 | 38,161 |
| **입력 열수** | 111 | 106 |
| **병합 후 열수** | 120 | 115 |
| **예상 금액 열 추가** | +12 (M1~M12) | +12 (M1~M12) |
| **최종 열수** | 132 | 127 |
| **매핑 성공률** | 100.0% | 99.5% |
| **처리 대상** | 270,192건 | 37,959건 |

### 계산 복잡도

```
총 계산 횟수 = (ENTR_BY_INS 고객수 + ENTR_INT_INS 고객수) × 12개월
             = (270,192 + 37,959) × 12
             = 3,697,812번의 월별 금액 계산
```

---

## 📝 주요 특징

### ✅ 장점
1. **동적 정책 반영**: 정책 기간에 따라 자동으로 할인 적용
2. **가입일 기준 계산**: 각 고객의 실제 가입일을 기준으로 예측
3. **유연한 할인 로직**: 평생할인, 기간할인, 이벤트가를 구분하여 적용
4. **완전한 데이터 보존**: 원본 데이터에 예상 금액 컬럼만 추가
5. **시각화 제공**: 4가지 차트로 다각도 분석

### ⚠️ 주의사항
1. **가입일 필수**: 가입일이 없는 데이터는 예상 금액이 0으로 처리
2. **정책 기간 검증**: 정책반영시작일/종료일이 유효하지 않으면 할인 미적용
3. **음수 방지**: 최종 금액이 음수가 되지 않도록 `max(0, amount)` 처리
4. **대용량 처리**: 30만+ 행 × 12개월 계산이므로 처리 시간 소요

---

## 🎯 활용 방안

```mermaid
mindmap
  root((예상 금액<br/>활용))
    재무 예측
      월별 매출 전망
      고객 생애 가치 LTV
      캐시플로우 예측
    마케팅
      고객 세그먼테이션
      타겟 마케팅
      프로모션 효과 분석
    정책 수립
      요금제 최적화
      할인 정책 평가
      신규 상품 기획
    위험 관리
      이탈 가능성 분석
      수익성 모니터링
      이상 패턴 탐지
```

---

## 📌 결론

이 플로우 차트는 `forecasting_analysis.ipynb`의 전체 프로세스를 시각화한 것으로, 다음과 같은 핵심 단계를 포함합니다:

1. **데이터 준비**: 3개 CSV 파일 로드 및 병합
2. **계산 로직**: 정책 기간과 할인을 고려한 월별 예상 금액 산정
3. **결과 생성**: 12개월 예상 금액이 추가된 CSV 파일 생성
4. **분석 및 시각화**: 4가지 차트로 다각도 분석 제공

이를 통해 MVNO 사업자는 가입 고객의 향후 12개월간 예상 매출을 정확히 예측하고, 데이터 기반 의사결정을 할 수 있습니다.

