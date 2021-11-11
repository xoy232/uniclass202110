import os
import shutil
import traceback


def check_filepath(Folder, FileName):
    if os.path.exists(Folder):
        if os.path.isdir(Folder):
            print('check folder is ok')
        else:
            print(Folder + ' : 不是資料夾')
            return -1
    else:
        print('將建立不存在的資料夾')
        try:
            os.mkdir(Folder)
        except:
            print(traceback.format_exc())
            return -1

    if os.path.exists(FileName):
        if os.path.isfile(FileName):
            print(FileName + '檔案存在')
            try:
                os.remove(FileName)
                print('砍掉')
            except:
                print(traceback.format_exc())
                return -1
        else:
            print(FileName + '  不是檔案')
            return -1
    else:
        print(f'{FileName} 路徑沒問題')


def RmFile(filename):
    try:
        os.remove(filename)
    except:
        pass

def ReadFolderFile(Folderpath):
    return (f"{Folderpath}/{i}" for i in os.listdir(Folderpath))
    

def RmFolder(Folderpath):
    try:
        shutil.rmtree(Folderpath)
    except:
        pass