#!usr/bin/python 
# -*- coding: utf-8 -*-
import threading,sys
import time
from datetime import datetime
from threading import Thread
from config import*
import random
import re
import sys
from clockwork import clockwork

accounts=[]
success_jobs=[]
failed_jobs=[]

parameters=sys.argv
if len(parameters)>1 and (parameters[1]=="w" or parameters[1]=="W"):
	S_sender=True
else:
	S_sender=False
try: 
	L=open(clockwork_accounts)
	l=L.readline()
	while l!='':
		accounts.append(l.replace("\n",""))
		l=L.readline()
	L.close()
except: 
	print("\n[+] We were unable to open the accounts file. Check again your path and try again.")

try: 
	L=open(jobsf)
	jobs = L.read().split('\n')
	Failed_jobs=[]
	L.close()
except: 
	print("\n[+] We were unable to open the jobs file. Check again your path and try again.")

try: 
	L=open(linkf)
	links = L.read().split('\n')
	L.close()
except: 
	print("\n[+] We were unable to open the links file. Check again your path and try again.")

try: 
	L=open(senderf)
	senders = L.read().split('\n')
	L.close()
except: 
	print("\n[+] We were unable to open the senders file. Check again your path and try again.")
try: 
	L=open(bodyf,encoding="utf8")
	body = L.read()
	L.close()
except Exception as e: 
	print("\n[+] We were unable to open the body file. Check again your path and try again.",bodyf,e)

print("limit number of thread is : ",thread_limit)


def timer():
	now = time.localtime(time.time())
	return time.asctime(now)

def get_account(index=random.randint(0,len(accounts)-1)):
	return accounts[index]

def get_proxy(index):
	return proxies[index%len(proxies)]

def sendsms(body,job,number,sender=False):   # seperated function for checking
	global N,jobs
	Err_N=0
	while True:
		try:
			API_Key = get_account(N)
			client = clockwork.API(API_Key)
			print("[+]",API_Key,job)
			if sender:
				message=clockwork.SMS(to=number,message=body,from_name =sender)
			else:
				message=clockwork.SMS(to=number,message=body)
			response = client.send(message)
			if response.success:
				print("\t\t[-]",'Sent message',":".join(job))
				print("\t\t[-]",'Remaining balance is', client.get_balance())
				success_jobs.append(job)
				return True
			else:
				er=int(response.error_code)
				print ("\t\t[-]","error code :",er)
				if er==1:
					print("\t\t[-]","Something went wrong in our API")
				elif er==12:
					print("\t\t[-]","Message text is too long")
				elif er==13:
					print("\t\t[-]","You don't have an international contract")
				elif er==15:
					print("\t\t[-]","you Cannot  send SMS to this country")
				elif er==17:
					print("\t\t[-]","You IP address is blocked")
				elif er==25:
					print("\t\t[-]","Your account is setup to require a unique Client ID on each message, we've seen this one before.")
				elif er==26:
					print("\t\t[-]","Something went wrong in our API")
				elif er==33:
					print("\t\t[-]","Your account is setup to check for a unique client ID on every message, one wasn't supplied in this send.")
				elif er==40:
					print("\t\t[-]","MMS text has an invalid character")
				elif er==41:
					print("\t\t[-]","MMS Payload can't be decoded as hex")
				elif er==42:
					print("\t\t[-]","MMS payload can't be decoded as Base64")
				elif er==43:
					print("\t\t[-]","No content type provided on MMS payload")
				elif er==44:
					print("\t\t[-]","All MMS Payload parts must have an ID")
				elif er==45:
					print("\t\t[-]","The combined parts are too large to send")
				elif er==49:
					print("\t\t[-]","All MMS parts must have unique filenames")
				elif er==57:
					print("\t\t[-]","You need to provide an API Key or a Username and Password when calling the API")
				elif er==58:
					print("\t\t[-]","Log in to your API account to check the key or create a new one")
				elif er==59:
					print("\t\t[-]","This account isn't allowed to use a Username and Password, log in to your account to create a key")
				elif er==60:
					print("\t\t[-]","Sometimes your message will be caught by our spam filter. If you're having trouble because of this error - get in touch and we'll get you up and running. Include an example of the message that was caught if you can")
				elif er==100:
					print("\t\t[-]","Something went wrong in our API")
				elif er==101:
					print("\t\t[-]","Something went wrong in our API")
				elif er==102:
					print("\t\t[-]","API Post can't be parsed as XML")
				elif er==305:
					print("\t\t[-]","You've sent too many status requests this hour")
				N=(N+1)%len(accounts)
				Err_N+=1
				if Err_N>len(accounts):
					print("problem happen with all accounts , or there is a problem with connection / and your file : job, account, sender,link, body")
					failed_jobs.append(job)
					return
		except Exception as e:
			print("\t\t[-]",e,":", API_Key)
			print()
			#print("[-]\t\tLogin Failed:", API_Key)
			N=(N+1)%len(accounts)
			Err_N+=1
			if Err_N>len(accounts):
				print("problem happen with all accounts , or there is a problem with connection / and your file : job, account, sender,link, body")
				failed_jobs.append(job)
				return
			#print("Try with other credential")

