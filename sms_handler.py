import africastalking
import logging

class smshandler():


    def sendsms(self, name):
        apikey = "983a36a35b591a83c382ebe9a1a33e7ee3a5e0e98981e6f5d47da8e87f176798"
        username = "sandbox"
        # sender_id = "mysenderid"
        africastalking.initialize(username, apikey)
        message_recipient = ['+254705066102']
        sms = africastalking.SMS
        smsheader = "Hello, authorized: "
        authname  = name
        smspayload = smsheader + (authname)
        smsresponse = sms.send(smspayload, message_recipient)
        logging.debug(smsresponse)