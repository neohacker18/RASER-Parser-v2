import spacy
import pickle
from utils import preprocessing 
from sentence_transformers import SentenceTransformer, util

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

def calculate_semantic_similarity_score(model,resume, semantic_analysis_jd_sentences,job_description_embeddings):
  
  resume_=preprocessing.TextPreprocessor(resume)
  resume_sentences=resume_.split(".")

  for i in range(len(resume_sentences)):
    sentence_text=""
    items=preprocessing.textPreprocessor(resume_sentences[i])
    for item in items:
      sentence_text += item+" "
    resume_sentences[i]=sentence_text

  resume_skills=skill_finder(preprocessing.cleanResume(resume))

  improved_input_resume=[]
  for i in range(len(resume_skills)):
    items_in_text=preprocessing.textPreprocessor(resume_skills[i])
    for item in items_in_text:
      improved_input_resume.append(item)

  improved_input_resume=list(set(improved_input_resume))

  visited_resume_sentences=[]
  for x in improved_input_resume:
    for sentence in resume_sentences:
      if x in sentence and sentence not in visited_resume_sentences:
        visited_resume_sentences.append(sentence)
        break

  semantic_analysis_resume_sentences=[]
  for i in range(len(visited_resume_sentences)):
    sentence_text=preprocessing.cleanText(visited_resume_sentences[i])
    visited_resume_sentences[i]=sentence_text

  semantic_analysis_resume_sentences=visited_resume_sentences

  if(len(semantic_analysis_resume_sentences)==0 or len(semantic_analysis_jd_sentences)==0):
    return 0

  resume_embeddings = model.encode(semantic_analysis_resume_sentences, convert_to_tensor=True)

  cosine_similarities = util.pytorch_cos_sim(resume_embeddings, job_description_embeddings)

  similarity_scores=[]
  for i, resume_sentence in enumerate(semantic_analysis_resume_sentences):
    scores_for_resume=[]
    for j, jd_sentence in enumerate(semantic_analysis_jd_sentences):
      similarity_score = cosine_similarities[i][j].item()
      scores_for_resume.append(similarity_score)
    similarity_scores.append(scores_for_resume)

  total_score = sum([max(scores) for scores in similarity_scores])
  return total_score