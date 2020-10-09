from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QFileDialog

import os

settings=QSettings('pts', 'hsrr')


def load_file_dialog(ext='',caption=''):
    p=QFileDialog.getOpenFileName(caption='UploadLoad File',filter='*'+ext+';;*',directory=get_default_folder())#path
    if p!='':
        settings.setValue('folder',os.path.dirname(p))#save folder in settings
        return p

    
def load_files_dialog(ext='',caption=''):
    #paths=QFileDialog.getOpenFileNamesAndFilter(caption=caption, directory=folder, filter='*'+ext+';;*')#pyqt4
    paths=QFileDialog.getOpenFileNames(caption=caption, directory=get_default_folder(), filter='*'+ext+';;*')#pyqt5

    if len(paths)>0:
        settings.setValue('folder',os.path.dirname(paths[-1]))#save folder in settings
        return paths[0]
    else:
        return []


def save_file_dialog(ext='',caption='',default_name=''):
    p=QFileDialog.getSaveFileName(caption=caption,filter='*'+ext+';;*',directory=os.path.join(get_default_folder(),default_name))[0]#(path,filter) for pyqt5
    #p=QFileDialog.getSaveFileName(caption=caption,filter='*'+ext+';;*',directory=path.join(folder,default_name))#(path,filter) for pyqt4
    print(p)
    if p!='':
        settings.setValue('folder',os.path.dirname(p))#save folder in settings
        return p


def filename(p):
    return path.splitext(path.basename(p))[0]


def get_default_folder():
    folder=settings.value('folder','',str)
    if folder=='':
        folder=os.path.expanduser('~\\Documents')#path to users documents   
    return folder


def load_directory_dialog(ext='',caption=''):
    p=QFileDialog.getExistingDirectory(caption=caption, directory=get_default_folder())#pyqt5

    if p:
        settings.setValue('folder',p)#save folder in settings
        return p
    else:
        return []


def filter_files(folder,ext):
    res=[]
    for root, dirs, files in os.walk(folder):
        res+=[os.path.join(root,f) for f in files if os.path.splitext(f)[-1]==ext]
    return res
