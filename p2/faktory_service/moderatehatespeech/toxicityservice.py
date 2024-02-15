import requests
import logging
import os
from dotenv import load_dotenv
from datetime import date
load_dotenv()




class ToxicityService:
  __BASE_URL = 'https://api.moderatehatespeech.com/api/v1/'
  def __init__(self):
    self.__s = requests.session()
    self.__s.headers = {
    'Content-Type': 'application/json'
    }

  def add_token(self,token):
    self.__token = token
    
  def __create_body(self,text):
    return {
        "text":text,
        "token":self.__token
    }

  def moderate(self,text):
    body = self.__create_body(text)
    end_point = self.__BASE_URL + 'moderate/'
    return self.__execute(end_point, body)


  def report(self, text, intended):
    if intended!=1 or intended!=2:
      return "Unsupported Label"

    body = self.__create_body(text)
    body['intended'] = intended
    end_point = self.__BASE_URL + 'report/'
    return self.__execute(end_point, body)


  def __execute(self,end_point, body):
    try:
      resp = self.__s.post(
          url = end_point,
          json = body
      )
      logging.info(f'request successful: {resp.text}')
      return resp.json()
    except requests.exceptions.RequestException as e:
      logging.error(f'request failed: {e}')
      print(f'request failed: {e}')
      raise Exception(f'request failed: {e}')
