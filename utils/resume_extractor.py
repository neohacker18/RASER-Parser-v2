import gdown
import pandas as pd

def get_pdf_links(file_path):
  df = pd.read_excel(file_path)

  key_value_pairs_2d = []

  for index, row in df.iterrows():
      first = row['First Name']
      second = row['Last Name']
      link = row['PDF Links']

      key_value_pair = [f"{first.replace(' ', '_')}_{second}", link]
      key_value_pairs_2d.append(key_value_pair)


  pdf_links=key_value_pairs_2d
  return pdf_links


def downloadResumes(name,google_drive_url,file_no):
  file_id = google_drive_url.split('/')[-2]

  output_path = f"./test/resume_data/{name}{file_no}.pdf"

  gdown.download(f"https://drive.google.com/uc?id={file_id}", output_path, quiet=False)

  print(f"Downloaded {output_path}")


def process_pdfs(file_path='./resumes.xlsx'):
  pdf_links=get_pdf_links(file_path)
  print(pdf_links)
  for i in range(len(pdf_links)):
    downloadResumes(pdf_links[i][0],pdf_links[i][1],i+1)