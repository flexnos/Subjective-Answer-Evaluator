import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout, Concatenate
from sklearn.model_selection import train_test_split
import pickle
# ...existing code...

# Example labeled data: (reference_answer, student_answer, similarity_score 0-1)
data = [
    ("What is photosynthesis?", "Process by which plants make food", 1.0),
    ("Explain photosynthesis.", "It rains a lot", 0.1),
    ("Define photosynthesis.", "Sunlight helps plants make food", 0.9),
    # Add more pairs here
]

ref_texts = [x[0] for x in data]
stu_texts = [x[1] for x in data]
labels = np.array([x[2] for x in data])

all_texts = ref_texts + stu_texts

# Tokenizer and padding
tokenizer = Tokenizer(num_words=10000)
tokenizer.fit_on_texts(all_texts)

max_len = 100
ref_seqs = pad_sequences(tokenizer.texts_to_sequences(ref_texts), maxlen=max_len)
stu_seqs = pad_sequences(tokenizer.texts_to_sequences(stu_texts), maxlen=max_len)

X = np.concatenate([ref_seqs, stu_seqs], axis=1)
input_len = max_len * 2

# CNN Model
def build_cnn_model(vocab_size, embedding_dim, input_length):
    input_layer = Input(shape=(input_length,))
    embedding_layer = Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=input_length)(input_layer)

    convs = []
    for fsz in [3,4,5]:
        conv = Conv1D(filters=128, kernel_size=fsz, activation='relu')(embedding_layer)
        pool = GlobalMaxPooling1D()(conv)
        convs.append(pool)

    concat = Concatenate()(convs)
    dropout = Dropout(0.5)(concat)
    dense = Dense(64, activation='relu')(dropout)
    output = Dense(1, activation='sigmoid')(dense)  # Output similarity score [0,1]

    model = Model(inputs=input_layer, outputs=output)
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae'])
    return model

model = build_cnn_model(vocab_size=10000, embedding_dim=128, input_length=input_len)

X_train, X_val, y_train, y_val = train_test_split(X, labels, test_size=0.2, random_state=42)

model.fit(X_train, y_train, epochs=10, batch_size=16, validation_data=(X_val, y_val))

# Save model and tokenizer to disk
model.save("cnn_answer_evaluator.h5")

with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)
