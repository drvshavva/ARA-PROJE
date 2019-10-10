# -*- coding: utf-8 -*-
"""karakter_tabanlı_klasik_3gram_tfidf.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zLLLu2MneJtixsdkMoi-VuAFeyWHKdJq
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import xgboost 
from sklearn import model_selection, preprocessing, linear_model, naive_bayes, metrics, svm
from sklearn import decomposition, ensemble

"""BU PROGRAMDA KARAKTER TABANLI 3-GRAM tf-ıdf VECTORIZER ICIN KLASİK YÖNTEMLERİN BAŞARI SONUÇLARI ELDE EDİLMİŞTİR"""

#train ve test verilerini train ve test olarak okuduk

train=pd.read_excel("clean_tweet_train.xlsx")
test=pd.read_excel("clean_tweet_test.xlsx")

Train = train.append(test, ignore_index=True).fillna(' ')

train.dropna(inplace=True)
train.reset_index(drop=True,inplace=True)
train.info()

test.dropna(inplace=True)
test.reset_index(drop=True,inplace=True)
test.info()

x_train=train.text.tolist()
y_train=train.sentiment.tolist()
x_test=test.text.tolist()
y_test=test.sentiment.tolist()

tfidf = TfidfVectorizer(analyzer='char', ngram_range=(1,3))
tfidf.fit(train['text'])
xtrain_tfidf =  tfidf.transform(x_train)
xtest_tfidf =  tfidf.transform(x_test)

def model_training(classifier, vector_train, y_train, vector_test):
    classifier.fit(vector_train, y_train)
    predictions = classifier.predict(vector_test)
   
    
    return metrics.accuracy_score(predictions, y_test)

# Naive Bayes 
accuracy = model_training(naive_bayes.MultinomialNB(), xtrain_tfidf,  y_train, xtest_tfidf )
print ("NB, karakter tabanlı tfidf:% ", accuracy*100)

# Logistic Regression
accuracy = model_training(linear_model.LogisticRegression(solver='saga',multi_class='multinomial'), xtrain_tfidf,  y_train, xtest_tfidf)
print ("LR, karakter tabanlı TF-IDF:%", accuracy*100)

# SVM 
accuracy =  model_training(svm.SVC(kernel='linear'), xtrain_tfidf, y_train,  xtest_tfidf)
print ("SVM,  karakter tabanlı TF-IDF::%", accuracy*100)

# Random forest
accuracy =   model_training(ensemble.RandomForestClassifier(n_estimators=100), xtrain_tfidf, y_train, xtest_tfidf)
print ("RF, karakter tabanlı TF-IDF:% ", accuracy*100)

# Extereme Gradient Boosting 
accuracy = model_training(xgboost.XGBClassifier(booster='gblinear'), xtrain_tfidf.tocsc(), y_train, xtest_tfidf.tocsc())
print ("Xgb, karakter tabanlı TF-IDF:% ", accuracy*100)