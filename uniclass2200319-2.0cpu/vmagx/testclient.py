from multiprocessing.connection import Client


address = ("localhost",12000)

for i in range(11001,11501) :
    try :
        with Client(("192.168.50.102",i), authkey=b'secret password') as client:
            client.recv()
            client.send("0")
    except:
        pass
        
# with Client(("192.168.50.102",12000), authkey=b'secret password') as client:
#     data = client.recv()
#     client.send("0")
# print(data[0])
# print(data[2])
    
    