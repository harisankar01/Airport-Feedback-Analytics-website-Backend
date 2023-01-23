# Update pip
python3.9 -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install NLTK Packages
python3.9 -c "import nltk; nltk.download('vader_lexicon')"

# Collect Static Files on Deploy
python3.9 manage.py collectstatic