FROM python:3.12

COPY requirements.txt .

RUN pip3 install --upgrade pip setuptools wheel

RUN pip3 install -r requirements.txt 

RUN python3 -m spacy download en_core_web_sm

COPY institutes.csv .

COPY extract.py .

COPY transform.py .

COPY load.py .

COPY etl.py .

CMD ["python3", "etl.py"]