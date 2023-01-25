from nltk.tokenize import word_tokenize, sent_tokenize
from api.db import connect
from .searializer import AirPort_serializer
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
import datetime
from bs4 import BeautifulSoup
import requests
from django.views.decorators.csrf import csrf_exempt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download("vader_lexicon'", download_dir="/var/lang/nltk_data")
stop_words = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their',
              'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than'}


# For Gensim
client = connect()
db = client['Airport_Analysis']
coll = db["airport_feedbacks"]
food_db = db["food airlines"]
lat_long_db = db["Airport_lat_long"]
sid = SentimentIntensityAnalyzer()


@api_view(['GET'])
def getRoutes(request, airport):
    fields = coll.find({}).limit(20)
    airport_loc = lat_long_db.find(
        {"City/Town": {'$regex': str(airport.split("-ai")[0]).upper(), '$options': 'i'}})
    list_cur = list(airport_loc)
    print(list_cur)
    if not bool(list_cur):
        airport_loc = lat_long_db.find(
            {"Airport Name": {'$regex': str(airport.split("-ai")[0]).upper(), '$options': 'i'}})
    # print(airport_loc)
    list_cur = list(airport_loc)
    out = {"lat": 0, "long": 0}
    if bool(list_cur):
        out = {
            "lat": list_cur[0]["Latitude Decimal Degrees"],
            "long": list_cur[0]["Longitude Decimal Degrees"]
        }
    time_graph = coll.find(
        {"airport_name": airport}, {"_id": 0, "airport_name": 1, "date": 1, "overall_rating": 1}).sort("date")
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
    seri = AirPort_serializer(
        fields, many=True, allow_null=True, required=False)
    count_array = [0, 0, 0, 0, 0, 0, 0, 0]
    arr_ll = ["queuing_rating", "terminal_cleanliness_rating",
              "terminal_seating_rating", "terminal_signs_rating", "food_beverages_rating",
              "airport_shopping_rating", "wifi_connectivity_rating", "airport_staff_rating"]
    comments_fin = []
    for i in seri.data:
        # print(i)
        pred = sid.polarity_scores(i["content"])
        for j in arr_ll:
            if i[j] == "":
                i[j] = "0"
        count_array[0] += float(i["queuing_rating"])
        count_array[1] += float(i["terminal_cleanliness_rating"])
        count_array[2] += float(i["terminal_seating_rating"])
        count_array[3] += float(i["terminal_signs_rating"])
        count_array[4] += float(i["food_beverages_rating"])
        count_array[5] += float(i["airport_shopping_rating"])
        count_array[6] += float(i["wifi_connectivity_rating"])
        count_array[7] += float(i["airport_staff_rating"])
        # for key in sorted(pred.keys()):
        #     print('{}: {}, '.format(key, pred[key]), end='')
        # print("/n")
        analise = pred["compound"]
        if analise >= 0.5:
            pos += 1
        elif analise < -0.5:
            comments_fin.append({
                "content": i["content"],
                "user_name": i["author"],
                "date": i["date"],
                "user_country": i["author_country"],
                "rating": float(i["overall_rating"]) % 5
            })
            neg += 1
        else:
            neu += 1
    # print("calue", pos, neg, neu)
    json_object = [
        {"name": "positive", "value": pos},
        {"name": "negative", "value": neg},
        {"name": "neutral", "value": neg},
    ]
    count_array = [i/5 for i in count_array]
    # print(count_array)
    r = requests.get(
        "https://unsplash.com/s/photos/"+airport).text
    soup = BeautifulSoup(r, 'html.parser')
    images = soup.find_all('img')
    # print(images[5]["src"])
    comments_fin.sort(
        key=lambda x: datetime.datetime.strptime(x['date'], '%Y-%m-%dT00:00:00Z'))
    final_ob = {
        "sentiment": json_object,
        "time_analysis": time_details,
        "rating_analysis": count_array,
        "image": images[15]["src"],
        "tickets": comments_fin,
        "coors": out
    }
    return JsonResponse(final_ob, safe=False)


