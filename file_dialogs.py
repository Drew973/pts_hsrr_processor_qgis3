from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QFileDialog

from os import path

settings=QSettings('pts', 'fitter')


def load_file_dialog(ext='',caption=''):
    folder=settings.value('folder','',str)
    if folder=='':
        folder=path.expanduser('~\\Documents')#path to users documents

    p=QFileDialog.getOpenFileName(caption='UploadLoad File',filter='*'+ext+';;*',directory=folder)#path
    if p!='':
        settings.setValue('folder',path.dirname(p))#save folder in settings
        return p

    
def load_files_dialog(ext='',caption=''):
    folder=settings.value('folder','',str)
    if folder=='':
        folder=path.expanduser('~\\Documents')#path to users documents
    #paths=QFileDialog.getOpenFileNamesAndFilter(caption=caption, directory=folder, filter='*'+ext+';;*')#pyqt4
    paths=QFileDialog.getOpenFileNames(caption=caption, directory=folder, filter='*'+ext+';;*')#pyqt5

    if len(paths)>0:
        settings.setValue('folder',path.dirname(paths[-1]))#save folder in settings
        return paths[0]
    else:
        return []


def save_file_dialog(ext='',caption='',default_name=''):
    folder=settings.value('folder','',str)
    
    if folder=='':
        folder=path.expanduser('~\\Documents')#path to users documents

    p=QFileDialog.getSaveFileName(caption=caption,filter='*'+ext+';;*',directory=path.join(folder,default_name))[0]#(path,filter) for pyqt5
    #p=QFileDialog.getSaveFileName(caption=caption,filter='*'+ext+';;*',directory=path.join(folder,default_name))#(path,filter) for pyqt4

    print(p)
    
    if p!='':
        settings.setValue('folder',path.dirname(p))#save folder in settings
        return p


def filename(p):
    return path.splitext(path.basename(p))[0]
