import requests as r
import ast
import json
import time
import matplotlib.pyplot as plt

def state():
    res =r.get("http://127.0.0.1:8000/superapi/state/", auth)
    if res.status_code == 200:
        return(res.text)
    else:
        return("error state")

def stats():
    res =r.get("http://127.0.0.1:8000/superapi/stats/", auth)
    if res.status_code == 200:
        return(res.text)
    else:
        return("error state")

def spot():
    res = r.get("http://127.0.0.1:8000/superapi/spots/", auth)
    #print(res.text)
    return(ast.literal_eval(res.text))

def addSpot():
    res = r.post("http://127.0.0.1:8000/superapi/spots/", json.dumps({'token' : token, 'user_id' : user_id,
                                                           'spot':{'centrex' : 0, 'centrey': 0, 'centrez':0, 'rayon':1,
                                                                   'currentQuestion' : 2,
                                                                   'questionList': [2],
                                                                   'startTime' : time.time(),
                                                                   'delay' : 15}}))

    print(res.text)

def displaySpots():
    spots=spot()
    points = []
    rayons = []
    circles = []
    
    for s in spots['spots']:
        points.append((s['centrex'], s['centrey']))
        rayons.append(s['rayon'])

    a = plt.Circle(points, rayons)
    plt.show()
    
def question(nbr=None):

    if nbr == None:
        res = r.get("http://127.0.0.1:8000/superapi/questions/", auth)
    else:
        res = r.get("http://127.0.0.1:8000/superapi/questions/"+str(nbr)+"/", auth)
    print(res.text)

def questionDelete(nbr):
    res = r.post("http://127.0.0.1:8000/superapi/questions/delete/"+str(nbr)+"/", auth)
    print(res.text)

def addQuestion():

    data = {'question':
            {'questionText': "nouvelle question 2",
                'answer1': "1",
                'answer2' : "2",
                'answer3' : "3",
                'answer4' : "4",
                'rightAnswer' : 1,
                'difficulty' : 12,
                'score' : 123,
                'topic' : "truc"}
            }

    data.update(auth)
    print(data)
    res = r.post("http://127.0.0.1:8000/superapi/questions/", json.dumps(data))
    print(res.status_code)
    print(res.text)

def position(nbr=None):
    if nbr == None:
        res = r.get("http://127.0.0.1:8000/superapi/position/", auth)
    else:
        res = r.get("http://127.0.0.1:8000/superapi/position/"+str(nbr)+"/", auth)
    print(res.text)
    

res = r.post("http://127.0.0.1:8000/superapi/auth/",
             {'username': 'rgaret', 'password': 'azertyuiop'})

if res.status_code == 200:
    data = ast.literal_eval(res.text)
    token = data["token"]
    user_id =data["user_id"]
    auth ={'token' : token, 'user_id' : user_id}
    
    print("Token: "+str(token)+" user_id: "+str(user_id))

    #print("\nServer state: "+ state())
    #print("\nServer stats" + stats())
    

else:
    print("Authentication failed")

