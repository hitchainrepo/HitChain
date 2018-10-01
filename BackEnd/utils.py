import datetime

def getCurrentTime():
    create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return create_time