# -*- coding: utf-8 -*-
"""lstm_word2vec_kernel_size=2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xzN2-zJm2QtxLhlejtqdz6rMESlv3r7K
"""

import pandas as pd  
import numpy as np
import matplotlib.pyplot as plt

#train ve test verilerini train ve test olarak okuduk
train=pd.read_excel("clean_tweet_train.xlsx")
test=pd.read_excel("clean_tweet_test.xlsx")

corpus = train.append(test, ignore_index=True).fillna(' ')

test.dropna(inplace=True)
test.reset_index(drop=True,inplace=True)

train.dropna(inplace=True)
train.reset_index(drop=True,inplace=True)

x_train=train.text
y_train=train.sentiment
x_test=test.text
y_test=test.sentiment

from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.layers import Embedding
from keras.layers import Conv1D, GlobalMaxPooling1D

from tqdm import tqdm
tqdm.pandas(desc="progress-bar")
import gensim
from gensim.models.word2vec import Word2Vec
from gensim.models.doc2vec import TaggedDocument
import multiprocessing
from sklearn import utils

def labelize_tweets_ug(tweets,label):
    result = []
    prefix = label
    for i, t in zip(tweets.index, tweets):
        result.append(TaggedDocument(t.split(), [prefix + '_%s' % i]))
    return result

#bütün tweet verilerini topladık -train-test ve validationda olan textler toplandı
all_x = pd.concat([x_train,x_test])
all_x_w2v = labelize_tweets_ug(all_x, 'all')

#tweet kelimelerine word2vec cbow yöntemi(sg=0) uygulanıyor-window_size=2
cores = multiprocessing.cpu_count()
model_ug_cbow = Word2Vec(sg=0, size=100, negative=5, window=2, min_count=2, workers=cores, alpha=0.065, min_alpha=0.065)
model_ug_cbow.build_vocab([x.words for x in tqdm(all_x_w2v)])

for epoch in range(30):
    model_ug_cbow.train(utils.shuffle([x.words for x in tqdm(all_x_w2v)]), total_examples=len(all_x_w2v), epochs=1)
    model_ug_cbow.alpha -= 0.002
    model_ug_cbow.min_alpha = model_ug_cbow.alpha

#daha sonra skip-gram modeli 
model_sg = Word2Vec(sg=1, size=100, negative=5, window=2, min_count=2, workers=cores, alpha=0.065, min_alpha=0.065)
model_sg.build_vocab([x.words for x in tqdm(all_x_w2v)])

"""%%time
#kelime vektörlerinin elde edilemesi için skip-gram modeli kullanılıyor
for epoch in range(30):
    model_sg.train(utils.shuffle([x.words for x in tqdm(all_x_w2v)]), total_examples=len(all_x_w2v), epochs=1)
    model_sg.alpha -= 0.002
    model_sg.min_alpha = model_sg.alpha
"""

#bu iki yöntemi birleştirdik
embeddings_index = {}
for w in model_ug_cbow.wv.vocab.keys():
    embeddings_index[w] = np.append(model_ug_cbow.wv[w],model_sg.wv[w])
print('Word vektör sayısı:' , len(embeddings_index))

from keras.preprocessing import sequence
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer

tokenizer = Tokenizer(num_words=10000)
tokenizer.fit_on_texts(x_train)

sequences = tokenizer.texts_to_sequences(x_train)
x_train_seq = pad_sequences(sequences, maxlen=35)

sequences_test = tokenizer.texts_to_sequences(x_test)
x_test_seq = pad_sequences(sequences_test, maxlen=35)

from keras import utils as np_utils
y_test = np_utils.to_categorical(y_test, num_classes= 3)
y_train = np_utils.to_categorical(y_train, num_classes= 3)

#elde ettiğimix-z kelime vektörlerinden bir matrix oluşturuyoruz ,embedding layer
#için num_words ile training için kullanacağımız most frequent word sayısı belirlendi
#200 ise embedding_dimension 
num_words = 10000
embedding_matrix = np.zeros((num_words, 200))
for word, i in tokenizer.word_index.items():
    if i >= num_words:
        continue
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        embedding_matrix[i] = embedding_vector

print(x_train_seq.shape)
print(y_train.shape)
print(x_test_seq.shape)
print(y_test.shape)

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.layers.embeddings import Embedding

embedding_vecor_length = 200
model = Sequential()
model.add(Embedding(10000, embedding_vecor_length, input_length=35))
model.add(Dropout(0.2))
model.add(Conv1D(filters=32, kernel_size=2, padding='same', activation='relu'))
model.add(MaxPooling1D(pool_size=2))
model.add(LSTM(100))
model.add(Dense(3, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())
model.fit(x_train_seq, y_train, epochs=10, batch_size=64)
scores = model.evaluate(x_test_seq, y_test, verbose=0)
print("Accuracy: %.2f%%" % (scores[1]*100))

embedding_vecor_length = 200
model = Sequential()
model.add(Embedding(10000, embedding_vecor_length,weights=[embedding_matrix], input_length=35,trainable=False))
model.add(Dropout(0.2))
model.add(Conv1D(filters=32, kernel_size=2, padding='same', activation='relu'))
model.add(MaxPooling1D(pool_size=2))
model.add(LSTM(100))
model.add(Dense(3, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())
model.fit(x_train_seq, y_train, epochs=10, batch_size=64)
scores = model.evaluate(x_test_seq, y_test, verbose=0)
print("Accuracy: %.2f%%" % (scores[1]*100))

embedding_vecor_length = 200
model = Sequential()
model.add(Embedding(10000, embedding_vecor_length,weights=[embedding_matrix], input_length=35,trainable=True))
model.add(Dropout(0.2))
model.add(Conv1D(filters=32, kernel_size=2, padding='same', activation='relu'))
model.add(MaxPooling1D(pool_size=2))
model.add(LSTM(100))
model.add(Dense(3, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())
model.fit(x_train_seq, y_train, epochs=10, batch_size=64)
scores = model.evaluate(x_test_seq, y_test, verbose=0)
print("Accuracy: %.2f%%" % (scores[1]*100))