N,X,S = 0,0,0
L_th=[]
print("[!] Start at: " + timer() + "")
print("[+] cheking accounts balences  :")
for i in accounts:
	client = clockwork.API(i)
	balance = float(client.get_balance()['balance'])
	if balance<limit_amount:
		accounts.remove(i)
		print("\t",i,balance,'disable')
	print("\t",i,balance,'active')
print("\t","-----------------------------")
print("\t","Total active accounts",len(accounts))
if(len(accounts)<1):
		print("\t","there is active accounts")
		sys.exit()

for j in jobs:
	if j!="":
		job=j.split(":")
		try:
			number=job[1]
			body1 = re.sub('_To', job[0], body)
			body1 = re.sub('_From', senders[S], body1)
			body1 = re.sub('_Link', links[X], body1)
			if (S_sender):
				th=Thread(target=sendsms,args=(body1,job,number,senders[S],))
			else:
				th=Thread(target=sendsms,args=(body1,job,number,))
			L_th.append(th)
			th.start()
			while threading.active_count() >=thread_limit:
				pass
		except Exception as e:
			print('\n[+] We have found a error in your accounts list')
			print('\n[!] IMPORTANT: THE ACCOUNT ACCOUNTS MUST BE IN THE FOLLOWING FORMAT : API KEY:API SECRET')
			print(e)
		N = (N + 1) % len(accounts)
		X = (X + 1) % len(links)
		S = (S + 1) % len(senders)
		time.sleep(timing)

for i in L_th:
	i.join()
print("[!] Ended at: " + timer() + "")
print("reformat the accounts/links/senders file")
N = (N - 1) % len(accounts)
accounts = accounts[N + 1:]+accounts[:N + 1]
X = (X - 1) % len(links)
links = links[X + 1:] + links[:X + 1]
S = (S - 1) % len(links)
senders = senders[S + 1:] + senders[:S + 1]

L = open(nexmo_accounts,"w")
for i in accounts:
	L.write(i + "\n")
L.close()

L = open(linkf,"w")
for i in links:
	L.write(i + "\n")
L.close()

L = open(senderf,"w")
for i in senders:
	L.write(i + "\n")
L.close()

now = datetime.now()
current_time = now.strftime("%m-%d-%Y %H-%M-%S")
L = open("Logs/"+current_time+"_"+s_jobsf ,"w")
for i in success_jobs:
	L.write(':'.join(i) + "\n")
L.close()

L = open("Logs/"+current_time+"_"+f_jobsf ,"w")
for i in failed_jobs:
	L.write(':'.join(i) + "\n")
L.close()