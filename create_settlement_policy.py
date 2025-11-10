#!/usr/bin/env python3
"""
정산 월 기준 상품 정책 파일 생성기

사용법:
    python create_settlement_policy.py --yymm 2508

기능:
    - 전월 가입자 데이터와 당월 개통처리부 데이터에서 상품코드 추출
    - MVNO_PRD_PLC.csv를 기준으로 필터링
    - YYMM_MVNO_PRD_PLC.csv 파일 생성
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import logging
from datetime import datetime
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('create_settlement_policy.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def load_csv_with_encoding(file_path, encodings=['utf-8', 'cp949', 'euc-kr', 'utf-8-sig']):
    """
    여러 인코딩을 시도하여 CSV 파일 로드
    """
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
            logger.info(f"✅ 파일 로드 성공: {file_path.name} (인코딩: {encoding})")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.warning(f"⚠️ {encoding} 인코딩 시도 실패: {e}")
            continue
    
    raise ValueError(f"❌ 파일 로드 실패: {file_path}")


def extract_product_codes(df, column_candidates, df_name="DataFrame"):
    """
    데이터프레임에서 상품코드 추출
    
    Args:
        df: pandas DataFrame
        column_candidates: 확인할 컬럼명 리스트
        df_name: 데이터프레임 이름 (로깅용)
    
    Returns:
        set: 고유한 상품코드 집합
    """
    product_codes = set()
    found_columns = []
    
    for col in column_candidates:
        if col in df.columns:
            # NaN이 아닌 값만 추출
            codes = df[col].dropna().astype(str).str.strip()
            # 빈 문자열 제외
            codes = codes[codes != '']
            product_codes.update(codes.tolist())
            found_columns.append(col)
            logger.info(f"  - {col}: {len(codes.unique())}개 고유 코드")
    
    if not found_columns:
        logger.warning(f"⚠️ {df_name}에서 상품코드 컬럼을 찾을 수 없습니다.")
        logger.info(f"   사용 가능한 컬럼: {', '.join(df.columns[:10].tolist())}...")
    else:
        logger.info(f"✅ {df_name}에서 {len(found_columns)}개 컬럼에서 {len(product_codes)}개 고유 코드 추출")
    
    return product_codes, found_columns


def extract_pricing_info(df, df_name="DataFrame"):
    """
    데이터프레임에서 요금 정보 추출
    
    Returns:
        dict: {상품코드: 기본요금} 매핑
    """
    pricing_info = {}
    
    # 상품코드 컬럼 찾기
    product_col = None
    for col in ['MVNO상품코드', '개통요금제코드', '상품코드', '요금제코드', 'MVNO_PRD_CD']:
        if col in df.columns:
            product_col = col
            break
    
    if product_col is None:
        logger.warning(f"⚠️ {df_name}에서 상품코드 컬럼을 찾을 수 없습니다.")
        return pricing_info
    
    # 요금 컬럼 찾기
    price_col = None
    for col in ['기본요금', '요금', '월정액', '월정액요금', '기본료']:
        if col in df.columns:
            price_col = col
            break
    
    if price_col is None:
        logger.info(f"ℹ️ {df_name}에서 요금 컬럼을 찾을 수 없습니다.")
        return pricing_info
    
    # 상품코드별 평균 요금 계산
    try:
        df_temp = df[[product_col, price_col]].copy()
        df_temp[price_col] = pd.to_numeric(df_temp[price_col], errors='coerce')
        
        pricing = df_temp.groupby(product_col)[price_col].agg(['mean', 'count']).reset_index()
        pricing = pricing[pricing['count'] > 0]
        
        for _, row in pricing.iterrows():
            code = str(row[product_col]).strip()
            price = row['mean']
            if not pd.isna(price) and price > 0:
                pricing_info[code] = int(price)
        
        logger.info(f"✅ {df_name}에서 {len(pricing_info)}개 상품의 요금 정보 추출")
        logger.info(f"   컬럼: {product_col} -> {price_col}")
        
    except Exception as e:
        logger.warning(f"⚠️ 요금 정보 추출 중 오류: {e}")
    
    return pricing_info


def create_settlement_policy(yymm: str, base_dir: Path = Path(".")):
    """
    정산 월 기준 상품 정책 파일 생성
    
    Args:
        yymm: 정산 연월 (예: "2508")
        base_dir: 기준 디렉토리
    """
    logger.info("="*70)
    logger.info(f"🚀 정산 월 상품 정책 파일 생성 시작: {yymm}")
    logger.info("="*70)
    
    # 1. 파일 경로 설정
    csv_dir = base_dir / "csv"
    converted_dir = csv_dir / "converted"
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    # 전월 YYMM 계산
    year = int(yymm[:2])
    month = int(yymm[2:4])
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_yymm = f"{prev_year:02d}{prev_month:02d}"
    
    # 파일 경로
    prev_subscriber_file = csv_dir / f"20{prev_yymm}_SS001344_ENTR_BY_STACC_PTN_INS_001.csv"
    current_processing_file = converted_dir / f"{yymm}월 통합 개통처리부 분석.csv"
    policy_file = csv_dir / "MVNO_PRD_PLC.csv"
    output_file = output_dir / f"{yymm}_MVNO_PRD_PLC.csv"
    
    logger.info(f"\n📁 파일 경로:")
    logger.info(f"  1️⃣ 전월 가입자: {prev_subscriber_file.name}")
    logger.info(f"  2️⃣ 당월 개통처리부: {current_processing_file.name}")
    logger.info(f"  3️⃣ 원본 정책: {policy_file.name}")
    logger.info(f"  4️⃣ 출력 파일: {output_file.name}")
    
    # 2. 파일 존재 확인
    logger.info(f"\n📋 파일 존재 확인:")
    missing_files = []
    
    for file_path, desc in [
        (prev_subscriber_file, "전월 가입자"),
        (current_processing_file, "당월 개통처리부"),
        (policy_file, "원본 정책")
    ]:
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            logger.info(f"  ✅ {desc}: {size_mb:.2f}MB")
        else:
            logger.error(f"  ❌ {desc}: 파일 없음")
            missing_files.append(str(file_path))
    
    if missing_files:
        logger.error(f"\n❌ 필수 파일이 없습니다:")
        for f in missing_files:
            logger.error(f"   - {f}")
        return False
    
    # 3. 원본 정책 파일 로드
    logger.info(f"\n📖 원본 정책 파일 로드 중...")
    df_policy = load_csv_with_encoding(policy_file)
    logger.info(f"   행 수: {len(df_policy):,}")
    logger.info(f"   컬럼 수: {len(df_policy.columns)}")
    logger.info(f"   주요 컬럼: {', '.join(df_policy.columns[:10].tolist())}")
    
    # 4. 전월 가입자 데이터 로드
    logger.info(f"\n📖 전월 가입자 데이터 로드 중...")
    df_prev = load_csv_with_encoding(prev_subscriber_file)
    logger.info(f"   행 수: {len(df_prev):,}")
    
    # 상품코드 추출 대상 컬럼
    product_columns = ['MVNO상품코드', '개통요금제코드', '상품코드', '요금제코드', 'MVNO_PRD_CD']
    
    logger.info(f"\n🔍 전월 가입자 데이터에서 상품코드 추출:")
    prev_codes, prev_cols = extract_product_codes(df_prev, product_columns, "전월 가입자")
    
    # 요금 정보 추출
    logger.info(f"\n💰 전월 가입자 데이터에서 요금 정보 추출:")
    prev_pricing = extract_pricing_info(df_prev, "전월 가입자")
    
    # 5. 당월 개통처리부 데이터 로드
    logger.info(f"\n📖 당월 개통처리부 데이터 로드 중...")
    df_current = load_csv_with_encoding(current_processing_file)
    logger.info(f"   행 수: {len(df_current):,}")
    
    logger.info(f"\n🔍 당월 개통처리부에서 상품코드 추출:")
    current_codes, current_cols = extract_product_codes(df_current, product_columns, "당월 개통처리부")
    
    # 요금 정보 추출
    logger.info(f"\n💰 당월 개통처리부에서 요금 정보 추출:")
    current_pricing = extract_pricing_info(df_current, "당월 개통처리부")
    
    # 6. 상품코드 통합
    all_codes = prev_codes.union(current_codes)
    logger.info(f"\n📊 상품코드 통계:")
    logger.info(f"  - 전월 가입자: {len(prev_codes):,}개")
    logger.info(f"  - 당월 개통처리부: {len(current_codes):,}개")
    logger.info(f"  - 전체 고유 코드: {len(all_codes):,}개")
    
    # 7. 원본 정책에서 필터링
    # MVNO_PRD_PLC의 상품코드 컬럼 찾기
    policy_product_col = None
    for col in ['요금제코드', 'MVNO_PRD_CD', 'MVNO상품코드', '상품코드']:
        if col in df_policy.columns:
            policy_product_col = col
            break
    
    if policy_product_col is None:
        logger.error(f"\n❌ 정책 파일에서 상품코드 컬럼을 찾을 수 없습니다.")
        logger.info(f"   사용 가능한 컬럼: {', '.join(df_policy.columns.tolist())}")
        return False
    
    logger.info(f"\n🔍 정책 파일 필터링 (기준 컬럼: {policy_product_col}):")
    
    # 정책 파일의 상품코드를 문자열로 변환
    df_policy[policy_product_col] = df_policy[policy_product_col].astype(str).str.strip()
    
    # 필터링
    df_filtered = df_policy[df_policy[policy_product_col].isin(all_codes)].copy()
    
    logger.info(f"  - 원본 정책 행 수: {len(df_policy):,}개")
    logger.info(f"  - 필터링 후 행 수: {len(df_filtered):,}개")
    logger.info(f"  - 제외된 행: {len(df_policy) - len(df_filtered):,}개")
    
    if len(df_filtered) == 0:
        logger.warning(f"\n⚠️ 필터링 결과가 비어있습니다.")
        logger.info(f"   정책 파일의 상품코드 샘플: {df_policy[policy_product_col].head().tolist()}")
        logger.info(f"   추출된 상품코드 샘플: {list(all_codes)[:5]}")
        return False
    
    # 8. 요금 정보 병합 (있는 경우)
    all_pricing = {**prev_pricing, **current_pricing}  # current가 우선
    
    if all_pricing:
        logger.info(f"\n💰 요금 정보 병합:")
        logger.info(f"  - 요금 정보가 있는 상품: {len(all_pricing):,}개")
        
        # 정책 파일에 요금 컬럼이 없으면 추가
        if '추출요금' not in df_filtered.columns:
            df_filtered['추출요금'] = df_filtered[policy_product_col].map(all_pricing)
            added = df_filtered['추출요금'].notna().sum()
            logger.info(f"  - 요금 정보 추가: {added:,}개 상품")
    
    # 9. 메타데이터 추가
    df_filtered['생성일시'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df_filtered['정산연월'] = yymm
    df_filtered['데이터출처'] = '전월가입자+당월개통처리부'
    
    # 10. 결과 저장
    logger.info(f"\n💾 결과 저장 중...")
    df_filtered.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    output_size_mb = output_file.stat().st_size / (1024 * 1024)
    logger.info(f"  ✅ 저장 완료: {output_file}")
    logger.info(f"  📊 파일 크기: {output_size_mb:.2f}MB")
    logger.info(f"  📋 행 수: {len(df_filtered):,}")
    logger.info(f"  📋 컬럼 수: {len(df_filtered.columns)}")
    
    # 11. 요약 통계
    logger.info(f"\n" + "="*70)
    logger.info(f"✅ 정산 월 상품 정책 파일 생성 완료!")
    logger.info(f"="*70)
    logger.info(f"\n📊 최종 통계:")
    logger.info(f"  - 정산 연월: {yymm} ({year+2000}년 {month}월)")
    logger.info(f"  - 전월 가입자 상품: {len(prev_codes):,}개")
    logger.info(f"  - 당월 개통처리부 상품: {len(current_codes):,}개")
    logger.info(f"  - 전체 고유 상품: {len(all_codes):,}개")
    logger.info(f"  - 정책 매칭된 상품: {len(df_filtered):,}개")
    logger.info(f"  - 출력 파일: {output_file}")
    
    # 상품코드별 집계 (상위 10개)
    if len(df_filtered) > 0:
        logger.info(f"\n🔝 상위 10개 상품코드:")
        top_codes = df_filtered[policy_product_col].value_counts().head(10)
        for code, count in top_codes.items():
            logger.info(f"  - {code}: {count}개")
    
    return True


def main():
    """
    메인 함수
    """
    parser = argparse.ArgumentParser(
        description='정산 월 기준 상품 정책 파일 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
    # 2508월(2025년 8월) 정책 파일 생성
    python create_settlement_policy.py --yymm 2508
    
    # 특정 디렉토리에서 실행
    python create_settlement_policy.py --yymm 2508 --dir /path/to/project
    
필수 파일 구조:
    csv/202507_SS001344_ENTR_BY_STACC_PTN_INS_001.csv  (전월 가입자)
    csv/converted/2508월 통합 개통처리부 분석.csv      (당월 개통처리부)
    csv/MVNO_PRD_PLC.csv                                (원본 정책)
        """
    )
    
    parser.add_argument(
        '--yymm',
        required=True,
        help='정산 연월 (예: 2508 = 2025년 8월)'
    )
    
    parser.add_argument(
        '--dir',
        default='.',
        help='프로젝트 기준 디렉토리 (기본값: 현재 디렉토리)'
    )
    
    args = parser.parse_args()
    
    # YYMM 형식 검증
    if not (len(args.yymm) == 4 and args.yymm.isdigit()):
        logger.error(f"❌ 잘못된 YYMM 형식: {args.yymm}")
        logger.error(f"   올바른 형식: 4자리 숫자 (예: 2508)")
        return 1
    
    base_dir = Path(args.dir).resolve()
    if not base_dir.exists():
        logger.error(f"❌ 디렉토리가 존재하지 않습니다: {base_dir}")
        return 1
    
    # 정책 파일 생성
    success = create_settlement_policy(args.yymm, base_dir)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

