#!/usr/bin/env python3
"""
Excel 업로드 및 질의응답 테스트 스크립트
"""

import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def test_excel_load():
    """Excel 파일 로드 테스트"""
    print("=" * 60)
    print("📊 Excel 파일 로드 테스트")
    print("=" * 60)
    
    excel_files = [
        "csv/excel/정산요약.xlsx",
        "csv/excel/2508월 통합 개통처리부 분석.xlsx",
    ]
    
    for excel_file in excel_files:
        if not os.path.exists(excel_file):
            print(f"⚠️ 파일 없음: {excel_file}")
            continue
            
        try:
            print(f"\n📁 파일: {excel_file}")
            df = pd.read_excel(excel_file)
            print(f"✅ 로드 성공")
            print(f"   - 행 수: {len(df):,}")
            print(f"   - 열 수: {len(df.columns)}")
            print(f"   - 컬럼: {list(df.columns)[:5]}...")
            print(f"   - 메모리: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
            
            # 샘플 데이터 확인
            print("\n📋 샘플 데이터 (상위 3행):")
            print(df.head(3).to_string())
            
        except Exception as e:
            print(f"❌ 로드 실패: {str(e)}")

def test_api_key():
    """API 키 확인 테스트"""
    print("\n" + "=" * 60)
    print("🔑 API 키 확인 테스트")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        api_key = api_key.strip()
        print(f"✅ API 키 존재: 예")
        print(f"📏 길이: {len(api_key)} 문자")
        print(f"🔤 시작: {api_key[:10]}...")
        print(f"🔤 끝: ...{api_key[-4:]}")
        
        if api_key.startswith('sk-'):
            print("✅ 형식: 올바름")
        else:
            print("⚠️ 형식: 의심스러움")
            
        if ' ' in api_key:
            print("⚠️ 경고: 공백 포함")
        if '\n' in api_key or '\r' in api_key:
            print("⚠️ 경고: 줄바꿈 포함")
    else:
        print("❌ API 키 없음")
        print("💡 .env 파일에 OPENAI_API_KEY를 설정하세요")

def test_openai_connection():
    """OpenAI API 연결 테스트"""
    print("\n" + "=" * 60)
    print("🤖 OpenAI API 연결 테스트")
    print("=" * 60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ API 키가 없어 테스트를 건너뜁니다")
        return False
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key.strip())
        
        # 간단한 테스트 요청
        print("📡 테스트 요청 전송 중...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, just testing. Reply with 'OK'."}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ API 연결 성공")
        print(f"📝 응답: {result}")
        return True
        
    except Exception as e:
        print(f"❌ API 연결 실패: {str(e)}")
        
        error_str = str(e).lower()
        if '400' in error_str or 'bad request' in error_str:
            print("🚨 400 에러: 잘못된 요청")
            print("💡 가능한 원인:")
            print("   - 잘못된 모델명")
            print("   - API 키 형식 오류")
        elif '401' in error_str or 'unauthorized' in error_str:
            print("🚨 401 에러: 인증 실패")
            print("💡 API 키를 확인하세요")
        elif '429' in error_str:
            print("🚨 429 에러: 요청 한도 초과")
            print("💡 잠시 후 다시 시도하세요")
            
        return False

def test_data_query_simulation():
    """데이터 질의 시뮬레이션"""
    print("\n" + "=" * 60)
    print("💬 데이터 질의 시뮬레이션")
    print("=" * 60)
    
    # 샘플 데이터 생성
    df = pd.DataFrame({
        '지역': ['서울', '부산', '대구', '인천', '광주'],
        '인구': [10000000, 3500000, 2500000, 3000000, 1500000],
        '면적': [605, 770, 884, 1063, 501]
    })
    
    print("📊 샘플 데이터:")
    print(df)
    
    # 질문 예시
    questions = [
        "인구가 가장 많은 지역은?",
        "면적이 가장 큰 지역은?",
        "인구 밀도가 가장 높은 지역은?"
    ]
    
    print("\n📝 질문 예시:")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")
    
    # 간단한 쿼리 테스트
    print("\n🔍 쿼리 테스트:")
    max_population = df.loc[df['인구'].idxmax()]
    print(f"✅ 인구가 가장 많은 지역: {max_population['지역']} ({max_population['인구']:,}명)")

def main():
    """메인 테스트 실행"""
    print("\n" + "🧪 " * 20)
    print("Excel 업로드 및 질의응답 테스트 스크립트")
    print("🧪 " * 20 + "\n")
    
    # 1. Excel 파일 로드 테스트
    test_excel_load()
    
    # 2. API 키 확인
    test_api_key()
    
    # 3. OpenAI API 연결 테스트
    api_ok = test_openai_connection()
    
    # 4. 데이터 질의 시뮬레이션
    test_data_query_simulation()
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    print(f"API 연결: {'✅ 성공' if api_ok else '❌ 실패'}")
    print("\n💡 다음 단계:")
    if api_ok:
        print("  1. Streamlit 앱 실행: streamlit run app.py")
        print("  2. Excel 파일 업로드")
        print("  3. 질문 입력 및 테스트")
    else:
        print("  1. .env 파일에 올바른 OPENAI_API_KEY 설정")
        print("  2. 또는 Ollama 설치 및 실행 (무료)")
        print("  3. 다시 테스트")
    print("=" * 60)

if __name__ == "__main__":
    main()

