

import os

def removeFile(fileName):
 if(os.path.exists(fileName)):
  os.remove(fileName)
