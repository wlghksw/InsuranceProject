#!/usr/bin/env python3
"""
암보험 상품 추천 API 서버 실행 스크립트
"""

import uvicorn
import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    print("암보험 상품 추천 API 서버를 시작합니다...")
    print("데이터를 로딩 중입니다...")
    
    # app 디렉토리로 이동
    import os
    app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app")
    os.chdir(app_dir)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
