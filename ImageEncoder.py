from Data import Stream
import jsonpickle as pk
def encodeImage(image,date,deviceId,fileName):
  stream= Stream(image,date,deviceId,fileName)
  return stream
