import africastalking
import logging
import time
import os

from gtts import gTTS


class smshandler():


    def sendsms(self, name):
        apikey = "983a36a35b591a83c382ebe9a1a33e7ee3a5e0e98981e6f5d47da8e87f176798"
        username = "sandbox"
        # sender_id = "mysenderid"
        africastalking.initialize(username, apikey)
        message_recipient = ['+254705066102']
        sms = africastalking.SMS
        

        currentTime = int(time.strftime('%H'))

        if currentTime < 12 :
            greeting = "Goodmorning "
        elif currentTime > 12 :
            greeting = "Good afternoon "
        elif currentTime > 18 :
            greeting = "Good evening "
            
        smsfooter = " welcome home"
        authname  = name
        smsheader = greeting
        smspayload = smsheader + (authname) + smsfooter 
        
        #text to speech conversion
        file = "test1.mp3"
        
        
        #initialize tts, create mp3 and play
        tts = gTTS(smspayload, 'en')
        tts.save(file)
        os.system("mpg123 " + file)


        smsresponse = sms.send(smspayload, message_recipient)
        logging.debug(smsresponse)