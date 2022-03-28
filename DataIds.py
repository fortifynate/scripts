import os, json
from DataDictionary import DataDictionary
import pandas as pd
import numpy as np

JSON_FILENAME = "DataDictionary/data_dictionary.json"
PACKET_HEADERS=["data_id","data_name","frame_num","timestamp"]

# use converters to skip lines that have corrupted values (bad float prints)
# example: 2300,RESAG_STATUS,4986,36004589,3168,3,1,1,35.5,38.4,0.0,89.5.1f,0,5.0,0,0
def int_converter(value_string):
  try:
    return np.int32(value_string)
  except:
    return None

def float_converter(value_string):
  try:
    return np.float64(value_string)
  except:
    return None

def load_data_dict():
  data_dict = DataDictionary.DataDictionary()
  json_filepath =   json_filepath = os.path.join(os.path.dirname(__file__), JSON_FILENAME)
  with open(json_filepath, 'r') as json_file:
    print ("Loading data dictionary from " + json_filepath)
    dict_json = json.load(json_file)
    DataDictionary.json_to_controller_dictionary(data_dict.core, dict_json['core'])
    DataDictionary.json_to_controller_dictionary(data_dict.pmc, dict_json['pmc3'])
  return data_dict.to_df()

def get_headers_by_id(datadict_df, data_id):
  rows = datadict_df[datadict_df["ID"] == data_id]
  col_names = rows["Enum Name"].str.lower().to_list()
  headers = PACKET_HEADERS + col_names
  convert_functions = [float_converter if x=='FLOAT' else int_converter for x in rows["Var Type"].to_list()]
  converters = dict(zip(col_names,convert_functions))
  return (headers, converters)

def generate_datastream_df(csv_list, data_id, datadict_df, align_list=[]):
  align_index = 0
  (headers, converters) = get_headers_by_id(datadict_df, data_id)
  if len(csv_list) == 0:
    return pd.DataFrame(columns = headers)
  datastream_df = pd.read_csv(csv_list[0], names=headers, converters=converters, on_bad_lines='skip')
  for csv_file in csv_list[1:]:
    next_df = pd.read_csv(csv_file, names=headers, converters=converters, on_bad_lines='skip')
    # realign timestamps with provided offsets
    if len(align_list) > 0:
      last_timestamp = int(datastream_df['timestamp'].tail(1))
      new_timestamp = last_timestamp+align_list[align_index]
      timestamp_offset = int(next_df['timestamp'].head(1)) - (new_timestamp)
      next_df['timestamp'] = next_df['timestamp'].sub(timestamp_offset)
      align_index+=1
    datastream_df = pd.concat([datastream_df, next_df])
  return datastream_df
