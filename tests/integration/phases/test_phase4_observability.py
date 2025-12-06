#!/usr/bin/env python3
"""Test script for Phase 4: Observability Foundation"""
import sys
from src.company_researcher.workflows.parallel_agent_research import research_company

def main():
    if len(sys.argv) < 2:
        print('Usage: python test_phase4.py <company_name>')
        sys.exit(1)
    
    company_name = ' '.join(sys.argv[1:])
    print('Testing Phase 4 with company:', company_name)
    
    try:
        result = research_company(company_name)
        print('SUCCESS - Quality:', result['metrics']['quality_score'])
        print('Report:', result['report_path'])
    except Exception as e:
        print('FAILED:', e)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
