import math as pd
from nltk.tokenize import word_tokenize, sent_tokenize
from django.http import JsonResponse
from api.db import connect
from rest_framework.decorators import api_view
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.data.path.append("/tmp")
client = connect()
db = client['Airport_Analysis']
food_db = db["lounge"]
schedule_db = db["flight_schedule"]
sid = SentimentIntensityAnalyzer()


@api_view(['GET'])
def LoungeReviews(request, airport):
    data = airport
    data = data.split("-")[0].capitalize()
    # print(data)
    flights = schedule_db.find(
        {"origin": data}, {"_id": 0, "airline": 1, "dayOfWeek": 1})
    su_arr = []
    for fi in flights:
        summa = fi["airline"].split(" ")
        # print(summa)
        if len(summa) == 1:
            summa = "".join(summa).lower()
        else:
            summa = "-".join(summa).lower()
        su_arr.append(summa)
    su_arr = [*set(su_arr)]
    arrow = {
        "value": [],
        "recomm": [],
        "rating": []
    }

    # print(su_arr)
    json_op = {
        "pos_items": [],
        "neg_items": []
    }
    senti_dict = {
        "pos": 0,
        "neg": 0,
        "neu": 0
    }
    airplain_food = []
    valie = 0
    comment_fin = []
    for su in su_arr:
        valie = 0
        if su == "":
            continue
        fields = food_db.find({"airline_name": su}).limit(15)

        food_names = ["lounge", "areas", "bar", "drinks",
                      "food", "restrooms", "toilets", "secure", "security"]
        for i in fields:

            # print(i)
            if i["overall_rating"] == "" or i["overall_rating"] == None:
                i["overall_rating"] = 0
            arrow["rating"].extend([i["overall_rating"]])
            arrow["recomm"].extend(([(i["recommended"]+1)*5]))
            arrow["value"].extend([i["staff_service_rating"]])
            valie += i["overall_rating"] + i["comfort_rating"]
            senti = sid.polarity_scores(i["content"])["compound"]
            tokenized = sent_tokenize(i["content"].lower())
            for line in tokenized:
                # print(line)
                for j in food_names:
                    tokens = word_tokenize(line)
                    tagged = nltk.pos_tag(tokens)
                    if j in line:
                        senti = sid.polarity_scores(line)["compound"]
                        if senti >= 0.5:
                            senti_dict["pos"] += 1
                            for j, tag in enumerate(tagged):
                                if tag[1] == "JJ":
                                    if tagged[j+1][1] == "NN" or "NNP":
                                        semi = str(tag[0]) + \
                                            str(tagged[j+1][1])
                                        json_op["pos_items"].extend([semi])
                                    else:
                                        continue
                                    json_op["pos_items"].extend([tag[0]])
                        elif senti <= -0.5:
                            senti_dict["neg"] += 1
                            if type(i) is not tuple:
                                comment_fin.append({
                                    "content": i["content"],
                                    "user_name": i["author"],
                                    "date": i["date"],
                                    "user_country": i["author_country"],
                                    "rating": float(i["overall_rating"]) % 5
                                })
                            for j, i in enumerate(tagged):
                                if i[1] == "JJ":
                                    if tagged[j+1][1] == "NN" or "NNP":
                                        semi = str(i[0])+str(tagged[j+1][1])
                                        json_op["neg_items"].extend([semi])
                                else:
                                    continue
                                json_op["neg_items"].extend([i[0]])
                        else:
                            senti_dict["neu"] += 1
        airplain_food.append({
            "label": su,
            "value": valie+10
        })
    for j, i in enumerate(airplain_food):
        if i["value"] == "NaN":
            del airplain_food[j]
        if i["value"] != i["value"]:
            del airplain_food[j]
        if pd.isna((float(i["value"]))) == True:
            # print({pd.isna((float(i["value"])))})
            print(airplain_food[j])
            del airplain_food[j]
            print(airplain_food)
        else:
            print(pd.isna((float(i["value"]))))
    # print(airplain_food)
    senti_arr = [
        {"name": "positive", "value": senti_dict["pos"]},
        {"name": "negative", "value": senti_dict["neg"]},
        {"name": "neutral", "value": senti_dict["neu"]},
    ]
    arrow_fin = [
        {"name": 'Rating', "data": arrow["rating"]},
        {"name": 'Recommended', "data": arrow["recomm"]},
        {"name": 'Value for Money', "data": arrow["value"]}
    ]
    for val in arrow_fin:
        for j, cc in enumerate(val["data"]):
            if pd.isna((float(cc))) == True:
                val["data"][j] = 0
    final_op = [json_op, senti_arr, airplain_food, comment_fin, arrow_fin]
    return JsonResponse(final_op, safe=False)
