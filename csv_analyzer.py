#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV 데이터 분석 프로그램
통신사 가입자 정보 및 요금제 데이터 분석
분석 결과를 database.md 파일로 저장
"""

import pandas as pd
import os
import glob
from pathlib import Path
from datetime import datetime

def number_to_excel_column(n):
    """
    숫자를 엑셀 컬럼 ID로 변환 (1=A, 2=B, ..., 26=Z, 27=AA, ...)
    
    Args:
        n (int): 컬럼 번호 (1부터 시작)
    
    Returns:
        str: 엑셀 컬럼 ID
    """
    result = ""
    while n > 0:
        n -= 1  # 0-based로 변환
        result = chr(65 + n % 26) + result
        n //= 26
    return result

class CSVAnalyzer:
    def __init__(self, csv_folder='csv', output_file='database.md'):
        """
        CSV 분석기 초기화
        
        Args:
            csv_folder (str): CSV 파일들이 있는 폴더 경로
            output_file (str): 분석 결과를 저장할 마크다운 파일명
        """
        self.csv_folder = csv_folder
        self.output_file = output_file
        self.dataframes = {}
        self.analysis_results = []
        self.column_info = []
        self.file_encodings = {}
        
    def load_csv_files(self):
        """CSV 폴더의 모든 CSV 파일을 로드"""
        csv_files = glob.glob(os.path.join(self.csv_folder, '*.csv'))
        
        if not csv_files:
            print(f"❌ {self.csv_folder} 폴더에 CSV 파일이 없습니다.")
            return
            
        print(f"📁 {len(csv_files)}개의 CSV 파일을 발견했습니다.\n")
        
        for file_path in csv_files:
            try:
                # 파일명 추출
                file_name = Path(file_path).name
                
                # 파일별 최적 인코딩 설정
                file_encodings = {
                    'ENTR_BY_INS.csv': 'cp949',      # M-2 가입자 정보 (한글 컬럼명)
                    'ENTR_INT_INS.csv': 'utf-8',     # M-1 신규 가입자 정보 
                    'MVNO_PRD_PLC.csv': 'utf-8'      # 요금제 정보
                }
                
                # 파일별 최적 인코딩 우선 시도, 실패시 다른 인코딩들 시도
                preferred_encoding = file_encodings.get(file_name, 'utf-8')
                encodings = [preferred_encoding] + ['utf-8', 'cp949', 'euc-kr', 'latin1']
                encodings = list(dict.fromkeys(encodings))  # 중복 제거
                
                df = None
                used_encoding = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        used_encoding = encoding
                        print(f"✅ {file_name} 로드 성공 (인코딩: {encoding})")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is not None:
                    self.dataframes[file_name] = df
                    self.file_encodings[file_name] = used_encoding
                else:
                    print(f"❌ {file_name} 로드 실패 - 인코딩 문제")
                    
            except Exception as e:
                print(f"❌ {file_name} 로드 중 오류: {str(e)}")
    
    def analyze_file(self, file_name):
        """개별 CSV 파일 분석"""
        if file_name not in self.dataframes:
            print(f"❌ {file_name} 파일이 로드되지 않았습니다.")
            return
            
        df = self.dataframes[file_name]
        
        print(f"\n{'='*60}")
        print(f"📊 파일 분석: {file_name}")
        print(f"{'='*60}")
        
        # 분석 결과를 저장할 딕셔너리
        analysis = {
            'file_name': file_name,
            'encoding': self.file_encodings.get(file_name, 'unknown'),
            'shape': df.shape,
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2,
            'columns': list(zip(df.columns, df.dtypes.astype(str))),
            'sample_data': df.head(10),
            'numeric_stats': None,
            'missing_info': df.isnull().sum()
        }
        
        # 기본 정보
        print(f"📏 데이터 크기: {df.shape[0]:,}행 × {df.shape[1]}열")
        print(f"💾 메모리 사용량: {analysis['memory_usage']:.2f} MB")
        
        # 컬럼 정보
        print(f"\n📋 컬럼 정보:")
        print("-" * 50)
        for i, (col, dtype) in enumerate(analysis['columns'], 1):
            print(f"{i:2d}. {col:<30} ({dtype})")
        
        # 샘플 데이터 (상위 10개)
        print(f"\n📄 샘플 데이터 (상위 10개):")
        print("-" * 50)
        print(df.head(10).to_string(index=True))
        
        # 기본 통계 (숫자형 컬럼만)
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            analysis['numeric_stats'] = df[numeric_cols].describe()
            print(f"\n📈 숫자형 컬럼 기본 통계:")
            print("-" * 50)
            print(analysis['numeric_stats'].to_string())
        
        # 결측값 정보
        missing_info = analysis['missing_info']
        if missing_info.sum() > 0:
            print(f"\n⚠️  결측값 정보:")
            print("-" * 50)
            for col, missing_count in missing_info[missing_info > 0].items():
                missing_pct = (missing_count / len(df)) * 100
                print(f"{col}: {missing_count:,}개 ({missing_pct:.1f}%)")
        else:
            print(f"\n✅ 결측값 없음")
        
        # 분석 결과 저장
        self.analysis_results.append(analysis)
        
        # 컬럼 정보 수집
        for i, (col, dtype) in enumerate(analysis['columns'], 1):
            excel_col_id = number_to_excel_column(i)
            self.column_info.append({
                '파일명': file_name,
                '컬럼번호': i,
                '엑셀컬럼ID': excel_col_id,
                '컬럼명': col,
                '데이터타입': dtype,
                '결측값개수': df[col].isnull().sum() if col in df.columns else 0,
                '결측값비율(%)': round((df[col].isnull().sum() / len(df)) * 100, 2) if col in df.columns else 0
            })
    
    def analyze_all(self):
        """모든 로드된 CSV 파일 분석"""
        if not self.dataframes:
            print("❌ 로드된 CSV 파일이 없습니다.")
            return
            
        for file_name in self.dataframes.keys():
            self.analyze_file(file_name)
    
    def get_summary(self):
        """전체 요약 정보"""
        if not self.dataframes:
            return
            
        print(f"\n{'='*60}")
        print(f"📊 전체 요약")
        print(f"{'='*60}")
        
        total_rows = sum(df.shape[0] for df in self.dataframes.values())
        total_cols = sum(df.shape[1] for df in self.dataframes.values())
        
        print(f"📁 총 파일 수: {len(self.dataframes)}개")
        print(f"📏 총 데이터: {total_rows:,}행")
        print(f"📋 총 컬럼 수: {total_cols}개")
        
        for file_name, df in self.dataframes.items():
            print(f"  - {file_name}: {df.shape[0]:,}행 × {df.shape[1]}열")
    
    def save_to_markdown(self):
        """분석 결과를 database.md 파일로 저장"""
        if not self.analysis_results:
            print("❌ 저장할 분석 결과가 없습니다.")
            return
        
        # 마크다운 내용 생성
        md_content = []
        
        # 헤더
        md_content.append("# CSV 데이터베이스 분석 보고서")
        md_content.append(f"\n**분석 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md_content.append(f"**분석 파일 수**: {len(self.analysis_results)}개")
        
        # 전체 요약
        total_rows = sum(result['shape'][0] for result in self.analysis_results)
        total_cols = sum(result['shape'][1] for result in self.analysis_results)
        total_memory = sum(result['memory_usage'] for result in self.analysis_results)
        
        md_content.append("\n## 📊 전체 요약")
        md_content.append(f"- **총 데이터**: {total_rows:,}행")
        md_content.append(f"- **총 컬럼**: {total_cols}개")
        md_content.append(f"- **총 메모리 사용량**: {total_memory:.2f} MB")
        
        # 각 파일별 상세 분석
        for i, result in enumerate(self.analysis_results, 1):
            md_content.append(f"\n## {i}. {result['file_name']}")
            
            # 기본 정보
            md_content.append(f"\n### 📋 기본 정보")
            md_content.append(f"- **파일명**: `{result['file_name']}`")
            md_content.append(f"- **인코딩**: {result['encoding']}")
            md_content.append(f"- **데이터 크기**: {result['shape'][0]:,}행 × {result['shape'][1]}열")
            md_content.append(f"- **메모리 사용량**: {result['memory_usage']:.2f} MB")
            
            # 컬럼 정보
            md_content.append(f"\n### 📝 컬럼 정보")
            md_content.append("| 번호 | 컬럼명 | 데이터 타입 |")
            md_content.append("|------|--------|-------------|")
            for j, (col, dtype) in enumerate(result['columns'], 1):
                md_content.append(f"| {j} | `{col}` | {dtype} |")
            
            # 샘플 데이터
            md_content.append(f"\n### 📄 샘플 데이터 (상위 10개)")
            md_content.append("```")
            md_content.append(result['sample_data'].to_string(index=True))
            md_content.append("```")
            
            # 숫자형 컬럼 통계
            if result['numeric_stats'] is not None:
                md_content.append(f"\n### 📈 숫자형 컬럼 기본 통계")
                md_content.append("```")
                md_content.append(result['numeric_stats'].to_string())
                md_content.append("```")
            
            # 결측값 정보
            missing_info = result['missing_info']
            if missing_info.sum() > 0:
                md_content.append(f"\n### ⚠️ 결측값 정보")
                md_content.append("| 컬럼명 | 결측값 개수 | 비율(%) |")
                md_content.append("|--------|-------------|---------|")
                for col, missing_count in missing_info[missing_info > 0].items():
                    missing_pct = (missing_count / result['shape'][0]) * 100
                    md_content.append(f"| `{col}` | {missing_count:,} | {missing_pct:.1f}% |")
            else:
                md_content.append(f"\n### ✅ 결측값")
                md_content.append("결측값이 없습니다.")
            
            md_content.append("\n---")
        
        # 파일에 저장
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_content))
            print(f"\n✅ 분석 결과가 '{self.output_file}' 파일로 저장되었습니다.")
        except Exception as e:
            print(f"❌ 파일 저장 중 오류 발생: {str(e)}")
    
    def save_column_info_to_csv(self, output_file='column_info.csv'):
        """컬럼 정보를 CSV 파일로 저장"""
        if not self.column_info:
            print("❌ 저장할 컬럼 정보가 없습니다.")
            return
        
        try:
            # 컬럼 정보를 DataFrame으로 변환
            df_columns = pd.DataFrame(self.column_info)
            
            # CSV 파일로 저장
            df_columns.to_csv(output_file, index=False, encoding='utf-8')
            print(f"\n✅ 컬럼 정보가 '{output_file}' 파일로 저장되었습니다.")
            
            # 저장된 정보 요약 출력
            print(f"📊 저장된 컬럼 정보:")
            print(f"  - 총 컬럼 수: {len(df_columns)}개")
            print(f"  - 파일별 컬럼 수:")
            for file_name in df_columns['파일명'].unique():
                count = len(df_columns[df_columns['파일명'] == file_name])
                print(f"    · {file_name}: {count}개")
                
        except Exception as e:
            print(f"❌ 컬럼 정보 CSV 저장 중 오류 발생: {str(e)}")

def main():
    """메인 실행 함수"""
    print("🚀 CSV 데이터 분석 프로그램 시작")
    print("=" * 60)
    
    # CSV 분석기 초기화
    analyzer = CSVAnalyzer()
    
    # CSV 파일들 로드
    analyzer.load_csv_files()
    
    # 모든 파일 분석
    analyzer.analyze_all()
    
    # 전체 요약
    analyzer.get_summary()
    
    # 분석 결과를 database.md 파일로 저장
    analyzer.save_to_markdown()
    
    # 컬럼 정보를 CSV 파일로 저장
    analyzer.save_column_info_to_csv()
    
    print(f"\n🎉 분석 완료!")

if __name__ == "__main__":
    main()