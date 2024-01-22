import os
import re
import json
from utils import preprocessing 
import pickle
from sentence_transformers import SentenceTransformer, util
from semantic_scorer import calculate_semantic_similarity_score

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
  resumes=[]
  jd=[]
  jd.append(jd_path)
  for resume_file in os.listdir(folder_path):
     if resume_file.endswith(".pdf"):
        resume_path=os.path.join(folder_path,resume_file)
        file_name=resume_path.split("\\")
        resumes.append(f"./test/resume_data/{file_name[1]}")

  print(resumes)
  return total_score_calculator(resumes,jd)

def calculate_structured_information_score(resume, jd_skills):
  with open('./training/dataset/vocabulary.json', 'r') as f:
        loaded_vocabulary = json.load(f)
        
  vocabulary=loaded_vocabulary
  resume=preprocessing.cleanResume(resume)
  resume_skills=skill_finder(resume)

  improved_input_resume=[]
  for i in range(len(resume_skills)):
    items_in_text=preprocessing.textPreprocessor(resume_skills[i])
    for item in items_in_text:
      improved_input_resume.append(item)

  resume_skills=improved_input_resume
  improved_input_resume=list(set(improved_input_resume))

  total_score = 0

  for x in jd_skills:
    if x in resume_skills:
      if x in vocabulary:
        total_score += 1*(vocabulary[x]*10)
      else:
        #average of min-max in vocabulary
        total_score += 1*(0.25)
  return total_score


def total_score_calculator(resumes,job_descriptions):
   combined_scores = []
   
   jd=preprocessing.TextPreprocessor(job_descriptions[0])
   jd_sentences=jd.split(".")
   
   for i in range(len(jd_sentences)):
    sentence_text=""
    items=preprocessing.textPreprocessor(jd_sentences[i])
    for item in items:
        sentence_text += item+" "
    jd_sentences[i]=sentence_text

    jd_skills=skill_finder(preprocessing.cleanResume(job_descriptions[0]))

    improved_input_jd=[]
    for i in range(len(jd_skills)):
        items_in_text=preprocessing.textPreprocessor(jd_skills[i])
        for item in items_in_text:
            improved_input_jd.append(item)

    improved_input_jd=list(set(improved_input_jd))
    visited_jd_sentences=[]
    for x in improved_input_jd:
        for sentence in jd_sentences:
            if x in sentence and sentence not in visited_jd_sentences:
                visited_jd_sentences.append(sentence)
                break

    semantic_analysis_jd_sentences=[]
    for i in range(len(visited_jd_sentences)):
        sentence_text=preprocessing.cleanText(visited_jd_sentences[i])
        visited_jd_sentences[i]=sentence_text

    semantic_analysis_jd_sentences=visited_jd_sentences
    model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
    job_description_embeddings = model.encode(semantic_analysis_jd_sentences, convert_to_tensor=True)

    score1={}
    score2={}
    id_counter=1
    for resume in resumes:
        structured_information_score = calculate_structured_information_score(resume, improved_input_jd)
        score1[resume]=structured_information_score
        semantic_similarity_score = calculate_semantic_similarity_score(model,resume,semantic_analysis_jd_sentences,job_description_embeddings)
        score2[resume]=semantic_similarity_score
        combined_score = structured_information_score * 0.4 + semantic_similarity_score * 0.6
        combined_scores.append(
            {"id": id_counter, "name": resume.split("/")[3], "dms": structured_information_score, "sss": semantic_similarity_score, "ts": combined_score}
        )
        id_counter += 1

    return combined_scores