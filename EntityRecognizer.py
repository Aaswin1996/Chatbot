import pandas as pd
import nltk
nltk.download('stopwords')


import string
import entity_check1

from nltk.corpus import stopwords
stopwords = stopwords.words('english')
print(stopwords)
df = pd.read_csv('Book1.csv')
#ab=pd.read_csv('response.csv')
# print(df.head())
#print(df.shape)

from sklearn.model_selection import train_test_split
train, test = train_test_split(df, test_size=0.33, random_state=42)


import spacy

nlp = spacy.load('en_core_web_sm')
#print(nlp)
punctuations = string.punctuation
def cleanup_text(docs, logging=False):
    texts = []
    counter = 1
    for doc in docs:
        #print(doc)
        if counter % 1000 == 0 and logging:
            print("Processed %d out of %d documents." % (counter, len(docs)))
        counter += 1
        doc = nlp(doc)
        #print(doc)
        tokens = [tok.lemma_.lower().strip() for tok in doc if tok.lemma_ != '-PRON-']
        tokens = [tok for tok in tokens if tok not in stopwords and tok not in punctuations]
        tokens = ' '.join(tokens)
        texts.append(tokens)
    return pd.Series(texts)



from sklearn.feature_extraction.text import CountVectorizer
from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.metrics import accuracy_score
from nltk.corpus import stopwords
import string
import re
import spacy
spacy.load('en_core_web_sm')
from spacy.lang.en import English
parser = English()

STOPLIST = set(stopwords.words('english') + list(ENGLISH_STOP_WORDS))
SYMBOLS = " ".join(string.punctuation).split(" ") + ["-", "...", "”", "”"]




class CleanTextTransformer(TransformerMixin):
    def transform(self, X, **transform_params):
        return [cleanText(text) for text in X]

    def fit(self, X, y=None, **fit_params):
        return self

    def get_params(self, deep=True):
        return {}


def cleanText(text):
    text = text.strip().replace("\n", " ").replace("\r", " ")
    text = text.lower()
    return text


def tokenizeText(sample):
    tokens = parser(sample)
    lemmas = []
    for tok in tokens:
        lemmas.append(tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_)
    tokens = lemmas
    tokens = [tok for tok in tokens if tok not in STOPLIST]
    tokens = [tok for tok in tokens if tok not in SYMBOLS]
    return tokens

def printNMostInformative(vectorizer, clf, N):
    feature_names = vectorizer.get_feature_names()
    coefs_with_fns = sorted(zip(clf.coef_[0], feature_names))
    topClass1 = coefs_with_fns[:N]
    topClass2 = coefs_with_fns[:-(N + 1):-1]



def model_train():


    vectorizer = CountVectorizer(tokenizer=tokenizeText, ngram_range=(1,1))
    clf = LinearSVC()
    pipe = Pipeline([('cleanText', CleanTextTransformer()), ('vectorizer', vectorizer), ('clf', clf)])

    # data
    train1 = train['Sentence'].tolist()
    labelsTrain1 = train['Class'].tolist()
    pipe.fit(train1,labelsTrain1)
    return pipe

def test_model(sentence,pipe):

    test1 = [sentence]

    preds = pipe.predict(test1)


    return preds


if __name__=='__main__':

    sentence=input("enter your query \n")
    pipe=model_train()
    response=test_model(sentence,pipe)
    print(response)
    out=entity_check1.information_retrieval(sentence, "$")
    out['output'][0]['intent']=str(response[0])
    print (out)
    num_entity=len(out['output'][0]['entities'])
    entityList=[]

    for entityIndex in range(num_entity):

        out1=out['output'][0]['entities'][entityIndex]['entity']
        print(out1)
        entityList.append(out1)

    print (entityList)

    dataset = pd.read_csv("response.csv")
    #dataset1 = pd.read_csv("test.csv")
    #print(len(dataset))

    dataset.shape


    #print(dataset['Entity'], entityList)
    #testing=dataset.loc[(dataset['Intent']==response[0]) & (dataset['Entity']==entityList)]

    #print(dataset.loc['Response'])
    X = dataset.drop('Response', axis=1)
    X = X.drop('Usecase',axis=1)

    #print (X)


    y = dataset['Response']





    train4=X.values.tolist()
    train5=y.values.tolist()
    #print (train4)
    #print(a)

    #
    #==============================================================================
    for i,c in enumerate(train4):
        #print("check")
        #print(";".join(entityList), c[1], entityList[0])
        value=";".join(entityList)
        value=value.lower()
        C=c[1].lower()
        if(value==C):
            print("reponse =",end=" ")
            print(train5[i])

    #
    #==============================================================================
    #print("accuracy:", accuracy_score(labelsTest1, preds))


