import pickle
import pathlib
pathlib.PosixPath = pathlib.WindowsPath
import sys
import fitz
import re 

def nlpParser(fname):
  doc=fitz.open(fname)
  text=""
  for page in doc:
    text=text+str(page.get_text())

  ' '.join(text.split())

  pkl_filename = 'spacy_ner_model.pkl'
  with open(pkl_filename,'rb') as file:
    model=pickle.load(file)

  doc=model(text)
  entity_dict={}
  email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
  skills=[]
  for ent in doc.ents:
    if ent.label_=="Skills" and ent.text not in skills:
      skills.append(ent.text)
    if ent.label_ == "Email Address":
      if re.search(email_pattern,ent.text):
        print(ent.text,"---->",ent.label_)
      else:
        print(ent.text,"---->","URL")
    else:
      print(ent.text,"---->",ent.label_)

  return skills
