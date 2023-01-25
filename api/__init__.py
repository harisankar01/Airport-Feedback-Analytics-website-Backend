# Install nltk packages into tmp folder of vercel server
import nltk
nltk.download("vader_lexicon", download_dir="/tmp")
nltk.download("punkt", download_dir="/tmp")
nltk.download("stopwords", download_dir="/tmp")
nltk.download("averaged_perceptron_tagger", download_dir="/tmp")
nltk.data.path.append("/tmp")
