# Update pip
python3.9 -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

## Specify path
echo "export NLTK_DATA=./temp/nltk_data" >> ~/.bashrc

# Collect Static Files on Deploy
python3.9 manage.py collectstatic