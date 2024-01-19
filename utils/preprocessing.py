import re
import nltk
from nltk.corpus import stopwords
import string
import sys,fitz
import textract
from nltk.tokenize import word_tokenize
from itertools import chain
import re
# nltk.download('stopwords')

def textPreprocessor(featureRecord):
    #Remove punctuations
    removePunctuation = [char for char in featureRecord if char not in string.punctuation]
    sentences =''.join(removePunctuation)

    #convert sentences to words
    words = sentences.split(" ")

    #normalize
    wordNormalized=[word.lower() for word in words]

    #remove stropwords
    finalWords=[word for word in wordNormalized if word not in stopwords.words("english")]

    return finalWords

def cleanResume(fname):
    doc=fitz.open(fname)
    resumeText=""
    for page in doc:
      resumeText=resumeText+str(page.get_text())
    ' '.join(resumeText.split())
    resumeText = re.sub('http\S+\s*', ' ', resumeText)
    resumeText = re.sub('RT|cc', ' ', resumeText)
    resumeText = re.sub('#\S+', '', resumeText)
    resumeText = re.sub('@\S+', '  ', resumeText)
    resumeText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', resumeText)
    resumeText = re.sub(r'[^\x00-\x7f]',r' ', resumeText)
    resumeText = re.sub('\s+', ' ', resumeText)
    return resumeText



def Preprocessfile(filename):
  text = textract.process(filename)
  text= text.decode('utf-8').replace("\n", " ")
  # print(text)
  x=[]
  tokens=word_tokenize(text)
  tok=[w.lower() for w in tokens]
  table=str.maketrans('','',string.punctuation)
  strpp=[w.translate(table) for w in tok]
  words=[word for word in strpp if word.isalpha()]
  stop_words=set(stopwords.words('english'))
  words=[w for w in words if not w in stop_words]
  x.append(words)
  # print(x)
  res=" ".join(chain.from_iterable(x))
  return res

def cleanText(resumeText):
    resumeText = re.sub('http\S+\s*', ' ', resumeText)
    resumeText = re.sub('RT|cc', ' ', resumeText)
    resumeText = re.sub('#\S+', '', resumeText)
    resumeText = re.sub('@\S+', '  ', resumeText)
    resumeText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', resumeText)
    resumeText = re.sub(r'[^\x00-\x7f]',r' ', resumeText)
    resumeText = re.sub('\s+', ' ', resumeText)
    return resumeText