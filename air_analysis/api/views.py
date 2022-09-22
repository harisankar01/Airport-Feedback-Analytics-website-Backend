
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
    time_graph = coll.find(
        {"airport_name": "portland-airport"}, {"_id": 0, "airport_name": 1, "date": 1, "overall_rating": 1}).sort("date")
    time_details = []
    for i in time_graph:
        i["date"] = i["date"].strftime("%d %B, %Y")
        if i["overall_rating"] != "":
            time_details.append(i)
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
        if analise >= 0.5:
            pos += 1
        elif analise < -0.5:
            neg += 1
        else:
            neu += 1
    print("calue", pos, neg, neu)
    json_object = [
        {"name": "positive", "value": pos},
        {"name": "negative", "value": neg},
        {"name": "neutral", "value": neg},
    ]

    final_ob = {
        "sentiment": json_object,
        "time_analysis": time_details
    }
    return JsonResponse(final_ob, safe=False)
