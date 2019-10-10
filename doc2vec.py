# -*- coding: utf-8 -*-
"""doc2vec.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RjrtBDnZTZ0CiOFXz32XJYSwjNaZ0aEm
"""

import pandas as pd  
import numpy as np
import matplotlib.pyplot as plt

train=pd.read_excel("clean_tweet_train.xlsx")
test=pd.read_excel("clean_tweet_test.xlsx")

Train = train.append(test, ignore_index=True).fillna(' ')

train.dropna(inplace=True)
train.reset_index(drop=True,inplace=True)
train.info()

test.dropna(inplace=True)
test.reset_index(drop=True,inplace=True)
test.info()

x_train=train.text
y_train=train.sentiment
x_test=test.text
y_test=test.sentiment

len(x_train)

len(x_test)

len(x_test)+len(x_train)

from tqdm import tqdm
tqdm.pandas(desc="progress-bar")
from gensim.models import Doc2Vec
from gensim.models.doc2vec import LabeledSentence
import multiprocessing
from sklearn import utils

#Gensim'in LabeledSentence fonksiyonunu kullanarak her bir Tweet'i unique bir Id ile etiketliyoruz
def labelize_tweets(tweets,label):
    result = []
    prefix = label
    for i, t in zip(tweets.index, tweets):
        result.append(LabeledSentence(t.split(), [prefix + '_%s' % i]))
    return result

#doc2vec eğitimi için bütün veri seti kullanıldı,unsupervised bir teknik olduğu için sadece x verileri
all_x = pd.concat([x_train,x_test])
all_x_w2v = labelize_tweets(all_x, 'all')

len(all_x_w2v)

#DBOW(distributed bag of words)Skip-gram model in word2vec
cores = multiprocessing.cpu_count()
model_dbow = Doc2Vec(dm=0, size=100, negative=6, min_count=2, workers=cores, alpha=0.065, min_alpha=0.065)
model_dbow.build_vocab([x for x in tqdm(all_x_w2v)])

"""%%time
#her iterasyon alpha değeri azalıyor
for epoch in range(30):
    model_dbow.train(utils.shuffle([x for x in tqdm(all_x_w2v)]), total_examples=len(all_x_w2v), epochs=1)
    model_dbow.alpha -= 0.002
    model_dbow.min_alpha = model_dbow.alpha
"""

#eğitilmiş doc2vec modelinden belge vektörlerini çıkarmak için 'get_vectors' 
def get_vectors(model, corpus, size):
    vecs = np.zeros((len(corpus), size))
    n = 0
    for i in corpus.index:
        prefix = 'all_' + str(i)
        vecs[n] = model.docvecs[prefix]
        n += 1
    return vecs

train_vecs_dbow = get_vectors(model_dbow, x_train, 100)
test_vecs_dbow = get_vectors(model_dbow, x_test, 100)

from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(solver='newton-cg')
clf.fit(train_vecs_dbow, y_train)

clf.score(test_vecs_dbow, y_test)

"""dbow modeli her kelimenin anlamını öğrenmez yukarıda da görüldüğü gibi başarısı count vectorizer ve tfidf vectorizer sonuçlarından daha düşük çıktı."""

model_dbow.save('d2v_model_dbow.doc2vec')

#DMC cbow model in word2vec-Cconcatenation kullanıldı dm_concat=1
model_dmc = Doc2Vec(dm=1, dm_concat=1, size=100, window=2, negative=5, min_count=2, workers=cores, alpha=0.065, min_alpha=0.065)
model_dmc.build_vocab([x for x in tqdm(all_x_w2v)])

"""%%time
for epoch in range(30):
    model_dmc.train(utils.shuffle([x for x in tqdm(all_x_w2v)]), total_examples=len(all_x_w2v), epochs=1)
    model_dmc.alpha -= 0.002
    model_dmc.min_alpha = model_dmc.alpha
"""

train_vecs_dmc = get_vectors(model_dmc, x_train, 100)
test_vecs_dmc = get_vectors(model_dmc, x_test, 100)

clf = LogisticRegression(solver='newton-cg')
clf.fit(train_vecs_dmc, y_train)

clf.score(test_vecs_dmc, y_test)

model_dmc.save('d2v_model_dmc.doc2vec')

"""yukarıda da görüldüğü gibi bu model içinde baarı düşük"""

#DMM DM_MEAN=1 distributed memory mean
model_dmm = Doc2Vec(dm=1, dm_mean=1, size=100, window=4, negative=5, min_count=2, workers=cores, alpha=0.065, min_alpha=0.065)
model_dmm.build_vocab([x for x in tqdm(all_x_w2v)])

"""%%time
for epoch in range(30):
    model_dmm.train(utils.shuffle([x for x in tqdm(all_x_w2v)]), total_examples=len(all_x_w2v), epochs=1)
    model_dmm.alpha -= 0.002
    model_dmm.min_alpha = model_dmm.alpha
"""

train_vecs_dmm = get_vectors(model_dmm, x_train, 100)
test_vecs_dmm = get_vectors(model_dmm, x_test, 100)

clf = LogisticRegression(solver='newton-cg')
clf.fit(train_vecs_dmm, y_train)

clf.score(test_vecs_dmm, y_test)

#modelleri birleştirerek başarının nasıl değiştiğini gözlemliyelim
def get_concat_vectors(model1,model2, corpus, size):
    vecs = np.zeros((len(corpus), size))
    n = 0
    for i in corpus.index:
        prefix = 'all_' + str(i)
        vecs[n] = np.append(model1.docvecs[prefix],model2.docvecs[prefix])
        n += 1
    return vecs

#dbow ile dmc birleştirildi
train_vecs_dbow_dmc = get_concat_vectors(model_dbow,model_dmc, x_train, 200)
test_vecs_dbow_dmc = get_concat_vectors(model_dbow,model_dmc, x_test, 200)

"""%%time
clf = LogisticRegression(solver='newton-cg')
clf.fit(train_vecs_dbow_dmc, y_train)
"""

clf.score(test_vecs_dbow_dmc, y_test)

train_vecs_dbow_dmm = get_concat_vectors(model_dbow,model_dmm, x_train, 200)
test_vecs_dbow_dmm = get_concat_vectors(model_dbow,model_dmm, x_test, 200)

"""%%time
clf = LogisticRegression(solver='newton-cg')
clf.fit(train_vecs_dbow_dmm, y_train)
"""

clf.score(test_vecs_dbow_dmm, y_test)