import logging
import datetime
import os 

HOME = os.getcwd()

def setlog(LOG,LEVEL="error"):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
    	'[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    	datefmt='%Y%m%d %H:%M:%S')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    log_filename = datetime.datetime.now().strftime(str(HOME+'/'+f"{datetime.date.today()}"+'.log'))
    fh = logging.FileHandler(log_filename)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)
    if LEVEL == "debug" or LEVEL ==  2 :
        logging.debug(LOG, exc_info=True)
    elif LEVEL == "info" or LEVEL == 5 :
        logging.info(LOG, exc_info=True)
    elif LEVEL == "warning" or LEVEL == 4  :
        logging.warning(LOG, exc_info=True)
    elif LEVEL == "error" or LEVEL ==  1:
        logging.error(LOG, exc_info=True)
    else :
        logging.critical(LOG, exc_info=True)
    



if __name__ == "__main__":
    import cv2
    import sys
    try:
        aaaa

    except:
        setlog(sys.exc_info(),LEVEL=0)