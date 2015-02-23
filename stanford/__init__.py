import os

def get_path():
  my_path = os.path.dirname(os.path.abspath(__file__)) + "/core"
  return my_path

