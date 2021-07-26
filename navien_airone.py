from os import POSIX_FADV_WILLNEED
import sys
import ssl
import time
import datetime
import logging, traceback
import paho.mqtt.client as mqtt
import json
import _thread

from . import protocol
#import protocol

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
log_format = logging.Formatter('%(asctime)s – %(name)s – %(levelname)s – %(message)s')
handler.setFormatter(log_format)
logger.addHandler(handler)


class NavienAirone:
    def __init__(
        self,
        brokeraddr: str = "a1folro8nc3ln2-ats.iot.ap-northeast-2.amazonaws.com",
        ca = "/usr/local/lib/python3.8/site-packages/navien_airone/cert/AmazonRootCA1.pem.txt",
        cert = "/usr/local/lib/python3.8/site-packages/navien_airone/cert/8afd5a2ab8-certificate.pem.crt",
        private = "/usr/local/lib/python3.8/site-packages/navien_airone/cert/8afd5a2ab8-private.pem.key",
        port: int = 8883,
        deviceid: str = None,
    ):
        self._brokeraddr = brokeraddr
        self._port = port
        self._ca = ca
        self._cert = cert
        self._private = private
        self._modelcode = "2"
        self._deviceid = deviceid
        self._pubaddr = f"cmd/rc/{self._modelcode}/{self._deviceid}/remote/"
        self._subaddr = f"cmd/rc/{self._modelcode}/{self._deviceid}/remote/"

        self._sub_client = None
        self._pub_client = None
        self._payload = None
        self._topic = None


    def tls_setting(self):
        try:
            #debug print opnessl version
            logger.info("open ssl version:{}".format(ssl.OPENSSL_VERSION))
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(cafile=self._ca)
            ssl_context.load_cert_chain(certfile=self._cert, keyfile=self._private)
            logger.info("debugging:{}".format(ssl_context))
            return  ssl_context

        except Exception as e:
            print("exception tls_setting(): ",e)
            raise e

    def sub_threading(self):
        try:
            _thread.start_new_thread(self.create_subscriber,(self._topic,))
            logger.info("@@@@@@@@@@@@@@@@@@@@@@@@@@start_new_thread create_subscriber@@@@@@@@@@@@@@@@@@@@@@@")
        except Exception as e:
            logger.info(f"navien start_new_thread error: {e}")
        

    def create_client(self, on_message):
        def on_connect(client, userdata, flags, rc):
            client.subscribe(self._subaddr)

            client = mqtt.Client("listener")
            client.on_connect = on_connect
            client.on_message = on_message
            client.connect(self._brokeraddr, port=8883)
            client.loop_forever()
            self._client = client

    def create_subscriber(self, protocol):
        def on_connect(client, userdata, flags, rc):
            logger.info(f"subscriber_on_cnnect!")
            #topic = self._subaddr+protocol+'/res'
            topic = self._subaddr+"status"+'/res'
            client.subscribe(topic)
            logger.info(f"create_subscriber topic: {topic}")
            logger.info("on_connect and sub!")

        def on_message(client,userdata,msg):
            self._payload = msg.payload
            logger.info(f"navien sub_on_message! self._payload:{self._payload}")
            #self._pub_client.disconnect()


        self._sub_client = mqtt.Client("subscriber")
        ssl_context = self.tls_setting()
        self._sub_client.tls_set_context(context = ssl_context)
        self._sub_client.on_connect = on_connect
        self._sub_client.on_message = on_message
        self._sub_client.connect(self._brokeraddr, port=8883)
        #self._client = sub_client
        logger.info("sub_loop_start()")
        self._sub_client.loop_forever()
        

        #self.publish_once(self,request)
        
        #time.sleep(0.6)
        
    def close_client(self):
        if self._client:
            self._client.disconnect()
            self._client = None
            logger.info("close_client()!!")

    def stop_client(self):
        if self._client:
            self._client.loop_stop()
            self._client = None
            logger.info("stop_client()!!")


    def publish_once(self,requesttopic,body):
        
        """
        request = {
                "clientId": "98D8630F60FA146E",
                "sessionId": "",
                "requestTopic":"cmd/rc/2/98D8630F60FA146E/remote/did",
                "responseTopic": "cmd/rc/2/98D8630F60FA146E/remote/did/res"
                }
        """
        
        def on_disconnect(client,userdata,flag):
            logger.info("disconnected!!")

        def on_publish(client,userdata,result):
            #time.sleep(5)
            self._pub_client.disconnect()
            logger.info("on_publish!!")

        def on_connect(client,userdata,flag,rc):
            while True:
                    try:
                        logger.info("navienmsg try to publish! topic: {0}, request: {1}".format(self._pubaddr+requesttopic, json.dumps(body)))
                        self._pub_client.publish(topic=self._pubaddr+requesttopic, payload=json.dumps(body))
                        break
                    except Exception as e:
                        print("publish error: ",e)
                        time.sleep(10)
            
            logger.info("on_connect! and pub message")
        
        #self.sub_threading()
        self._pub_client = mqtt.Client("pub")
        ssl_context = self.tls_setting()
        self._pub_client.tls_set_context(context=ssl_context)
        self._pub_client.on_connect = on_connect
        self._pub_client.on_publish = on_publish
        self._pub_client.on_disconnect = on_disconnect
        self._pub_client.connect(self._brokeraddr, self._port)
        self._pub_client.loop_forever()
        #self._client.loop_stop()
    
    def build_topic(self,requesttopic):
        return protocol.build_topic(requesttopic)
    
    def build_payload(self,requesttopic,operationmode,optionmode:'optionmode or schedule time',windlevel:'windlevel or deepsleep-time'):
        return protocol.build_payload(requesttopic,operationmode,optionmode,windlevel)

    

if __name__ == '__main__':
    #98D8630F60FA146E
    #98D8630F3D5E14D5
    request1 = {
                "clientId": "98D8630F60FA146E",
                "sessionId": "",
                "requestTopic":"cmd/rc/2/98D8630F60FA146E/remote/power",
                "responseTopic": "cmd/rc/2/98D8630F60FA146E/remote/status/res",
                "request":{"power":2}
                }
    
    request2 = {
                "clientId": "98D8630F60FA146E",
                "sessionId": "",
                "requestTopic":"cmd/rc/2/98D8630F60FA146E/remote/did",
                "responseTopic": "cmd/rc/2/98D8630F60FA146E/remote/did/res"
                }

    deviceid = "98D8630F60FA146E"
    navien_instance = NavienAirone(deviceid=deviceid)
    navien_instance.publish_once(protocol=navien_instance.build_protocol(requesttopic="device_status"), body=request1)
    navien_instance.publish_once(protocol=navien_instance.build_protocol(requesttopic="power"), body=request2)
    #_thread.start_new_thread(navien_instance.publish_once,(topic,request1))
    #navien_instance.publish_once(protocol=topic, body=request2)
    print(f"self._payload: {navien_instance._payload}")
