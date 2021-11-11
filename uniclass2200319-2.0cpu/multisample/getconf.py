import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import os 

HOME = os.getcwd()

nowfolder = f"{HOME}/multisample/mutiimg"

files = os.listdir(nowfolder)


allfiles = tuple([ (x[0],f"{nowfolder}/{x[1]}") for x in enumerate(files) ])


with open(f"{HOME}/multisample/image.yaml","w") as f :
    print(yaml.dump(allfiles,f,Dumper=Dumper))

