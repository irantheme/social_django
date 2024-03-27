import random
import core.config as config
import requests


class Utilities:

    def __init__(self):
        '''Initialize'''
        self.charactors = '1234567890abcdefghijklmnopqrsvutwxyz!@#$%^&*'
        self.API_KEY = config.API_KEY
        self.__URL = f'https://api.kavenegar.com/v1/{self.API_KEY}/verify/lookup.json'

    def create_password(self, length):
        '''Create password simple'''
        password = ''
        for i in range(length):
            num = random.randint(0, (len(self.charactors) - 1))
            password += self.charactors[num]
        return password

    def send_message(self, number, code):
        ''' Sending message to phone number with api key '''
        # Create format for send
        payload = {
            'receptor': number,
            'token': code,
            'template': 'password'
        }
        # Send message
        response = requests.post(self.__URL, data=payload)
        return response
