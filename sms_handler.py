import africastalking
import logging

class smshandler():


    def sendsms(self, name):
        apikey = "823aa862eec512244d026e18f269f14643882dc02124996d5d0d0d4eb28e4f81"
        username = "sandbox"
        # sender_id = "mysenderid"
        africastalking.initialize(username, apikey)
        message_recipient = ['+254720123456']
        sms = africastalking.SMS
        smsheader = "Hello, authorized: "
        authname  = name
        smspayload = smsheader.join(authname)
        smsresponse = sms.send(smspayload, message_recipient)
        logging.debug(smsresponse)