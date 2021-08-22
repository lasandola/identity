from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import threading
import argparse
import re
import cgi

import random

class LocalData(object):
  records = {}

class HTTPRequestHandler(BaseHTTPRequestHandler):

  def do_GET(self):

    print('got path: '+self.path)
    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    age_not_legal = False

    if None != re.search('/api/getdata/*/', self.path):

      apiversion = self.path.replace("/api/getdata/","")
      # Get a random gender: here we just use the stantard function
      # It is a tiny bit female oriented as the interval is: [0:1), so 100% is only possible for female.
      random_gender = random.random()
      female = random_gender
      male = 1.0 - female

      # Get a random Age
      legal_age = 18
      #random_age = int(random.random() * 90.0) # Uniform 0-90
      # Below we try a very bad distribution but it should work
      random_age = int(random.gauss(32,15) * 1.2)
      
      # Below we remove not legal ages and try to get a new random value bu we set a flag for minors
      if (random_age < legal_age):
        age_not_legal = True
        random_age = int(random.random() * 30.0)+legal_age
        
      # Bucketization here: https://stackoverflow.com/questions/12720151/simple-way-to-group-items-into-buckets
      # Below we have a simple version ;)
      random_age_bucket = "NAN"
      if (random_age > legal_age and random_age <= 25):
        random_age_bucket = "legal-25"
      elif (random_age > 25 and random_age <= 35):
        random_age_bucket = "26-35"
      elif (random_age > 35 and random_age <= 45):
        random_age_bucket = "36-45"
      elif (random_age > 45 and random_age <= 55):
        random_age_bucket = "46-55"
      elif (random_age > 55 and random_age<= 65):
        random_age_bucket = "56-65"
      elif (random_age > 65):
        random_age_bucket = "65+"
      else:
        random_age_bucket = "Internal error"

      # Let's add interest's
      random_interest = random.random()*10.0
      random_interest_bucket = "NAN"
      if (random_interest >= 0.0 and random_interest < 1.0 ):
        random_interest_bucket = "auto"
      elif (random_interest >= 1.0 and random_interest < 2.0 ):
        random_interest_bucket = "music"
      elif (random_interest >= 2.0 and random_interest < 3.0 ):
        random_interest_bucket = "electronics"
      elif (random_interest >= 3.0 and random_interest < 4.0 ):
        random_interest_bucket = "movies"
      elif (random_interest >= 4.0 and random_interest < 5.0 ):
        random_interest_bucket = "social media"
      elif (random_interest >= 5.0 and random_interest < 6.0 ):
        random_interest_bucket = "books"
      elif (random_interest >= 6.0 and random_interest < 7.0 ):
        random_interest_bucket = "motorrad"
      elif (random_interest >= 7.0 and random_interest < 8.0 ):
        random_interest_bucket = "quadcopters"
      elif (random_interest >= 8.0 and random_interest < 9.0 ):
        random_interest_bucket = "news"
      elif (random_interest >= 9.0 ):
        random_interest_bucket = "surprise me"
      else:
        random_interest_bucket = "Internal Error"


      response_static = '{"gender":"f", "age":"18", "interest":"xyz"}'
      response_actual = response_static
      if (apiversion == "v2/"):
        response_simple = '{"gender":'+'{"female":"'+str(female)+'","male":"'+str(male)+'"}'+', "age":"'+str(random_age)+'", "interest":"xyz"}'
        response_actual = response_simple
      if (apiversion == "v3/"):
        response_age_bucket = '{"gender":'+'{"female":"'+str(female)+'","male":"'+str(male)+'"}'+', "age":"'+str(random_age)+'"'+', "ageBucket":"'+random_age_bucket+'"'+', "interest":"'+str(random_interest)+'"}'
        response_actual = response_age_bucket
      if (apiversion == "v4/"):
        response_interest_bucket = '{"gender":'+'{"female":"'+str(female)+'","male":"'+str(male)+'"}'+', "ageBucket":"'+random_age_bucket+'"'+', "interest":"'+str(int(random_interest))+'", "interestBucket":"'+random_interest_bucket+'"}'
        response_actual = response_interest_bucket
      if (apiversion == "v5/"):
        if (age_not_legal):
          response_api = '{"not_legal":"true"}'
        else:
          response_api = '{"gender":'+'{"female":"'+str(female)+'","male":"'+str(male)+'"}'+', "ageBucket":"'+random_age_bucket+'"'+', "interestBucket":"'+random_interest_bucket+'"}'
        response_actual = response_api
        
      self.wfile.write(response_actual)

    return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  allow_reuse_address = True

  def shutdown(self):
    self.socket.close()
    HTTPServer.shutdown(self)

class SimpleHttpServer():
  def __init__(self, ip, port):
    self.server = ThreadedHTTPServer((ip,port), HTTPRequestHandler)

  def start(self):
    self.server_thread = threading.Thread(target=self.server.serve_forever)
    self.server_thread.daemon = True
    self.server_thread.start()

  def waitForThread(self):
    self.server_thread.join()

  def stop(self):
    self.server.shutdown()
    self.waitForThread()

if __name__=='__main__':
  parser = argparse.ArgumentParser(description='HTTP Server')
  parser.add_argument('port', type=int, help='Listening port for HTTP Server')
  parser.add_argument('ip', help='HTTP Server IP')
  args = parser.parse_args()

  random.seed(1)

  server = SimpleHttpServer(args.ip, args.port)
  print('HTTP Server Running...........')
  server.start()
  server.waitForThread()
