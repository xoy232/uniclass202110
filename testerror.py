import traceback
import sys

try :
    abc
    
    111
    
except:
    print("sys :",sys.exc_info())
    print("traceback : ",traceback.format_exc())