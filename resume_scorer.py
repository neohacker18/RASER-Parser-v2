import os
import re
import json
from utils import preprocessing 
import pickle

def skill_finder(text):
  pkl_filename = 'spacy_ner_model.pkl'
  with open(pkl_filename,'rb') as file:
    model=pickle.load(file)
  doc=model(text)
  doc=doc.ents
  skills=[]
  for ent in doc:
    label=ent.label_
    if label == "Skills" or label=="Designation" or label =="Degree":
      skills.append(ent.text)
  return list(set(skills))


def Score_Resumes(folder_path,jd_path):
    with open('./training/dataset/vocabulary.json', 'r') as f:
        loaded_vocabulary = json.load(f)
    
    vocabulary=loaded_vocabulary
    
    input_jd=preprocessing.cleanResume(jd_path)
    input_jd=skill_finder(input_jd)

    improved_input_jd=[]
    for i in range(len(input_jd)):
        items_in_text=preprocessing.textPreprocessor(input_jd[i])
        for item in items_in_text:
            improved_input_jd.append(item)

    jd_skills=list(set(improved_input_jd))
    req_skills_len = len(jd_skills)


    score_list={}
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            continue
        
        input_resume=preprocessing.cleanResume(item_path)
        input_resume=skill_finder(input_resume)

        improved_input_resume=[]

        for i in range(len(input_resume)):
            items_in_text=preprocessing.textPreprocessor(input_resume[i])
            for _item in items_in_text:
                improved_input_resume.append(_item)

        resume_skills=list(set(improved_input_resume))

        total_score=0
        checked_skills=[]

        for x in jd_skills:
            if x in resume_skills:
                checked_skills.append(x)
                if x in vocabulary:
                    total_score += max(vocabulary[x]*10,2.5)
                else:
                    total_score += 2.5

        checked_skills=list(set(checked_skills))
        for x in resume_skills:
            if x not in checked_skills:
                if x in vocabulary:
                    total_score += max(vocabulary[x],0.25)
                else:
                    total_score += 0.25

        if req_skills_len==0:
            req_skills_len=1
        match = round(total_score / req_skills_len * 100, 1)
        score_list[item]=match

    scores=[]
    id_counter=1
    for item in score_list:
        match=score_list[item]
        filename=item
        name = re.match(r'^([^0-9]+)', filename).group(1)
        dms=match
        sss=0
        ts=match
        scores.append({"id": id_counter, "name": name, "dms": dms, "sss": sss, "ts": ts})
        id_counter+=1
    
    return scores
