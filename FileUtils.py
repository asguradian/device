

import os

def removeFile(fileName):
 if(os.path.exist(fileName)):
  os.path.remove(fileName)
