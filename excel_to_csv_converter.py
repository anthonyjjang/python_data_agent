#!/usr/bin/env python3
"""
Excel to CSV Converter
Excel 파일들을 CSV 파일로 변환하는 스크립트
"""

import pandas as pd
import os
from pathlib import Path
from datetime import datetime


class ExcelToCSVConverter:
    """Excel 파일을 CSV로 변환하는 클래스"""
    
    def __init__(self, input_dir='csv/excel', output_dir='csv/converted'):
        """
        초기화
        
        Args:
            input_dir: Excel 파일이 있는 디렉토리
            output_dir: CSV 파일을 저장할 디렉토리
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def convert_single_file(self, excel_file, sheet_name=None, encoding='utf-8-sig'):
        """
        단일 Excel 파일을 CSV로 변환
        
        Args:
            excel_file: Excel 파일 경로
            sheet_name: 변환할 시트 이름 (None이면 첫 번째 시트)
            encoding: CSV 인코딩 (기본: utf-8-sig - Excel에서 한글 깨짐 방지)
        
        Returns:
            변환된 CSV 파일 경로
        """
        excel_path = Path(excel_file)
        
        print(f"\n📂 처리 중: {excel_path.name}")
        
        try:
            # Excel 파일 읽기
            if sheet_name:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                output_name = f"{excel_path.stem}_{sheet_name}.csv"
            else:
                df = pd.read_excel(excel_path)
                output_name = f"{excel_path.stem}.csv"
            
            # CSV 파일로 저장
            output_path = self.output_dir / output_name
            df.to_csv(output_path, index=False, encoding=encoding)
            
            print(f"✅ 변환 완료: {output_path}")
            print(f"   - 행 수: {len(df):,}행")
            print(f"   - 열 수: {len(df.columns)}열")
            print(f"   - 파일 크기: {output_path.stat().st_size / 1024:.2f} KB")
            
            return output_path
            
        except Exception as e:
            print(f"❌ 변환 실패: {excel_path.name}")
            print(f"   오류: {str(e)}")
            return None
    
    def convert_all_sheets(self, excel_file, encoding='utf-8-sig'):
        """
        Excel 파일의 모든 시트를 개별 CSV로 변환
        
        Args:
            excel_file: Excel 파일 경로
            encoding: CSV 인코딩
        
        Returns:
            변환된 CSV 파일 경로 리스트
        """
        excel_path = Path(excel_file)
        converted_files = []
        
        print(f"\n📂 처리 중: {excel_path.name} (모든 시트)")
        
        try:
            # 모든 시트 읽기
            excel_file_obj = pd.ExcelFile(excel_path)
            sheet_names = excel_file_obj.sheet_names
            
            print(f"   발견된 시트: {len(sheet_names)}개 - {sheet_names}")
            
            for sheet_name in sheet_names:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                
                # 파일명에 시트 이름 포함
                output_name = f"{excel_path.stem}_{sheet_name}.csv"
                output_path = self.output_dir / output_name
                
                df.to_csv(output_path, index=False, encoding=encoding)
                converted_files.append(output_path)
                
                print(f"   ✅ 시트 '{sheet_name}': {len(df):,}행 × {len(df.columns)}열")
            
            print(f"✅ 전체 변환 완료: {len(converted_files)}개 파일")
            
        except Exception as e:
            print(f"❌ 변환 실패: {excel_path.name}")
            print(f"   오류: {str(e)}")
        
        return converted_files
    
    def convert_all_files(self, all_sheets=False, encoding='utf-8-sig'):
        """
        디렉토리의 모든 Excel 파일을 CSV로 변환
        
        Args:
            all_sheets: True면 모든 시트를 개별 CSV로, False면 첫 번째 시트만
            encoding: CSV 인코딩
        
        Returns:
            변환 결과 통계
        """
        print("=" * 70)
        print("🔄 Excel to CSV 변환 시작")
        print("=" * 70)
        print(f"입력 디렉토리: {self.input_dir}")
        print(f"출력 디렉토리: {self.output_dir}")
        print(f"인코딩: {encoding}")
        print(f"모든 시트 변환: {'예' if all_sheets else '아니오'}")
        
        # Excel 파일 찾기
        excel_files = list(self.input_dir.glob('*.xlsx')) + list(self.input_dir.glob('*.xls'))
        
        if not excel_files:
            print("\n❌ Excel 파일을 찾을 수 없습니다.")
            return
        
        print(f"\n📊 발견된 Excel 파일: {len(excel_files)}개")
        
        success_count = 0
        fail_count = 0
        total_files = 0
        
        for excel_file in excel_files:
            try:
                if all_sheets:
                    converted = self.convert_all_sheets(excel_file, encoding)
                    if converted:
                        success_count += len(converted)
                        total_files += len(converted)
                else:
                    converted = self.convert_single_file(excel_file, encoding=encoding)
                    if converted:
                        success_count += 1
                    else:
                        fail_count += 1
                    total_files += 1
            except Exception as e:
                fail_count += 1
                print(f"❌ {excel_file.name} 처리 중 오류: {str(e)}")
        
        # 결과 요약
        print("\n" + "=" * 70)
        print("📊 변환 결과 요약")
        print("=" * 70)
        print(f"✅ 성공: {success_count}개")
        print(f"❌ 실패: {fail_count}개")
        print(f"📁 출력 디렉토리: {self.output_dir.absolute()}")
        print("=" * 70)
        
        return {
            'success': success_count,
            'fail': fail_count,
            'total': total_files,
            'output_dir': str(self.output_dir.absolute())
        }
    
    def preview_file(self, csv_file, rows=5):
        """
        변환된 CSV 파일 미리보기
        
        Args:
            csv_file: CSV 파일 경로
            rows: 표시할 행 수
        """
        try:
            df = pd.read_csv(csv_file, encoding='utf-8-sig', nrows=rows)
            print(f"\n📋 {Path(csv_file).name} 미리보기 (상위 {rows}행)")
            print("=" * 70)
            print(df)
            print("=" * 70)
            print(f"전체 컬럼: {', '.join(df.columns)}")
        except Exception as e:
            print(f"❌ 미리보기 실패: {str(e)}")


def main():
    """메인 실행 함수"""
    
    # 변환기 생성
    converter = ExcelToCSVConverter(
        input_dir='csv/excel',
        output_dir='csv/converted'
    )
    
    # 옵션 선택
    print("\n🔧 Excel to CSV 변환 도구")
    print("=" * 70)
    print("1. 모든 파일의 첫 번째 시트만 변환 (빠름)")
    print("2. 모든 파일의 모든 시트 변환 (권장)")
    print("3. 특정 파일만 변환")
    print("=" * 70)
    
    choice = input("\n선택 (1-3, 기본값: 2): ").strip() or '2'
    
    if choice == '1':
        # 첫 번째 시트만 변환
        converter.convert_all_files(all_sheets=False, encoding='utf-8-sig')
        
    elif choice == '2':
        # 모든 시트 변환
        converter.convert_all_files(all_sheets=True, encoding='utf-8-sig')
        
    elif choice == '3':
        # 특정 파일 선택
        excel_files = list(Path('csv/excel').glob('*.xlsx')) + list(Path('csv/excel').glob('*.xls'))
        
        print("\n📁 사용 가능한 파일:")
        for idx, file in enumerate(excel_files, 1):
            print(f"{idx}. {file.name}")
        
        file_idx = int(input("\n파일 번호 선택: ")) - 1
        
        if 0 <= file_idx < len(excel_files):
            all_sheets = input("모든 시트 변환? (y/n, 기본값: y): ").strip().lower() != 'n'
            
            if all_sheets:
                converter.convert_all_sheets(excel_files[file_idx])
            else:
                converter.convert_single_file(excel_files[file_idx])
        else:
            print("❌ 잘못된 파일 번호입니다.")
    
    # 변환된 파일 미리보기
    preview = input("\n변환된 파일 미리보기? (y/n): ").strip().lower()
    if preview == 'y':
        csv_files = list(Path('csv/converted').glob('*.csv'))
        if csv_files:
            print(f"\n📁 변환된 파일: {len(csv_files)}개")
            for idx, file in enumerate(csv_files[:5], 1):  # 최대 5개만 표시
                converter.preview_file(file, rows=3)


if __name__ == '__main__':
    main()

