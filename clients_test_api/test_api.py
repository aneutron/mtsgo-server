import requests as r
import ast
import json

##res = r.post("http://127.0.0.1:8000/api/auth/new/",
##             json.dumps({'creds': {
##            'username': 'user1',
##            'password': 'newpass',
##            'email': 'mycoolemail@hey.me'
##        }}))


def info():
    res = r.post("http://127.0.0.1:8000/api/player/", auth)
    print (res.text)


if res.status_code == 200:
    data = ast.literal_eval(res.text)
    token = data["token"]
    user_id =data["user_id"]
    auth ={'token' : token, 'user_id' : user_id}
    
    print("Token: "+str(token)+" user_id: "+str(user_id))

    res = r.get("http://127.0.0.1:8000/api/player/", auth)
    print (res.text)


else:
    print("Authentication failed")
