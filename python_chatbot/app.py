from flask import Flask, request, jsonify
import pandas as pd
import os

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# --- 딥러닝 모델 및 데이터 준비 ---
print("딥러닝 모델을 불러오는 중입니다...")

model_path = './my_insurance_model' # 훈련시킨 모델의 경로
model = SentenceTransformer(model_path)

print("모델 로딩 완료!")

basedir = os.path.dirname(os.path.abspath(__file__))
# create_csv.py로 생성된 새 파일을 읽도록 설정
csv_path = os.path.join(basedir, '보험용어정리_new.csv')
df = pd.read_csv(csv_path)

print("답변 데이터의 의미를 계산하는 중입니다...")

# '분류'와 '내용' 임베딩을 분리하여 생성
term_embeddings = model.encode(df['분류'].tolist())
content_embeddings = model.encode(df['내용'].tolist())

print("의미 계산 완료!")


# --- 챗봇 로직 ---
def chatbot(question):
    question_embedding = model.encode([question])

    # '용어'와 '설명' 유사도 각각 계산
    term_similarities = cosine_similarity(question_embedding, term_embeddings)
    content_similarities = cosine_similarity(question_embedding, content_embeddings)

    # 최종 가중치: 용어(80%), 설명(20%)으로 질문과 용어의 직접적인 연관성을 더 중요하게 판단
    combined_scores = (term_similarities * 0.8) + (content_similarities * 0.2)

    best_match_index = combined_scores.argmax()
    best_score = combined_scores[0, best_match_index]

    # 임계값(Threshold)
    if best_score > 0.6:
        best_match = df.iloc[best_match_index]
        return {"answer": f"{best_match['분류']} : {best_match['내용']}", "score": float(best_score)}
    else:
        return {"answer": "죄송합니다, 이해하지 못했습니다. 다시 질문해주세요", "score": float(best_score)}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_query = data.get("question", "")
    return jsonify(chatbot(user_query))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)