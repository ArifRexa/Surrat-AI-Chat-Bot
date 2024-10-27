import requests
import json
import os
import sys

server_url = 'https://www.acapela-cloud.com'

# ---------------------------------------------------------------------------------------------
def login(email, password):
	print('Logging in...')

	headers = {
		'Content-Type': 'application/json',
	}
	data = '{"email": "' + email + '","password": "' + password + '"}'

	response = requests.post(server_url + '/api/login/', headers=headers, data=data)

	# get token from login
	json_response = response.json()

	if response.status_code == 200:
		token = json_response["token"]
		return token
	else:
		return ""
		

# ---------------------------------------------------------------------------------------------
def logout(token):

	headers = {
    	'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}

	response = requests.get(server_url + '/api/logout/', headers=headers)
	return response

# ---------------------------------------------------------------------------------------------
def country_list():

	# get command history
	headers = {
    	'Content-Type': 'application/json',
	}

	response = requests.get(server_url + '/api/country/', headers=headers)
	
	return response
	
	
# ---------------------------------------------------------------------------------------------
def password_change(token,password):

	# get account detail
	headers = {
    	'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}

	data = '{"password": "' + password + '"}'
	response = requests.post(server_url + '/api/password/change/', headers=headers, data=data)
	return response

			
# ---------------------------------------------------------------------------------------------
def password_reset(email):

	# get account detail
	headers = {
    	'Content-Type': 'application/json',
	}

	data = '{"email": "' + email + '"}'
	response = requests.post(server_url + '/api/password/reset/verify', headers=headers, data=data)
	return response
	


			
# ---------------------------------------------------------------------------------------------
def password_reset_verify(code,password):

	# get account detail
	headers = {
    	'Content-Type': 'application/json',
	}

	data = '{"code": "' + code + '","password": "' + password + '"}'
	response = requests.post(server_url + '/api/password/reset/verify', headers=headers, data=data)
	return response
	


# ---------------------------------------------------------------------------------------------
def account_details(token):

	# get account detail
	headers = {
    	'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}

	response = requests.get(server_url + '/api/account/', headers=headers)
	return response


# ---------------------------------------------------------------------------------------------
def update_account_details(token,address):

	# update account details
	headers = {
    	'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}

	data = '{"address": "' + address + '"}'

	response = requests.patch(server_url + '/api/account/', headers=headers, data=data)
	return response
			


# ---------------------------------------------------------------------------------------------
def send_command(token,voice, text, output,type="mp3", wordpos="off", mouthpos="off", dico="", application="", volume="32768", shaping="100", speed="100", samplerate="", bitrate=""):

	# Send command
	headers = {
		'Authorization': 'Token ' + token,
		'Content-Type': 'application/json',
	}

	params = {'voice':voice,'output':output,'text':text,'type':type,'wordpos':wordpos,'mouthpos':mouthpos, 'dico':dico,'application':application,'volume':volume,'shaping':shaping,'speed':speed,'samplerate':samplerate,'bitrate':bitrate}
	
	if output == "stream":
		response = requests.get(server_url + '/api/command/', stream=True , headers=headers, params=params)
	else:
		response = requests.get(server_url + '/api/command/',  headers=headers, params=params)
		
	return response



# ---------------------------------------------------------------------------------------------
def send_command_post(token,voice, text, output,type="mp3", wordpos="off", mouthpos="off", dico="", application="", volume="32768", shaping="100", speed="100", samplerate="", bitrate=""):


	# Send command
	headers = {
		'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}

	data = '{"voice": "' + voice + '","output": "' + output + '","text": "' + text + '","type": "' + type + '","wordpos": "' + wordpos + '","mouthpos": "' + mouthpos + '","dico": "' + dico + '","application": "' + application + '","volume": "' + volume + '","shaping": "' + shaping + '","speed": "' + speed + '","samplerate": "' + samplerate + '","bitrate": "' + bitrate + '"}'

	if output == "stream":
		response = requests.post(server_url + '/api/command/', stream=True , headers=headers, data=data.encode('utf-8'))
	else:
		response = requests.post(server_url + '/api/command/',  headers=headers, data=data.encode('utf-8'))


	return response




# ---------------------------------------------------------------------------------------------
def command_stats(token, interval="day",option=""):

	# get command history
	headers = {
    	'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}
	params = {'type':'command', 'interval':interval, 'option':option}

	response = requests.get(server_url + '/api/stats/', headers=headers, params=params)

	return response

# ---------------------------------------------------------------------------------------------
def voice_stats(token, interval="month",option=""):

	# get voice history
	headers = {
    	'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}
	params = {'type':'voice', 'interval':interval, 'option':option}

	response = requests.get(server_url + '/api/stats/', headers=headers, params=params)

	return response

# ---------------------------------------------------------------------------------------------
def credit_stats(token, interval="month",option=""):

	# get credit history
	headers = {
    	'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}
	params = {'type':'credit', 'interval':interval, 'option':option}

	response = requests.get(server_url + '/api/stats/', headers=headers, params=params)

	return response



# ---------------------------------------------------------------------------------------------
def billing_stats(token, interval="month",option=""):

	# get billing history
	headers = {
    	'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}
	params = {'type':'billing', 'interval':interval, 'option':option}

	response = requests.get(server_url + '/api/stats/', headers=headers, params=params)

	return response


# ---------------------------------------------------------------------------------------------
def purchase_stats(token, interval="month"):

	# get purchase history
	headers = {
    	'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}
	params = {'type':'purchase', 'interval':interval}

	response = requests.get(server_url + '/api/stats/', headers=headers, params=params)

	return response

# ---------------------------------------------------------------------------------------------
def storage_add(token,file):

	# upload file
	headers = {
    	'Authorization': 'Token ' + token,
	}
	
	files = {"file": (file, open(file, 'rb'), 'multipart/form-data')}

	response = requests.post(server_url + '/api/storage/',files=files, headers=headers)

	return response


# ---------------------------------------------------------------------------------------------
def storage_get(token,file):

	# list user files or get file
	headers = {
    	'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}
	
	params = {'file': file}
	response = requests.get(server_url + '/api/storage/', headers=headers, params=params)
	   
	return response



# ---------------------------------------------------------------------------------------------
def storage_list(token):

	# list user files or get file
	headers = {
    	'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}
	
	response = requests.get(server_url + '/api/storage/', headers=headers)
	    
	return response

# ---------------------------------------------------------------------------------------------
def storage_delete(token,file):

	# list user files
	headers = {
    	'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}
	
	data = '{"file": "' + file + '"}'
	response = requests.delete(server_url + '/api/storage/', headers=headers, data=data)
	    
	return response


# ---------------------------------------------------------------------------------------------
def tos(token,answer=""):

	# get Terms of service text or accept/reject them
	headers = {
		'Authorization': 'Token ' + token,
    	'Content-Type': 'application/json',
	}

	if answer == "":
		response = requests.get(server_url + '/api/tos/', headers=headers)
	else:
		data = '{"answer": "' + answer + '"}'
		response = requests.post(server_url + '/api/tos/', headers=headers, data=data.encode('utf-8'))

	return response
