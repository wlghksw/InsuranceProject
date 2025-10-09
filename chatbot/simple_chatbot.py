from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

print("보험 챗봇 데이터를 불러오는 중입니다...")

basedir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(basedir, '보험용어정리_new.csv')
df = pd.read_csv(csv_path)

print("데이터 로딩 완료!")

# 간단한 키워드 매칭 챗봇
def chatbot(question):
    question_lower = question.lower().strip()
    
    best_match = None
    best_score = 0
    
    for idx, row in df.iterrows():
        keywords = str(row['분류']).lower().split('|')
        
        # 질문에 키워드가 포함되어 있는지 확인
        for keyword in keywords:
            keyword = keyword.strip()
            
            # 정확히 일치하는 경우 최우선
            if keyword == question_lower:
                return {"answer": f"{row['분류']} : {row['내용']}", "score": 1.0}
            
            # 키워드가 질문에 포함되어 있는 경우
            if keyword in question_lower:
                score = 0.8
                if score > best_score:
                    best_score = score
                    best_match = row
            
            # 질문이 키워드에 포함되어 있는 경우
            elif question_lower in keyword:
                score = 0.7
                if score > best_score:
                    best_score = score
                    best_match = row
    
    if best_match is not None and best_score > 0.5:
        answer = f"{best_match['내용']}"
        return {"answer": answer, "score": float(best_score)}
    else:
        return {"answer": "죄송합니다, 이해하지 못했습니다. 보험, 보험료, 특약, 갱신 등의 용어를 물어보세요.", "score": 0.0}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_query = data.get("question", "")
    return jsonify(chatbot(user_query))

if __name__ == "__main__":
    print("챗봇 서버를 시작합니다...")
    app.run(host='0.0.0.0', port=5001, debug=False)

