import os, json
from DataDictionary import DataDictionary
import pandas as pd

JSON_FILENAME = "DataDictionary/data_dictionary.json"
PACKET_HEADERS=["data_id","data_name","frame_num","timestamp"]

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
  headers = PACKET_HEADERS + datadict_df[datadict_df["ID"] == data_id]["Enum Name"].str.lower().to_list()
  return headers

def generate_datastream_df(csv_list, data_id, datadict_df, align_list=[]):
  align_index = 0
  headers = get_headers_by_id(datadict_df, data_id)
  if len(csv_list) == 0:
    return pd.DataFrame(columns = headers)
  datastream_df = pd.read_csv(csv_list[0], names=headers)
  for csv_file in csv_list[1:]:
    next_df = pd.read_csv(csv_file, names=headers)
    # realign timestamps with provided offsets
    if len(align_list) > 0:
      last_timestamp = int(datastream_df['timestamp'].tail(1))
      new_timestamp = last_timestamp+align_list[align_index]
      timestamp_offset = int(next_df['timestamp'].head(1)) - (new_timestamp)
      next_df['timestamp'] = next_df['timestamp'].sub(timestamp_offset)
      align_index+=1
    datastream_df = datastream_df.append(next_df)
  return datastream_df
# DATA_ID_MAP={
#   "ZLOAD"         : 1004,
#   "CKM_STATUS"    : 2000,
#   "RSVR_STATUS0"  : 2100, #RSVR_LEVEL
#   "RSVR_STATUS1"  : 2101, #RSVR_TEMP
#   "RSVR_DATA0"    : 2150,
#   "CIRCAG_STATUS" : 2200,
#   "CIRCAG_DATA0"  : 2250,
#   "AMBHEAT_STATUS": 2400,
# }

# DATA_HEADER_MAP= {
#   DATA_ID_MAP["ZLOAD"]             : ["z_arm_load",
#                                       "z_position",
#                                       "z_arm_load_unfiltered",
#                                       "z_bp_position",
#                                       ],
#   DATA_ID_MAP["CKM_STATUS"]        : ["state",
#                                       "mode",
#                                       "fault_bitmask",
#                                       "volume",
#                                       "total_capacity",
#                                       "fault_level",
#                                       "clean_flags",
#                                       "purge_mode",
#                                       "transfer_state"],
#   DATA_ID_MAP["RSVR_STATUS0"]      : ["status_bits",
#                                       "level",
#                                       "volume",
#                                       "target_volume",
#                                       "inlet_pump_mode",
#                                       "inlet_pump_speed",
#                                       "clamps_open"],
#   DATA_ID_MAP["RSVR_STATUS1"]      : ["inlet_temp",
#                                       "outlet_temp",
#                                       "outlet_pump_mode",
#                                       "outlet_pump_speed",
#                                       "status_bits"],
#   DATA_ID_MAP["RSVR_DATA0"]        : ["update_time",
#                                       "target_level",
#                                       "raw_level",
#                                       "pump_speed",
#                                       "volume_target",
#                                       "total_volume",
#                                       "print_head_volume",
#                                       "part_volume",
#                                       "resin_volume"],
#   DATA_ID_MAP["CIRCAG_STATUS"]     : ["status_bits",
#                                       "heat_mode",
#                                       "motor_mode",
#                                       "meas_mode",
#                                       "resin_temp",
#                                       "wall_temp",
#                                       "level",
#                                       "volume",
#                                       "agitator_speed",
#                                       "bottom_temp"],
#   DATA_ID_MAP["CIRCAG_DATA0"]      : ["update_time",
#                                       "heat_mode",
#                                       "tgt_body_temp",
#                                       "body_temp",
#                                       "tgt_resin_temp",
#                                       "resin_temp",
#                                       "inlet_temp",
#                                       "duty_cycle"],
#   DATA_ID_MAP["AMBHEAT_STATUS"]    : ["state",
#                                       "temp",
#                                       "inlet_temp"],
# }
