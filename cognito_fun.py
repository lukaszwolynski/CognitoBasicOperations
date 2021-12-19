import json
import os
import boto3
import random
import string 


client = boto3.client("cognito-idp", region_name="eu-central-1")
user_pool_id = os.getenv("USER_POOL_ID")
CLIENT_ID = os.getenv("CLIENT_ID")

#create user and send verification code to user's email
def createUser(username, email, password, name):
    try:
        resp = client.sign_up(
                ClientId=CLIENT_ID,
                Username=username,
                Password=password, 
                UserAttributes=[
                {
                    'Name': "name",
                    'Value': name
                },
                {
                    'Name': "email",
                    'Value': email
                }
                ],
                ValidationData=[
                    {
                    'Name': "email",
                    'Value': email
                },
                {
                    'Name': "custom:username",
                    'Value': username
                }
    ])
    except client.exceptions.UsernameExistsException as e:
        return {"error": False, 
               "success": True, 
               "message": "This username already exists", 
               "data": None}
    except client.exceptions.InvalidPasswordException as e:
        return {"error": False, 
               "success": True, 
               "message": "Password should have Caps,\
                          Special chars, Numbers", 
               "data": None}


def confirmUser(username):
    response = client.admin_confirm_sign_up(
    UserPoolId=user_pool_id,
    Username=username
)

def getUsers():
    usernames = list ()
    users_resp = client.list_users (
            UserPoolId = user_pool_id,
            AttributesToGet = ['email'])
    
    for user in users_resp['Users']:
        user_record = {'username': user['Username'], 
                      'email': None,
                      'confirmed': user['UserStatus']
        }
        for attr in user['Attributes']:
                if attr['Name'] == 'email':
                    user_record['email'] = attr['Value']
                usernames.append (user_record)
    return usernames     
    

def getOnlyConfirmedUsers():
    users = getUsers()
    for user in users:
        if user['confirmed'] != 'CONFIRMED':
            users.remove(user)
    return users
    
    
def lambda_handler(event, context):
    usernames = ["CoolUser", "CoolerUser", "TheCoolestUserInTheWorld"]
    emails = []
    for i in range(3):
        emails.append(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)) + "@mail.com")
    
    password = "zaq1@WSX"
    names = ["SuperCoolUser", "AnotherCoolUser", "TheCoolestUserInTheWorld"]
    
    for i in range(len(usernames)):
        createUser(usernames[i], emails[i], password, names[i])
        
        if i%2 == 0:
            confirmUser(usernames[i])
    
    #createUser(username, email, password, name)
    return {
        'statusCode': 200,
        'body': getOnlyConfirmedUsers()
    }
