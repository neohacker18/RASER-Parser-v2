from flask import Flask, request, redirect
from flask_restful import Resource, Api
from flask_cors import CORS
import os
import parser_1
import resume_scorer
from utils import resume_extractor
import re
import firebase_admin
import asyncio
import requests
from firebase_admin import credentials
import asyncio
import time


cred = credentials.Certificate(r'C:\Users\Aryan Sethi\AppData\Roaming\gcloud\raser-backend-3fdaade544f1.json')  
firebase_admin.initialize_app(cred,{"storageBucket":"raser-backend.appspot.com/raserDocs"})

from firebase_admin import storage


app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)

class Test(Resource):
    def get(self):
        return 'Welcome to, Test App API!'

    def post(self):
        try:
            value = request.get_json()
            if(value):
                return {'Post Values': value}, 201

            return {"error":"Invalid format."}

        except Exception as error:
            return {'error': error}

class GetParsedOutput(Resource):
    def get(self):
        return {"error": "Invalid Method."}

    def post(self):
        try:
            if 'file' not in request.files:
                return {"error": "No file received."}

            file = request.files['file']

            if file and file.filename.endswith('.pdf'):
                uploaded_file_path = os.path.join("uploads", file.filename)
                file.save(uploaded_file_path)

                output = parser_1.nlpParser(uploaded_file_path)
                return {"Skills": output}, 201

            return {"error": "Invalid file format. Please upload a PDF file."}

        except FileNotFoundError as error:
            return {'error': f'File not found: {error.filename}'}, 404  

        except Exception as error:
            return {'error': str(error)}, 500  
        
class GetRankedResumes(Resource):
    def get(self):
        return {"error": "Invalid Method."}
    
    def download_file(self,url, filename):
        response = requests.get(url, stream=True)
        response.raise_for_status()  

        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    def process_resume(self):
        resume_extractor.process_pdfs("./test/excel/resumes.xlsx")
        res = resume_scorer.Score_Resumes("./test/resume_data","./test/cv_data/jd.pdf")
        # test=[{"id": 4, "name": "Tushar_Jha4.pdf", "dms": 117.9, "sss": 117.9, "ts": 16.5}, {"id": 1, "name": "Aryan__Sethi1.pdf", "dms": 117.9, "sss": 101.8, "ts": 14.25}, {"id": 3, "name": "Nayra_Sethi2.pdf", "dms": 117.9, "sss": 100.0, "ts": 14.0}, {"id": 2, "name": "Gunika_Dhingra3.pdf", "dms": 117.9, "sss": 80.4, "ts": 11.25}]
        return res

    def post(self):
        try:
            data=request.get_json()
            excelUrl=f'https://firebasestorage.googleapis.com/v0/b/raser-backend.appspot.com/o/raserDocs%2F{data.get("excelUrl")}?alt=media&token={data.get("excelToken")}'
            jdUrl=f'https://firebasestorage.googleapis.com/v0/b/raser-backend.appspot.com/o/raserDocs%2F{data.get("jdUrl")}?alt=media&token={data.get("jdToken")}'

            excel_file_path=r'test/excel/resumes.xlsx'
            jd_file_path=r'test/cv_data/jd.pdf'
            print(excelUrl)

            self.download_file(excelUrl,excel_file_path)
            self.download_file(jdUrl,jd_file_path)

            # return self.process_resume(),201
        
            folder_path="./test/resume_data"
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                for item in os.listdir(folder_path):
                    item_path=os.path.join(folder_path,item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)

                
                res=self.process_resume()
                return res,201
                # return res,201
                # # sorted_score_list = dict(sorted(res.items(), key=lambda item: item[1], reverse=True))
                # if res:
                #     return res, 201
                # else:
                #     return {"error": "Something went wrong"}

        except Exception as error:
            return {'error': str(error)}, 500  

api.add_resource(Test,'/')
api.add_resource(GetParsedOutput,'/getOutput')
api.add_resource(GetRankedResumes,'/getRankedResumes')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 