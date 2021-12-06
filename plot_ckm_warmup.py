import os
import argparse
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from DataIds import *

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("csv_dir", help="data csv directory")
  parser.add_argument("-s", "--save", help="save output",
                      action="store_true")
  parser.add_argument("-m", "--mode", help="Plot Mode", choices=['chamber', 'lvtemp', 'lvpump'], default="lvtemp")
  parser.add_argument("--state", help="Add State Info", action='store_true')
  parser.add_argument("--align", help="Align timestamps", type=str)
  parser.add_argument("--data-logger", help="Data Logger File", dest="data_logger")
  parser.add_argument("--data-logger-offset", help="Data Logger Offset", default=0, type=int, dest="data_logger_offset")
  args = parser.parse_args()

  # attempt to locate data files
  ckm_csv = []
  rsvrlevel_csv = []
  rsvrtemp_csv = []
  circag_csv = []
  ambheat_csv = []
  for filename in os.listdir(args.csv_dir):
    if "Data_2000" in filename:
      ckm_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2100" in filename:
      rsvrlevel_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2101" in filename:
      rsvrtemp_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2200" in filename:
      circag_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2400" in filename:
      ambheat_csv.append(os.path.join(args.csv_dir, filename))

  if args.align:
    align_list = [int(offset) for offset in args.align.split(',')]
    if len(align_list) != (len(ckm_csv) - 1):
      print("Number of align offsets(%d) must match the number of CSV files(%d)-1" % (len(align_list), len(ckm_csv)))
      exit()
  data_break_timestamps = []
  # create data frames and append any extra found files
  align_index = 0
  ckm_df = pd.read_csv(ckm_csv[0], names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["CKM_STATUS"]])
  for csv_file in ckm_csv[1:]:
    next_df = pd.read_csv(csv_file, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["CKM_STATUS"]])
    # realign timestamps with an offset of 5s
    if args.align:
      last_timestamp = int(ckm_df['timestamp'].tail(1))
      new_timestamp = last_timestamp+align_list[align_index]
      timestamp_offset = int(next_df['timestamp'].head(1)) - (new_timestamp)
      next_df['timestamp'] = next_df['timestamp'].sub(timestamp_offset)
      align_index+=1
      data_break_timestamps.append((last_timestamp,new_timestamp))
    ckm_df = ckm_df.append(next_df)

  align_index = 0
  rsvrlevel_df = pd.read_csv(rsvrlevel_csv[0], names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["RSVR_STATUS0"]])
  for csv_file in rsvrlevel_csv[1:]:
    next_df = pd.read_csv(csv_file, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["RSVR_STATUS0"]])
    # realign timestamps with an offset of 5s
    if args.align:
      last_timestamp = int(rsvrlevel_df['timestamp'].tail(1))
      timestamp_offset = int(next_df['timestamp'].head(1)) - (last_timestamp + align_list[align_index])
      next_df['timestamp'] = next_df['timestamp'].sub(timestamp_offset)
      align_index+=1
    rsvrlevel_df = rsvrlevel_df.append(next_df)

  align_index = 0
  rsvrtemp_df = pd.read_csv(rsvrtemp_csv[0], names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["RSVR_STATUS1"]])
  for csv_file in rsvrtemp_csv[1:]:
    next_df = pd.read_csv(csv_file, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["RSVR_STATUS1"]])
    # realign timestamps with an offset of 5s
    if args.align:
      last_timestamp = int(rsvrtemp_df['timestamp'].tail(1))
      timestamp_offset = int(next_df['timestamp'].head(1)) - (last_timestamp + align_list[align_index])
      next_df['timestamp'] = next_df['timestamp'].sub(timestamp_offset)
      align_index+=1
    rsvrtemp_df = rsvrtemp_df.append(next_df)

  align_index = 0
  circag_df = pd.read_csv(circag_csv[0], names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["CIRCAG_STATUS"]])
  for csv_file in circag_csv[1:]:
    next_df = pd.read_csv(csv_file, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["CIRCAG_STATUS"]])
    # realign timestamps with an offset of 5s
    if args.align:
      last_timestamp = int(circag_df['timestamp'].tail(1))
      timestamp_offset = int(next_df['timestamp'].head(1)) - (last_timestamp + align_list[align_index])
      next_df['timestamp'] = next_df['timestamp'].sub(timestamp_offset)
      align_index+=1
    circag_df = circag_df.append(next_df)

  if len(ambheat_csv) > 0:
    align_index = 0
    ambheat_df = pd.read_csv(ambheat_csv[0], names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["AMBHEAT_STATUS"]])
    for csv_file in ambheat_csv[1:]:
      next_df = pd.read_csv(csv_file, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["AMBHEAT_STATUS"]])
      # realign timestamps with an offset of 5s
      if args.align:
        last_timestamp = int(ambheat_df['timestamp'].tail(1))
        timestamp_offset = int(next_df['timestamp'].head(1)) - (last_timestamp + align_list[align_index])
        next_df['timestamp'] = next_df['timestamp'].sub(timestamp_offset)
        align_index+=1
      ambheat_df = ambheat_df.append(next_df)

  if args.data_logger:
    data_logger_df = pd.read_csv(args.data_logger, parse_dates=[1])
    # assume data logs every 5 s (based on 12 samples per minute)
    print(args.data_logger_offset)
    data_logger_df['timestamp'] = data_logger_df['Number']*5000 + int(ckm_df['timestamp'].head(1))+args.data_logger_offset


  if args.mode == "chamber":
    if len(ambheat_csv) == 0:
      # ambient heat data required for chamber plot
      print ("Could not locate chamber(2400) data files in " + arg.csv_dir);
      exit()
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
      go.Scatter(x=ambheat_df['timestamp']/1000, y=ambheat_df['temp'], name='chamber temp'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=ambheat_df['timestamp']/1000, y=ambheat_df['inlet_temp'], name='chamber inlet temp'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=ambheat_df['timestamp']/1000, y=ambheat_df['state'], name='chamber heat mode', showlegend=False),
      row=2, col=1,
    )
  elif args.mode == "lvtemp":
    if len(rsvrlevel_csv) == 0:
      print ("Could not locate rsvrlevel(2100) data files in " + args.csv_dir)
      exit()
    if len(rsvrtemp_csv) == 0:
      print ("Could not locate rsvrtemp(2101) data files in " + args.csv_dir)
      exit()
    if len(circag_csv) == 0:
      print ("Could not locate circag(2200) data files in " + args.csv_dir)
      exit()

    fig = make_subplots(x_title="Timestamp(s)", rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02,
                        row_heights=[0.75, 0.25],
                        specs=[[{"secondary_y": False}], [{"secondary_y": False}]])
    fig.update_layout(title="CKM Warm Up - LV Temp")
    fig.update_yaxes(title_text="Temp (C)", row=1, col=1)
    fig.update_yaxes(title_text="Volume (mL)", row=2, col=1)
    fig.add_trace(
      go.Scatter(x=rsvrtemp_df['timestamp']/1000, y=rsvrtemp_df['inlet_temp'], name='rsvr inlet temp'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrtemp_df['timestamp']/1000, y=rsvrtemp_df['outlet_temp'], name='rsvr outlet temp'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=circag_df['timestamp']/1000, y=circag_df['wall_temp'], name='circag wall temp'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=circag_df['timestamp']/1000, y=circag_df['resin_temp'], name='circag resin temp'),
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
      go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['volume'], name='rsvr volume'),
      row=2, col=1,
    )
    fig.add_trace(
      go.Scatter(x=circag_df['timestamp']/1000, y=circag_df['volume'], name='circag volume'),
      row=2, col=1,
    )
    fig.add_trace(
      go.Scatter(x=ckm_df['timestamp']/1000, y=ckm_df['volume'], name='total volume'),
      row=2, col=1,
    )

  elif args.mode == "lvpump":
    if len(rsvrlevel_csv) == 0:
      print ("Could not locate rsvrlevel(2100) data files in " + args.csv_dir)
      exit()
    if len(rsvrtemp_csv) == 0:
      print ("Could not locate rsvrtemp(2101) data files in " + args.csv_dir)
      exit()
    fig = make_subplots(x_title="Timestamp(s)", rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02,
                        row_heights=[0.5, 0.5],
                        specs=[[{"secondary_y": False}], [{"secondary_y": False}]])
    fig.update_layout(title="CKM Warm Up - LV Pumps")
    fig.update_yaxes(title_text="Pump Speed (rpm)", row=1, col=1)
    fig.update_yaxes(title_text="Volume (mL)", row=2, col=1)
    fig.add_trace(
      go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['inlet_pump_speed'], name='inlet pump speed'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrtemp_df['timestamp']/1000, y=rsvrtemp_df['outlet_pump_speed'], name='outlet pump speed'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['volume'], name='rsvr volume'),
      row=2, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['target_volume'], name='rsvr tgt volume'),
      row=2, col=1,
    )
  else:
    print ("Unrecognized plot mode: " + args.mode)
    exit()

  # annotate with ckm states
  # find start/stop of each state
  if args.state:
    active_df = ckm_df.loc[ckm_df['state'] == 8]
    active_min = active_df["timestamp"].min()/1000
    active_max = active_df["timestamp"].max()/1000
    if not pd.isna(active_min) and not pd.isna(active_max):
      fig.add_vrect(x0=active_min, x1=active_max,
                    annotation_text="active", annotation_position="top left",
                    fillcolor="green", opacity=0.25, line_width=0)

    circwait_df = ckm_df.loc[ckm_df['state'] == 7]
    circwait_min = circwait_df["timestamp"].min()/1000
    circwait_max = circwait_df["timestamp"].max()/1000
    if (circwait_max-circwait_min)>5:
      fig.add_vrect(x0=circwait_min, x1=circwait_max,
                    annotation_text="circ_wait", annotation_position="top left",
                    fillcolor="yellow", opacity=0.25, line_width=0)

    prime_df = ckm_df.loc[ckm_df['state'] == 6]
    prime_min = prime_df["timestamp"].min()/1000
    prime_max = prime_df["timestamp"].max()/1000
    if (prime_max-prime_min)>5:
      fig.add_vrect(x0=prime_min, x1=prime_max,
                    annotation_text="prime", annotation_position="top left",
                    fillcolor="orange", opacity=0.25, line_width=0)

    preheat_df = ckm_df.loc[ckm_df['state'] == 5]
    preheat_min = preheat_df["timestamp"].min()/1000
    preheat_max = preheat_df["timestamp"].max()/1000
    if (preheat_max-preheat_min)>5:
      fig.add_vrect(x0=preheat_min, x1=preheat_max,
                    annotation_text="preheat", annotation_position="top left",
                    fillcolor="red", opacity=0.25, line_width=0)

  if args.align:
    for timestamp in data_break_timestamps:
      fig.add_vrect(x0=timestamp[0]/1000, x1=timestamp[1]/1000,
                    annotation_text="FH Reset", annotation_position="top left",
                    fillcolor="red", opacity=0.25, line_width=0)

  # Save the html plot
  if args.save == True:
    fig.write_html(os.path.join(args.csv_dir, "ckm_warm_up_" + args.mode + ".html"))
  fig.show()
