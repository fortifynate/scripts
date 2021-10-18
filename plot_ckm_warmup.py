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
  args = parser.parse_args()

  # attempt to locate data files
  rsvrlevel_csv = []
  rsvrtemp_csv = []
  circag_csv = []
  ambheat_csv = []
  for filename in os.listdir(args.csv_dir):
    if "Data_2100" in filename:
      rsvrlevel_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2101" in filename:
      rsvrtemp_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2200" in filename:
      circag_csv.append(os.path.join(args.csv_dir, filename))
    if "Data_2400" in filename:
      ambheat_csv.append(os.path.join(args.csv_dir, filename))


  # create data frames and append any extra found files
  rsvrlevel_df = pd.read_csv(rsvrlevel_csv[0], names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["RSVR_STATUS0"]])
  for csv_file in rsvrlevel_csv[1:]:
    rsvrlevel_df = rsvrlevel_df.append(pd.read_csv(csv_file, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["RSVR_STATUS0"]]))

  rsvrtemp_df = pd.read_csv(rsvrtemp_csv[0], names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["RSVR_STATUS1"]])
  for csv_file in rsvrtemp_csv[1:]:
    rsvrtemp_df = rsvrtemp_df.append(pd.read_csv(csv_file, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["RSVR_STATUS1"]]))

  circag_df = pd.read_csv(circag_csv[0], names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["CIRCAG_STATUS"]])
  for csv_file in circag_csv[1:]:
    circag_df = circag_df.append(pd.read_csv(csv_file, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["CIRCAG_STATUS"]]))

  if len(ambheat_csv) > 0:
    ambheat_df = pd.read_csv(ambheat_csv[0], names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["AMBHEAT_STATUS"]])
    for csv_file in ambheat_csv[1:]:
      ambheat_df = ambheat_df.append(pd.read_csv(csv_file, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["CIRCAG_STATUS"]]))



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

    fig = make_subplots(x_title="Timestamp(s)", rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02,
                        row_heights=[0.5, 0.25, 0.25],
                        specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]])
    fig.update_layout(title="CKM Warm Up - LV Temp")
    fig.update_yaxes(title_text="Temp (C)", row=1, col=1)
    fig.update_yaxes(title_text="Volume (mL)", row=2, col=1)
    fig.update_yaxes(title_text="Heat Mode", row=3, col=1,
                     tickvals=[1, 2, 3, 4],
                     ticktext=['preheat', 'body', 'resin', 'inlet'])
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
    fig.add_trace(
      go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['volume'], name='rsvr volume'),
      row=2, col=1,
    )
    fig.add_trace(
      go.Scatter(x=circag_df['timestamp']/1000, y=circag_df['volume'], name='circag volume'),
      row=2, col=1,
    )
    fig.add_trace(
      go.Scatter(x=circag_df['timestamp']/1000, y=circag_df['heat_mode'], name='heat mode'),
      row=3, col=1,
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

  # Save the html plot
  if args.save == True:
    fig.write_html(os.path.join(args.csv_dir, "ckm_warm_up_" + args.mode + ".html"))
  fig.show()
