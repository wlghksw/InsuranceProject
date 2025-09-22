import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# 1. 사전 훈련된 한국어 모델 불러오기
print("사전 훈련된 한국어 모델을 불러옵니다...")
model = SentenceTransformer('jhgan/ko-sroberta-multitask')

# 2. 우리가 만든 CSV 데이터 준비
print("'보험용어정리_new.csv' 파일을 읽어옵니다...")
df = pd.read_csv('보험용어정리_new.csv')

# AI가 학습할 수 있는 형태(질문-답변 쌍)로 데이터를 가공합니다.
train_examples = []
for index, row in df.iterrows():
    questions = str(row['분류']).split('|')
    answer = str(row['내용'])
    for question in questions:
        # --- 여기가 수정된 부분입니다! ---
        # 질문과 답변이 완벽한 짝이라는 의미로 label=1.0을 추가합니다.
        train_examples.append(InputExample(texts=[question, answer], label=1.0))

print(f"{len(train_examples)}개의 학습 예제를 생성했습니다.")

# 3. 학습 환경 설정
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)

# 학습 횟수(epoch) 4 -> 8
num_epochs = 10

# 4. 모델 학습 시작
print(f"{num_epochs} 에포크 동안 모델 학습을 시작합니다...")
model.fit(train_objectives=[(train_dataloader, train_loss)],
          epochs=num_epochs,
          warmup_steps=100,
          show_progress_bar=True)

# 5. 훈련된 모델 저장
print("학습된 모델을 'my_insurance_model' 폴더에 저장합니다...")
model.save('my_insurance_model')

print("\n🎉 모델 생성 및 저장이 완료되었습니다!")
print("이제 'python app.py'를 실행하여 챗봇 서버를 시작할 수 있습니다.")