@api_view(['GET'])
def getWord(request, route):
    fields = coll.find({"airport_name": route},
                       {"_id": 0, "content": 1}).limit(15)
    feautures = ["airport", "terminal", "check in",
                 "security", "queue", "experience", "toilets", "shop"]
    senti_dict = {
        "airport": {
            "pos": 0,
            "neg": 0,
            "neu": 0,
            "remarks": [],
            "good_points": [],
            "neutal_points": []
        },
        "terminal": {
            "pos": 0,
            "neg": 0,
            "neu": 0,
            "remarks": [],
            "good_points": [],
            "neutal_points": []
        },
        "check in": {
            "pos": 0,
            "neg": 0,
            "neu": 0,
            "remarks": [],
            "good_points": [],
            "neutal_points": []
        },
        "security": {
            "pos": 0,
            "neg": 0,
            "neu": 0,
            "remarks": [],
            "good_points": [],
            "neutal_points": []
        },
        "queue": {
            "pos": 0,
            "neg": 0,
            "neu": 0,
            "remarks": [],
            "good_points": [],
            "neutal_points": []
        },
        "experience": {
            "pos": 0,
            "neg": 0,
            "neu": 0,
            "remarks": [],
            "good_points": [],
            "neutal_points": []
        },
        "toilets": {
            "pos": 0,
            "neg": 0,
            "neu": 0,
            "remarks": [],
            "neutal_points": []
        },
        "shop": {
            "pos": 0,
            "neg": 0,
            "neu": 0,
            "remarks": [],
            "good_points": [],
            "neutal_points": []
        },
    }

    for i in fields:
        tokenized = sent_tokenize(i["content"].lower().replace("-", " "))
        for line in tokenized:
            # print(line)
            for j in feautures:
                tokens = word_tokenize(line)
                filtered_sentence = [
                    w for w in tokens if not w.lower() in stop_words]
                tagged = nltk.pos_tag(filtered_sentence)
                if j in line:
                    senti = sid.polarity_scores(line)["compound"]
                    if senti >= 0.5:
                        senti_dict[j]["pos"] += 1
                        for i in tagged:
                            if i[1] == "JJ":
                                senti_dict[j]["good_points"].extend([i[0]])
                    elif senti < -0.5:
                        senti_dict[j]["neg"] += 1
                        for i in tagged:
                            if i[1] == "JJ":
                                senti_dict[j]["remarks"].extend([i[0]])
                    else:
                        senti_dict[j]["neu"] += 1
                        for i in tagged:
                            if i[1] == "JJ":
                                senti_dict[j]["neutal_points"].extend([i[0]])
                    # print(j)

                else:
                    continue

            # print(tagged)
            # for i in tagged:
            #     print(i)
    # ll=senti_dict.items()
    analytics = []
    for key, value in senti_dict.items():
        analytics.append({
            key: value
        })
    return JsonResponse(analytics, safe=False)


@csrf_exempt
def change_db(request, portName):
    if request.method == "POST":
        data = JSONParser().parse(request)
        fields = coll.find({"$and": [{"airport_name": portName}, {"content": {"$regex": data["tag"], '$options': 'i'}}]},
                           {"_id": 0, "content": 1, "author": 1, "date": 1, "overall_rating": 1, "author_country": 1}).limit(15)
        fina_arr = []
        for i in fields:
            print(i)
            if i["overall_rating"] == "":
                i["overall_rating"] = 0
            fina_arr.append({
                "content": i["content"],
                "user_name": i["author"],
                "date": i["date"].strftime("%d %B, %Y"),
                "user_country": i["author_country"],
                "rating": float(i["overall_rating"]) % 5
            })
        fina_arr.sort(
            key=lambda x: datetime.datetime.strptime(x['date'], '%d %B, %Y'))
        # print(fina_arr)
    return JsonResponse(fina_arr, safe=False)


"""
big_arr = []
    for i in fields:
        final_dic = {}
        tokenized = sent_tokenize(i["content"])
        for i in tokenized:
            adj_list = []
            wordsList = nltk.word_tokenize(i)
            tagged = nltk.pos_tag(wordsList)

            for j, i in enumerate(tagged):
                if i[1] == "JJ":
                    try:
                        if (j-1 > 0 and j-1 < len(tagged)) and (tagged[j-1][1] == "NN" or tagged[j-1][1] == "NNS"):
                            adj_list.append(tagged[j-1][0]+" "+i[0])
                        else:
                            adj_list.append(i[0])
                    except:
                        print("Its")
                if i[1] == "CC" and j+1 < len(tagged)-1:
                    if tagged[j+1][1] in ["NNP", "NN"]:
                        # print("CURRINKFKNDSKNDNKSM")
                        tagged = tagged[index(tagged.index(i))+1:]
                        adj_list = []
                        continue
                if tagged[0][1] == "JJ" and len(tagged) > 8:
                    break
                if tagged[0][1] in ["NNP", "NN"] and tagged[1][1] not in ["NNP", "NN", "CC"] and tagged[1][1] != "PRP":
                    if tagged[0][0] in final_dic.keys():
                        adj_list = [
                            j for j in adj_list if j not in final_dic[tagged[0][0]]]
                        final_dic[tagged[0][0]].extend(adj_list)
                    else:
                        final_dic[tagged[0][0]] = adj_list
                else:
                    if (i[1] in ["NN", "NNS", "NNPS", "NNP"] or i[0] == "terminal") and (j-1 > 0 and j-1 < len(tagged)):
                        if tagged[j-1][1] not in ["TO", "DT"]:
                            # print("TSAGGEGRD:", tagged[j-1][1])
                            if i[0] in final_dic.keys() and adj_list != []:
                                adj_list = [
                                    j for j in adj_list if j not in final_dic[i[0]]]
                                final_dic[i[0]].extend(adj_list)
                            elif i[0] not in final_dic.keys() and adj_list != [] and adj_list != None:
                                final_dic.update({i[0]: list(adj_list)})
                            adj_list = []
            # print(final_dic)
        big_arr.append(final_dic)
"""
