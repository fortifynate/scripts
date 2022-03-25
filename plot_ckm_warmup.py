import os
import argparse
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from DataDictionary import DataDictionary

PACKET_HEADERS=["data_id","data_name","frame_num","timestamp"]
JSON_FILENAME = "DataDictionary/data_dictionary.json"

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

def generate_databreak_timestamps(csv_list, data_id, datadict_df, align_list):
  data_break_timestamps = []
  align_index = 0
  headers = get_headers_by_id(datadict_df, data_id)
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
      data_break_timestamps.append((last_timestamp,new_timestamp))
    datastream_df = datastream_df.append(next_df)
  return data_break_timestamps


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

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("csv_dir", help="data csv directory")
  parser.add_argument("-s", "--save", help="save output",
                      action="store_true")
  parser.add_argument("-m", "--mode", help="Plot Mode", choices=['chamber', 'temp', 'pump', 'rsvrlevel'], default="temp")
  parser.add_argument("--state", help="Add State Info", action='store_true')
  # comma separated list of ms timestamp offsets in between each csv file.
  parser.add_argument("--align", help="Align timestamps", type=str)
  parser.add_argument("--data-logger", help="Data Logger File", dest="data_logger")
  # offset data logger start to align with datastream timestamps
  parser.add_argument("--data-logger-offset", help="Data Logger Offset", default=0, type=int, dest="data_logger_offset")
  args = parser.parse_args()

  # attempt to locate data files
  ckm_csv = []
  rsvrlevel_csv = []
  rsvrtemp_csv = []
  rsvrleveldata_csv = []
  circag_csv = []
  resag_csv = []
  ambheat_csv = []
  for filename in os.listdir(args.csv_dir):
    if "Data_2000" in filename:
      ckm_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2100" in filename:
      rsvrlevel_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2101" in filename:
      rsvrtemp_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2150" in filename:
      rsvrleveldata_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2200" in filename:
      circag_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2300" in filename:
      resag_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2400" in filename:
      ambheat_csv.append(os.path.join(args.csv_dir, filename))

  align_list = []
  if args.align:
    align_list = [int(offset) for offset in args.align.split(',')]
    if len(align_list) != (len(ckm_csv) - 1):
      print("Number of align offsets(%d) must match the number of CSV files(%d)-1" % (len(align_list), len(ckm_csv)))
      exit()

  data_dict = load_data_dict()

  # create data frames and append any extra found files
  ckm_df = generate_datastream_df(ckm_csv, 2000, data_dict, align_list)
  rsvrlevel_df = generate_datastream_df(rsvrlevel_csv, 2100, data_dict, align_list)
  rsvrtemp_df = generate_datastream_df(rsvrtemp_csv, 2101, data_dict, align_list)
  rsvrleveldata_df = generate_datastream_df(rsvrleveldata_csv, 2150, data_dict, align_list)
  circag_df = generate_datastream_df(circag_csv, 2200, data_dict, align_list)
  resag_df = generate_datastream_df(resag_csv, 2300, data_dict, align_list)
  ambheat_df = generate_datastream_df(ambheat_csv, 2400, data_dict, align_list)
  if args.align:
    data_break_timestamps = generate_databreak_timestamps(ckm_csv, 2000, data_dict, align_list)

  # check if in full mode
  ckm_full_mode = not (ckm_df['ckm_status_mode'][0] == 1)

  if args.data_logger:
    data_logger_df = pd.read_csv(args.data_logger, parse_dates=[1])
    # assume data logs every 5 s (based on 12 samples per minute)
    print(args.data_logger_offset)
    data_logger_df['timestamp'] = data_logger_df['Number']*5000 + int(ckm_df['timestamp'].head(1))+args.data_logger_offset


  if args.mode == "chamber":
    fig = make_subplots(x_title="Timestamp(s)", rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02,
                        row_heights=[0.75, 0.25],
                        specs=[[{"secondary_y": False}], [{"secondary_y": False}]])
    fig.update_layout(title="CKM Warm Up - Chamber Temp")
    fig.update_yaxes(title_text="Temp (C)", row=1, col=1)
    fig.update_yaxes(title_text="Chamber Heat Mode", row=2, col=1,
                     tickvals=[1, 2, 3],
                     ticktext=['off', 'heat', 'overtemp'])
    fig.add_trace(
      go.Scatter(x=ambheat_df['timestamp']/1000, y=ambheat_df['ambheat_status_ambient_temp'], name='chamber temp'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=ambheat_df['timestamp']/1000, y=ambheat_df['ambheat_status_inlet_air_temp'], name='chamber inlet temp'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=ambheat_df['timestamp']/1000, y=ambheat_df['ambheat_status_state'], name='chamber heat mode', showlegend=False),
      row=2, col=1,
    )
  elif args.mode == "temp":
    fig = make_subplots(x_title="Timestamp(s)", rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02,
                        row_heights=[0.75, 0.25],
                        specs=[[{"secondary_y": False}], [{"secondary_y": False}]])
    fig.update_layout(title="CKM Warm Up - Temp")
    fig.update_yaxes(title_text="Temp (C)", row=1, col=1)
    fig.update_yaxes(title_text="Volume (mL)", row=2, col=1)
    fig.add_trace(
      go.Scatter(x=rsvrtemp_df['timestamp']/1000, y=rsvrtemp_df['rsvr_inlet_temp'], name='rsvr inlet temp'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrtemp_df['timestamp']/1000, y=rsvrtemp_df['rsvr_outlet_temp'], name='rsvr outlet temp'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=circag_df['timestamp']/1000, y=circag_df['circag_wall_temp'], name='circag wall temp'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=circag_df['timestamp']/1000, y=circag_df['circag_bottom_temp'], name='circag bottom temp'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=circag_df['timestamp']/1000, y=circag_df['circag_resin_temp'], name='circag resin temp'),
      row=1, col=1,
    )
    if ckm_full_mode:
      fig.add_trace(
        go.Scatter(x=resag_df['timestamp']/1000, y=resag_df['resag_wall_temp'], name='drawer wall temp'),
        row=1, col=1,
      )
      fig.add_trace(
        go.Scatter(x=resag_df['timestamp']/1000, y=resag_df['resag_resin_temp'], name='drawer resin temp'),
        row=1, col=1,
      )
    if args.data_logger:
      fig.add_trace(
        go.Scatter(x=data_logger_df['timestamp']/1000, y=data_logger_df['Wall Temp'], name='DataLogger Wall Temp'),
        row=1, col=1,
      )
      fig.add_trace(
        go.Scatter(x=data_logger_df['timestamp']/1000, y=data_logger_df['Base Temp'], name='DataLogger Base Temp'),
        row=1, col=1,
      )
    fig.add_trace(
      go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['rsvr_volume'], name='rsvr volume'),
      row=2, col=1,
    )
    fig.add_trace(
      go.Scatter(x=circag_df['timestamp']/1000, y=circag_df['circag_volume'], name='circag volume'),
      row=2, col=1,
    )
    fig.add_trace(
      go.Scatter(x=circag_df['timestamp']/1000, y=resag_df['resag_volume'], name='drawer volume'),
      row=2, col=1,
    )
    fig.add_trace(
      go.Scatter(x=ckm_df['timestamp']/1000, y=ckm_df['ckm_status_volume'], name='total volume'),
      row=2, col=1,
    )

  elif args.mode == "pump":
    if ckm_full_mode:
      secondary_y = True
    else:
      secondary_y = False
    fig = make_subplots(x_title="Timestamp(s)", rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02,
                        row_heights=[0.5, 0.5],
                        specs=[[{"secondary_y": False}], [{"secondary_y": secondary_y}]])
    fig.update_layout(title="CKM Warm Up - Pumps")
    fig.update_yaxes(title_text="Pump Speed (rpm)", row=1, col=1)
    fig.update_yaxes(title_text="Volume (mL)", row=2, col=1)
    if ckm_full_mode:
      fig.update_yaxes(title_text="Transfer Pump State", row=2, col=1, secondary_y=True)
    fig.add_trace(
      go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['rsvr_inlet_pump_speed'], name='inlet pump speed'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrtemp_df['timestamp']/1000, y=rsvrtemp_df['rsvr_outlet_pump_speed'], name='outlet pump speed'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['rsvr_volume'], name='rsvr volume'),
      row=2, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['rsvr_target_volume'], name='rsvr tgt volume'),
      row=2, col=1,
    )
    if ckm_full_mode:
      fig.add_trace(
        go.Scatter(x=resag_df['timestamp']/1000, y=resag_df['resag_pump_state'], name='Transfer Pump Mode speed'),
        row=2, col=1,
        secondary_y=True,
      )
      fig.add_trace(
        go.Scatter(x=circag_df['timestamp']/1000, y=circag_df['circag_volume'], name='circag volume'),
        row=2, col=1,
      )
      fig.add_trace(
        go.Scatter(x=circag_df['timestamp']/1000, y=resag_df['resag_volume'], name='drawer volume'),
        row=2, col=1,
      )

  elif args.mode == "rsvrlevel":
    if len(rsvrleveldata_csv) == 0:
      print ("Could not locate rsvrleveldata_csv(2150) data files in " + args.csv_dir)
      exit()
    if len(rsvrtemp_csv) == 0:
      print ("Could not locate rsvrtemp(2101) data files in " + args.csv_dir)
      exit()
    fig = make_subplots(x_title="Timestamp(s)", rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02,
                        row_heights=[0.75, 0.25],
                        specs=[[{"secondary_y": False}], [{"secondary_y": False}]])
    fig.update_layout(title="CKM Reservoir Level")
    fig.update_yaxes(title_text="Volume (mL)", row=1, col=1)
    fig.update_yaxes(title_text="Pump Speed (rpm)", row=2, col=1)
    fig.add_trace(
      go.Scatter(x=rsvrleveldata_df['update_time']/1000, y=rsvrleveldata_df['rsvrlvl_volume_target'], name='volume_target'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrleveldata_df['update_time']/1000, y=rsvrleveldata_df['rsvrlvl_volume'], name='total_volume'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrleveldata_df['update_time']/1000, y=rsvrleveldata_df['rsvrlvl_print_head_volume'], name='print_head_volume'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrleveldata_df['update_time']/1000, y=rsvrleveldata_df['rsvrlvl_part_volume'], name='part_volume'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrleveldata_df['update_time']/1000, y=rsvrleveldata_df['rsvrlvl_resin_volume'], name='resin_volume'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrleveldata_df['update_time']/1000, y=rsvrleveldata_df['rsvrlvl_pump_speed'], name='inlet pump speed'),
      row=2, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrtemp_df['timestamp']/1000, y=rsvrtemp_df['rsvr_outlet_pump_speed'], name='outlet pump speed'),
      row=2, col=1,
    )

  else:
    print ("Unrecognized plot mode: " + args.mode)
    exit()

  # annotate with ckm states
  # find start/stop of each state
  if args.state:
    active_df = ckm_df.loc[ckm_df['ckm_status_state'] == 9]
    active_min = active_df["timestamp"].min()/1000
    active_max = active_df["timestamp"].max()/1000
    if not pd.isna(active_min) and not pd.isna(active_max):
      fig.add_vrect(x0=active_min, x1=active_max,
                    annotation_text="active", annotation_position="top left",
                    fillcolor="green", opacity=0.25, line_width=0)

    circwait_df = ckm_df.loc[ckm_df['ckm_status_state'] == 8]
    circwait_min = circwait_df["timestamp"].min()/1000
    circwait_max = circwait_df["timestamp"].max()/1000
    if (circwait_max-circwait_min)>5:
      fig.add_vrect(x0=circwait_min, x1=circwait_max,
                    annotation_text="circ_wait", annotation_position="top left",
                    fillcolor="yellow", opacity=0.25, line_width=0)

    prime_df = ckm_df.loc[ckm_df['ckm_status_state'] == 7]
    prime_min = prime_df["timestamp"].min()/1000
    prime_max = prime_df["timestamp"].max()/1000
    if (prime_max-prime_min)>5:
      fig.add_vrect(x0=prime_min, x1=prime_max,
                    annotation_text="prime", annotation_position="top left",
                    fillcolor="orange", opacity=0.25, line_width=0)

    preheat_df = ckm_df.loc[ckm_df['ckm_status_state'] == 6]
    preheat_min = preheat_df["timestamp"].min()/1000
    preheat_max = preheat_df["timestamp"].max()/1000
    if (preheat_max-preheat_min)>5:
      fig.add_vrect(x0=preheat_min, x1=preheat_max,
                    annotation_text="preheat", annotation_position="top left",
                    fillcolor="red", opacity=0.25, line_width=0)

    fill_df = ckm_df.loc[ckm_df['ckm_status_state'] == 5]
    fill_min = fill_df["timestamp"].min()/1000
    fill_max = fill_df["timestamp"].max()/1000
    if (fill_max-fill_min)>5:
      fig.add_vrect(x0=fill_min, x1=fill_max,
                    annotation_text="fill", annotation_position="top left",
                    fillcolor="blue", opacity=0.25, line_width=0)

  if args.align:
    for timestamp in data_break_timestamps:
      fig.add_vrect(x0=timestamp[0]/1000, x1=timestamp[1]/1000,
                    annotation_text="FH Reset", annotation_position="top left",
                    fillcolor="red", opacity=0.25, line_width=0)

  # Save the html plot
  if args.save == True:
    fig.write_html(os.path.join(args.csv_dir, "ckm_warm_up_" + args.mode + ".html"))
  fig.show()
