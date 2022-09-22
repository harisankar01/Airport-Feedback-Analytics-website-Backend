from operator import ne
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords, wordnet
from nltk import tokenize, pos_tag
import nltk
from re import I
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Airport_feedbacks
from .searializer import AirPort_serializer
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017')
db = client['Airport_review_analysis']
coll = db["airport_feedbacks"]
# from pymongo import Connection
# server = "localhost"
# port = 27017
# # Establish a connection with mongo instance.
# conn = Connection(server, port)


@api_view(['GET'])
def getRoutes(request):
    fields = coll.find({}).limit(20)
    # print(list(fields))
    # modell = Airport_feedbacks()
    # val = modell.objects.all()
    # for i in val:
    #     print(i)
    pos, neg, neu = 0, 0, 0
    seri = AirPort_serializer(fields, many=True)
    sid = SentimentIntensityAnalyzer()
    for i in seri.data:
        pred = sid.polarity_scores(i["content"])
        # for key in sorted(pred.keys()):
        #     print('{}: {}, '.format(key, pred[key]), end='')
        # print("/n")
        analise = pred["compound"]
        # max_key = max(pred, key=pred.get)
        if analise >= 0.5:
            pos += 1
        elif analise < -0.5:
            neg += 1
        else:
            neu += 1
    print("calue", pos, neg, neu)
    json_object = {
        "positive": pos,
        "negative": neg,
        "neutral": neu
    }
    return JsonResponse(json_object, safe=False)
# Create your views here.
