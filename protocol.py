import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
log_format = logging.Formatter('%(asctime)s – %(name)s – %(levelname)s – %(message)s')
handler.setFormatter(log_format)
logger.addHandler(handler)

"""Responses to all remote controls are received ~/status/res"""

"""
=========================================TOPIC===============================================
"""

device_information = "did"
device_status = "status"
power = "power"
change_mode = "change-mode"
schedule = "schedule"
deep_sleep = "deep-sleep"

"""
======================================BODY.request===========================================
1)power on/off
2)청정환기 모드 및 바람세기 설정
3)실내청정 모드 및 바람세기 설정
4)자동모드 설정 및 바람세기 설정
5)예약설정 및 숙면설정
"""

power_off = {"power":1}
power_on = {"power":2}

"""Change_Mode"""
operation_mode_standby = {"operationMode":1}
operation_mode_airconditioning = {"operationMode":2}
operation_mode_generalventilation = {"operationMode":4}
operation_mode_exhaust = {"operationMode":5}
operation_mode_cooking = {"operationMode":6}
operation_mode_cleaning = {"operationMode":7}
operation_mode_aircleaning = {"operationMode":8}
operation_mode_yellowdustcleaning = {"operationMode":9}
operation_mode_heating = {"operationMode":10}
operation_mode_humidification = {"operationMode":11}
operation_mode_automaticoperation = {"operationMode":12}
operation_mode_bronchialprotection = {"operationMode":13}
operation_mode_skinprotection = {"operationMode":14}
operation_mode_airsupply = {"operationMode":15}

"""option_mode"""
nothing = {"optionMode":1}
turbo = {"optionMode":2}
powersaving = {"optionMode":3}
deepsleep = {"optionMode":4}

"""wind_level"""
notset = {"windLevel":0}
weakwind = {"windLevel":1}
heavywind = {"windLevel":2}
mightywind = {"windLevel":3}
autowind = {"windLevel":4}

"""Schedule"""
enable_power_off = {"enable":1}
enable_power_on = {"enable":2}
enable_disable_reservation = {"enable":3} #If you set this field to 3, please set scheduleTime field to zero

scheduletime_total_minutes = {"scheduleTime":f""} #Total minutes is the value converted from 24 hours into minutes.(ex.140 => am 2:20 )


"""Deep Sleep"""
enable_deepsleep_power_off = {"enable":1}
enable_deepsleep_power_on = {"enable":2}
starttime_total_minutes = {"startTime":f""} #as decimal format, same as schedule
endtime_total_minutes = {"endTime":f""} #as decimal format, same as schedule

def convert_string_to_date(optionmode):
    #ex) 14:30
    temp = optionmode.split(':')
    result = (int(temp[0]) * 60) + (int(temp[1]))
    return result

def build_topic(requesttopic):
    return globals()[requesttopic]


def build_payload(requesttopic,operationmode,optionmode,windlevel):
        try:
            requesttopic = globals()[requesttopic]
            operationmode = globals()[operationmode]
            
            payload = {}
            payload['clientId'] = "98D8630F60FA146E"
            payload['sessionId'] = ""
            payload['requestTopic'] = f"cmd/rc/2/98D8630F60FA146E/remote/{requesttopic}"
            payload['responseTopic'] = "cmd/rc/2/98D8630F60FA146E/remote/status/res"
            
            if requesttopic == 'power':
                payload['request'] = operationmode
                return payload

            if requesttopic == 'schedule':
                ## should be stirng convert to time
                optionmode = convert_string_to_date(optionmode)
                operationmode.update({"scheduleTime":optionmode})
                payload['request'] = operationmode
                return payload

            if requesttopic == 'deep-sleep': #not deep_sleep
                ## should be stirng convert to time
                optionmode = convert_string_to_date(optionmode)
                operationmode.update({"startTime":optionmode})
                windlevel = convert_string_to_date(windlevel)
                operationmode.update({"endTime":optionmode + windlevel}) #include string ','
                payload['request'] = operationmode
                return payload

            optionmode = globals()[optionmode]
            operationmode.update(optionmode)
            
            windlevel = globals()[windlevel]
            operationmode.update(windlevel)

            payload['request'] = operationmode

            logger.info(f"navienmsg payload7 {payload}")
            
            return payload
        
        except Exception as e:
            logger.info(f"navienmsg error in protocol.py {e}")