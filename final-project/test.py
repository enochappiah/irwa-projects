from sklearn.datasets import fetch_20newsgroups
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestCentroid
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


def loadData(X_train, X_test,MAX_NB_WORDS=75000):
    vectorizer_x = TfidfVectorizer(max_features=MAX_NB_WORDS)
    X_train = vectorizer_x.fit_transform(X_train).toarray()
    X_test = vectorizer_x.transform(X_test).toarray()
    print("tf-idf with",str(np.array(X_train).shape[1]),"features")
    return (X_train,X_test)


newsgroups_train = fetch_20newsgroups(subset='train')
newsgroups_test = fetch_20newsgroups()
print(len(list(newsgroups_test.target_names)))
X_train = newsgroups_train.data
X_test = newsgroups_test.data
y_train = newsgroups_train.target
y_test = newsgroups_test.target

'''arr = y_train[0]
print(arr, '\n\n\n\n')
print(y_train[1], '\n')
print(y_train[:2])'''

#X_train, X_test = loadData(X_train, X_test)
#y_train, y_test = loadData(y_train, y_test)


text_clf = Pipeline([('vect', CountVectorizer()),
                     ('tfidf', TfidfTransformer()),
                     ('clf', NearestCentroid()),
                     ])

text_clf.fit(X_train, y_train)


predicted = text_clf.predict(X_test)

print(metrics.classification_report(y_test, predicted))
'''
# halved the dataset for testing purposes
y_train = y_train[:len(y_train)//2]
y_test = y_train[len(y_train)//2:]

def TFIDF(X_train, X_test, size):
    vectorizer_x = TfidfVectorizer(max_features=size)
    X_train = vectorizer_x.fit_transform(X_train).toarray()
    X_test = vectorizer_x.transform(X_test).toarray()
    print("tf-idf with", str(np.array(X_train).shape[1]), "features")
    return (X_train, X_test)

X_train, X_test = TFIDF(X_train, X_test, size)

print("LENGTH OF X_TRAIN:",len(X_train))
print("LENGTH OF X_TEST:",len(X_test))
print("LENGTH OF Y_TRAIN:",len(y_train))
print("LENGTH OF Y_TEST:",len(y_test))

print("X_TRAIN SHAPE:",np.array(X_train).shape)
print("X_TEST SHAPE:",np.array(X_test).shape)
print("Y_TRAIN SHAPE:",np.array(y_train).shape)
print("Y_TEST SHAPE:",np.array(y_test).shape)'''
