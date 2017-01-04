import os
import subprocess

def create_bzip2_file(file_path):
  if not os.path.isfile(file_path + ".tmp.bz2"): 
    subprocess.call(["cp", file_path, file_path + ".tmp"])
    subprocess.call(["bzip2", file_path + ".tmp"])
  return file_path + ".tmp.bz2"

def create_hdt_file(input_file_path, output_file_path):
  if not os.path.isfile(output_file_path + ".hdt"):
    subprocess.call(["rdf2hdt", input_file_path, output_file_path + ".hdt"])
  return output_file_path + ".hdt"

def remove_file(file_path):
  if os.path.isfile(file_path):
    subprocess.call(["rm", file_path])
