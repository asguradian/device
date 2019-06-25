from Data import Stream
import jsonpickle as pk
def encodeImage(image,date,deviceId):
  stream= Stream(image,date,deviceId)
  return stream
