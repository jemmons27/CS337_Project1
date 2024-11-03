# CS337_Project1:
Python version =-3.12.3

GITHUB REPO: https://github.com/jemmons27/CS337_Project1

Instructions for setup: All necessary packages are in requirements.txt. Create a virtual environment using venv or conda and
run 'pip install -r requirements.txt'

To run the code run gg_api.py, which accesses and runs main.py


The code in gg_api uses a year variable multiple times, which corresponds to the year of the award ceremony
When initially fetching data from the json, the code looks for a file called 'gg' + year + '.json', so please
format the dataset files the same way. 

This year variable MUST be manually changed in gg_api.main and gg_api.pre_ceremony
Alternatively, one can comment out the hardcoded year and uncomment the input lines.



Libraries Included: 
annotated-types==0.7.0
blis==1.0.1
catalogue==2.0.10
certifi==2024.8.30
charset-normalizer==3.4.0
click==8.1.7
cloudpathlib==0.20.0
colorama==0.4.6
confection==0.1.5
cymem==2.0.8
en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl#sha256=1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85
ftfy==6.3.1
fuzzywuzzy==0.18.0
idna==3.10
Jinja2==3.1.4
joblib==1.4.2
langcodes==3.4.1
langdetect==1.0.9
language_data==1.2.0
Levenshtein==0.26.1
marisa-trie==1.2.1
markdown-it-py==3.0.0
MarkupSafe==3.0.2
mdurl==0.1.2
murmurhash==1.0.10
nltk==3.9.1
numpy==2.0.2
packaging==24.1
pandas==2.2.3
preshed==3.0.9
pydantic==2.9.2
pydantic_core==2.23.4
Pygments==2.18.0
python-dateutil==2.9.0.post0
python-Levenshtein==0.26.1
pytz==2024.2
RapidFuzz==3.10.1
regex==2024.9.11
requests==2.32.3
rich==13.9.3
setuptools==75.3.0
shellingham==1.5.4
six==1.16.0
smart-open==7.0.5
spacy==3.8.2
spacy-legacy==3.0.12
spacy-loggers==1.0.5
srsly==2.4.8
textblob==0.18.0.post0
thinc==8.3.2
tqdm==4.66.6
typer==0.12.5
typing_extensions==4.12.2
tzdata==2024.2
Unidecode==1.3.8
urllib3==2.2.3
wasabi==1.1.3
wcwidth==0.2.13
weasel==0.4.1
wordninja==2.0.0
wrapt==1.16.0

