# Update pip
python3.9 -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

chmod -R 777 /home/sbx_user1051/nltk_data
# Collect Static Files on Deploy
python3.9 manage.py collectstatic