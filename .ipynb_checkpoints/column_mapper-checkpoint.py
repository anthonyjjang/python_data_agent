#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
컬럼 매핑 정보 추출 프로그램
M-1 신규 가입자 정보(ENTR_INT_INS.csv)와 M-2 정산내역(ENTR_BY_INS.csv) 간의 
컬럼 매핑 관계를 분석하고 보고서를 생성합니다.
"""

import pandas as pd
import os
from datetime import datetime
from difflib import SequenceMatcher

class ColumnMapper:
    def __init__(self, column_info_file='column_info.csv'):
        """
        컬럼 매퍼 초기화
        
        Args:
            column_info_file (str): 컬럼 정보가 저장된 CSV 파일 경로
        """
        self.column_info_file = column_info_file
        self.m1_columns = []  # M-1 신규 가입자 정보 컬럼
        self.m2_columns = []  # M-2 정산내역 컬럼
        self.plan_columns = []  # 요금제 정보 컬럼
        self.mapping_results = []
        
    def load_column_info(self):
        """컬럼 정보 CSV 파일을 로드하고 파일별로 분류"""
        if not os.path.exists(self.column_info_file):
            print(f"❌ {self.column_info_file} 파일을 찾을 수 없습니다.")
            return False
            
        try:
            df = pd.read_csv(self.column_info_file, encoding='utf-8')
            
            # 파일별로 컬럼 정보 분류
            self.m1_columns = df[df['파일명'] == 'ENTR_INT_INS.csv'].copy()
            self.m2_columns = df[df['파일명'] == 'ENTR_BY_INS.csv'].copy()
            self.plan_columns = df[df['파일명'] == 'MVNO_PRD_PLC.csv'].copy()
            
            print(f"✅ 컬럼 정보 로드 완료:")
            print(f"  - M-1 신규 가입자: {len(self.m1_columns)}개 컬럼")
            print(f"  - M-2 정산내역: {len(self.m2_columns)}개 컬럼")
            print(f"  - 요금제 정보: {len(self.plan_columns)}개 컬럼")
            
            return True
            
        except Exception as e:
            print(f"❌ 컬럼 정보 로드 중 오류: {str(e)}")
            return False
    
    def calculate_similarity(self, str1, str2):
        """두 문자열 간의 유사도 계산"""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def find_exact_matches(self):
        """완전히 일치하는 컬럼명 찾기"""
        exact_matches = []
        
        m1_column_names = set(self.m1_columns['컬럼명'].tolist())
        m2_column_names = set(self.m2_columns['컬럼명'].tolist())
        
        common_columns = m1_column_names.intersection(m2_column_names)
        
        for col_name in common_columns:
            m1_info = self.m1_columns[self.m1_columns['컬럼명'] == col_name].iloc[0]
            m2_info = self.m2_columns[self.m2_columns['컬럼명'] == col_name].iloc[0]
            
            # 엑셀 컬럼 ID 가져오기
            m1_excel_id = m1_info.get('엑셀컬럼ID', f"Col{m1_info['컬럼번호']}")
            m2_excel_id = m2_info.get('엑셀컬럼ID', f"Col{m2_info['컬럼번호']}")
            
            exact_matches.append({
                'match_type': '완전일치',
                'm1_excel_id': m1_excel_id,
                'm1_column': col_name,
                'm1_type': m1_info['데이터타입'],
                'm1_missing': f"{m1_info['결측값개수']}개 ({m1_info['결측값비율(%)']}%)",
                'm2_excel_id': m2_excel_id,
                'm2_column': col_name,
                'm2_type': m2_info['데이터타입'],
                'm2_missing': f"{m2_info['결측값개수']}개 ({m2_info['결측값비율(%)']}%)",
                'similarity': 1.0,
                'notes': '동일한 컬럼명'
            })
        
        return exact_matches
    
    def find_similar_matches(self, threshold=0.7):
        """유사한 컬럼명 찾기"""
        similar_matches = []
        
        for _, m1_row in self.m1_columns.iterrows():
            m1_col = m1_row['컬럼명']
            best_match = None
            best_similarity = 0
            
            for _, m2_row in self.m2_columns.iterrows():
                m2_col = m2_row['컬럼명']
                
                # 완전 일치는 제외
                if m1_col == m2_col:
                    continue
                
                similarity = self.calculate_similarity(m1_col, m2_col)
                
                if similarity > best_similarity and similarity >= threshold:
                    best_similarity = similarity
                    best_match = m2_row
            
            if best_match is not None:
                # 엑셀 컬럼 ID 가져오기
                m1_excel_id = m1_row.get('엑셀컬럼ID', f"Col{m1_row['컬럼번호']}")
                m2_excel_id = best_match.get('엑셀컬럼ID', f"Col{best_match['컬럼번호']}")
                
                similar_matches.append({
                    'match_type': '유사일치',
                    'm1_excel_id': m1_excel_id,
                    'm1_column': m1_col,
                    'm1_type': m1_row['데이터타입'],
                    'm1_missing': f"{m1_row['결측값개수']}개 ({m1_row['결측값비율(%)']}%)",
                    'm2_excel_id': m2_excel_id,
                    'm2_column': best_match['컬럼명'],
                    'm2_type': best_match['데이터타입'],
                    'm2_missing': f"{best_match['결측값개수']}개 ({best_match['결측값비율(%)']}%)",
                    'similarity': best_similarity,
                    'notes': f'유사도: {best_similarity:.2f}'
                })
        
        return similar_matches
    
    def find_key_field_matches(self):
        """주요 키 필드 매칭 분석"""
        key_fields = {
            '가입번호': ['가입번호', '고객번호', '청구계정번호'],
            '요금제': ['요금제코드', '요금제명', '상품코드', '상품명'],
            '대리점': ['대리점코드', '대리점명', 'POS코드', 'POS명'],
            '일자': ['일자', '날짜', '시간', '년월'],
            '금액': ['금액', '료', '비용', '수수료']
        }
        
        key_matches = []
        
        for category, keywords in key_fields.items():
            m1_matches = []
            m2_matches = []
            
            # M-1에서 해당 키워드가 포함된 컬럼 찾기
            for _, row in self.m1_columns.iterrows():
                for keyword in keywords:
                    if keyword in row['컬럼명']:
                        m1_matches.append({
                            'column': row['컬럼명'],
                            'type': row['데이터타입'],
                            'missing': f"{row['결측값개수']}개 ({row['결측값비율(%)']}%)"
                        })
                        break
            
            # M-2에서 해당 키워드가 포함된 컬럼 찾기
            for _, row in self.m2_columns.iterrows():
                for keyword in keywords:
                    if keyword in row['컬럼명']:
                        m2_matches.append({
                            'column': row['컬럼명'],
                            'type': row['데이터타입'],
                            'missing': f"{row['결측값개수']}개 ({row['결측값비율(%)']}%)"
                        })
                        break
            
            if m1_matches or m2_matches:
                key_matches.append({
                    'category': category,
                    'm1_fields': m1_matches,
                    'm2_fields': m2_matches
                })
        
        return key_matches
    
    def analyze_mappings(self):
        """전체 매핑 분석 수행"""
        print("\n🔍 컬럼 매핑 분석 시작...")
        
        # 완전 일치 컬럼 찾기
        exact_matches = self.find_exact_matches()
        print(f"✅ 완전 일치 컬럼: {len(exact_matches)}개")
        
        # 유사 컬럼 찾기
        similar_matches = self.find_similar_matches()
        print(f"✅ 유사 컬럼: {len(similar_matches)}개")
        
        # 주요 키 필드 분석
        key_matches = self.find_key_field_matches()
        print(f"✅ 주요 키 필드 카테고리: {len(key_matches)}개")
        
        self.mapping_results = {
            'exact_matches': exact_matches,
            'similar_matches': similar_matches,
            'key_matches': key_matches
        }
        
        return True
    
    def generate_mapping_report(self, output_file='column_mapping_report.md'):
        """매핑 분석 결과를 마크다운 보고서로 생성"""
        if not self.mapping_results:
            print("❌ 분석 결과가 없습니다. analyze_mappings()을 먼저 실행하세요.")
            return
        
        md_content = []
        
        # 헤더
        md_content.append("# 컬럼 매핑 분석 보고서")
        md_content.append(f"\n**분석 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md_content.append("**분석 대상**: M-1 신규 가입자 정보 ↔ M-2 정산내역")
        
        # 전체 요약
        exact_count = len(self.mapping_results['exact_matches'])
        similar_count = len(self.mapping_results['similar_matches'])
        
        md_content.append("\n## 📊 매핑 요약")
        md_content.append(f"- **M-1 총 컬럼 수**: {len(self.m1_columns)}개")
        md_content.append(f"- **M-2 총 컬럼 수**: {len(self.m2_columns)}개")
        md_content.append(f"- **완전 일치 컬럼**: {exact_count}개")
        md_content.append(f"- **유사 컬럼**: {similar_count}개")
        md_content.append(f"- **총 매핑 가능 컬럼**: {exact_count + similar_count}개")
        
        # 완전 일치 컬럼
        if self.mapping_results['exact_matches']:
            md_content.append("\n## 🎯 완전 일치 컬럼")
            md_content.append("| M-1 엑셀ID | M-1 컬럼명 | M-1 타입 | M-1 결측값 | M-2 엑셀ID | M-2 컬럼명 | M-2 타입 | M-2 결측값 | 비고 |")
            md_content.append("|-----------|-----------|----------|------------|-----------|-----------|----------|------------|------|")
            
            for match in self.mapping_results['exact_matches']:
                md_content.append(f"| {match['m1_excel_id']} | `{match['m1_column']}` | {match['m1_type']} | {match['m1_missing']} | {match['m2_excel_id']} | `{match['m2_column']}` | {match['m2_type']} | {match['m2_missing']} | {match['notes']} |")
        
        # 유사 컬럼
        if self.mapping_results['similar_matches']:
            md_content.append("\n## 🔍 유사 컬럼 (유사도 0.7 이상)")
            md_content.append("| M-1 엑셀ID | M-1 컬럼명 | M-1 타입 | M-1 결측값 | M-2 엑셀ID | M-2 컬럼명 | M-2 타입 | M-2 결측값 | 유사도 |")
            md_content.append("|-----------|-----------|----------|------------|-----------|-----------|----------|------------|--------|")
            
            # 유사도 순으로 정렬
            sorted_matches = sorted(self.mapping_results['similar_matches'], 
                                  key=lambda x: x['similarity'], reverse=True)
            
            for match in sorted_matches:
                md_content.append(f"| {match['m1_excel_id']} | `{match['m1_column']}` | {match['m1_type']} | {match['m1_missing']} | {match['m2_excel_id']} | `{match['m2_column']}` | {match['m2_type']} | {match['m2_missing']} | {match['similarity']:.2f} |")
        
        # 주요 키 필드 분석
        if self.mapping_results['key_matches']:
            md_content.append("\n## 🔑 주요 키 필드 분석")
            
            for key_match in self.mapping_results['key_matches']:
                md_content.append(f"\n### {key_match['category']} 관련 필드")
                
                # M-1 필드
                if key_match['m1_fields']:
                    md_content.append("\n**M-1 신규 가입자 정보:**")
                    for field in key_match['m1_fields']:
                        md_content.append(f"- `{field['column']}` ({field['type']}) - 결측값: {field['missing']}")
                
                # M-2 필드
                if key_match['m2_fields']:
                    md_content.append("\n**M-2 정산내역:**")
                    for field in key_match['m2_fields']:
                        md_content.append(f"- `{field['column']}` ({field['type']}) - 결측값: {field['missing']}")
        
        # 매핑되지 않은 컬럼 분석
        md_content.append("\n## ❓ 매핑되지 않은 컬럼")
        
        # M-1에서 매핑되지 않은 컬럼
        mapped_m1_columns = set()
        for match in self.mapping_results['exact_matches']:
            mapped_m1_columns.add(match['m1_column'])
        for match in self.mapping_results['similar_matches']:
            mapped_m1_columns.add(match['m1_column'])
        
        unmapped_m1 = [col for col in self.m1_columns['컬럼명'] if col not in mapped_m1_columns]
        
        md_content.append(f"\n### M-1 전용 컬럼 ({len(unmapped_m1)}개)")
        for i, col in enumerate(unmapped_m1[:20], 1):  # 상위 20개만 표시
            md_content.append(f"{i}. `{col}`")
        if len(unmapped_m1) > 20:
            md_content.append(f"... 외 {len(unmapped_m1) - 20}개")
        
        # M-2에서 매핑되지 않은 컬럼
        mapped_m2_columns = set()
        for match in self.mapping_results['exact_matches']:
            mapped_m2_columns.add(match['m2_column'])
        for match in self.mapping_results['similar_matches']:
            mapped_m2_columns.add(match['m2_column'])
        
        unmapped_m2 = [col for col in self.m2_columns['컬럼명'] if col not in mapped_m2_columns]
        
        md_content.append(f"\n### M-2 전용 컬럼 ({len(unmapped_m2)}개)")
        for i, col in enumerate(unmapped_m2[:20], 1):  # 상위 20개만 표시
            md_content.append(f"{i}. `{col}`")
        if len(unmapped_m2) > 20:
            md_content.append(f"... 외 {len(unmapped_m2) - 20}개")
        
        # 요금제 정보와의 연결
        md_content.append("\n## 📋 요금제 정보 연결점")
        plan_col_names = self.plan_columns['컬럼명'].tolist()
        md_content.append("**요금제 정보 컬럼:**")
        for col in plan_col_names:
            md_content.append(f"- `{col}`")
        
        # 분석 권장사항
        md_content.append("\n## 💡 분석 권장사항")
        md_content.append("1. **완전 일치 컬럼**을 활용하여 M-1과 M-2 데이터 조인 가능")
        md_content.append("2. **가입번호** 기반으로 신규 가입자의 정산 내역 추적 가능")
        md_content.append("3. **요금제코드/명** 필드로 요금제 정보와 연결 분석 가능")
        md_content.append("4. **유사 컬럼**들은 데이터 정제 후 매핑 고려")
        md_content.append("5. **M-1 전용 컬럼**은 신규 가입 과정의 고유 정보")
        md_content.append("6. **M-2 전용 컬럼**은 정산 및 사용량 관련 상세 정보")
        
        # 파일에 저장
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_content))
            print(f"\n✅ 매핑 분석 보고서가 '{output_file}' 파일로 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ 보고서 저장 중 오류 발생: {str(e)}")

def main():
    """메인 실행 함수"""
    print("🔗 컬럼 매핑 분석 프로그램 시작")
    print("=" * 60)
    
    # 컬럼 매퍼 초기화
    mapper = ColumnMapper()
    
    # 컬럼 정보 로드
    if not mapper.load_column_info():
        return
    
    # 매핑 분석 수행
    if not mapper.analyze_mappings():
        return
    
    # 보고서 생성
    mapper.generate_mapping_report()
    
    print(f"\n🎉 컬럼 매핑 분석 완료!")

if __name__ == "__main__":
    main()