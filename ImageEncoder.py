from Data import Stream
import jsonpickle as pk
def encodeImage(image,date,deviceId,imageHash):
  stream= Stream(image,date,deviceId,imageHash)
  return stream
