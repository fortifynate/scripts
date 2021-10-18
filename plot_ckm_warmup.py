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
  args = parser.parse_args()

  # attempt to locate data files
  rsvrlevel_csv = None
  rsvrtemp_csv = None
  circag_csv = None
  ambheat_csv = None
  for filename in os.listdir(args.csv_dir):
    if "Data_2100" in filename:
      rsvrlevel_csv = os.path.join(args.csv_dir, filename)
    if "Data_2101" in filename:
      rsvrtemp_csv = os.path.join(args.csv_dir, filename)
    if "Data_2200" in filename:
      circag_csv = os.path.join(args.csv_dir, filename)
    if "Data_2400" in filename:
      ambheat_csv = os.path.join(args.csv_dir, filename)

  if rsvrlevel_csv is None or rsvrtemp_csv is None or circag_csv is None:
    print ("Could not locate data files in " + args.csv_dir)
    exit()

  rsvrlevel_df = pd.read_csv(rsvrlevel_csv, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["RSVR_STATUS0"]])
  rsvrtemp_df = pd.read_csv(rsvrtemp_csv, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["RSVR_STATUS1"]])
  circag_df = pd.read_csv(circag_csv, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["CIRCAG_STATUS"]])

  rows = 3
  if rows == 1:
    fig = make_subplots(x_title="Timestamp(s)", rows=rows, cols=1,)
  elif rows == 2:
    fig = make_subplots(x_title="Timestamp(s)", rows=rows, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02,
                        row_heights=[0.75, 0.25],
                        specs=[[{"secondary_y": False}], [{"secondary_y": False}]])
  elif rows == 3:
    fig = make_subplots(x_title="Timestamp(s)", rows=rows, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02,
                        row_heights=[0.5, 0.25, 0.25],
                        specs=[[{"secondary_y": False}], [{"secondary_y": False}], [{"secondary_y": False}]])
  fig.update_layout(title="CKM Warm Up")
  fig.update_yaxes(title_text="Temp (C)", row=1, col=1)
  fig.update_yaxes(title_text="Volume (mL)", row=2, col=1)
  # fig.update_yaxes(title_text="Heat Mode", row=3, col=1,
  #                  tickvals=[1, 2, 3, 4],
  #                  ticktext=['preheat', 'body', 'resin', 'inlet'])
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
  if rows >=2:
    # fig.add_trace(
    #   go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['inlet_pump_speed'], name='inlet pump speed'),
    #   row=2, col=1,
    # )
    # fig.add_trace(
    #   go.Scatter(x=rsvrtemp_df['timestamp']/1000, y=rsvrtemp_df['outlet_pump_speed'], name='outlet pump speed'),
    #   row=2, col=1,
    # )
    fig.add_trace(
      go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['volume'], name='rsvr volume'),
      row=2, col=1,
    )
    fig.add_trace(
      go.Scatter(x=circag_df['timestamp']/1000, y=circag_df['volume'], name='circag volume'),
      row=2, col=1,
    )
  if rows >=3:
    fig.add_trace(
      go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['volume'], name='rsvr volume'),
      row=3, col=1,
    )
    fig.add_trace(
      go.Scatter(x=rsvrlevel_df['timestamp']/1000, y=rsvrlevel_df['target_volume'], name='rsvr tgt volume'),
      row=3, col=1,
    )
    # fig.add_trace(
    #   go.Scatter(x=circag_df['timestamp']/1000, y=circag_df['heat_mode'], name='heat mode', showlegend=False),
    #   row=3, col=1,
    # )
  if ambheat_csv:
    ambheat_df = pd.read_csv(ambheat_csv, names=PACKET_HEADERS+DATA_HEADER_MAP[DATA_ID_MAP["AMBHEAT_STATUS"]])
    fig.add_trace(
      go.Scatter(x=ambheat_df['timestamp']/1000, y=ambheat_df['temp'], name='chamber temp'),
      row=1, col=1,
    )
    fig.add_trace(
      go.Scatter(x=ambheat_df['timestamp']/1000, y=ambheat_df['inlet_temp'], name='chamber inlet temp'),
      row=1, col=1,
    )
  # fig.add_trace(
  #   go.Scatter(x=ambheat_df['timestamp']/1000, y=ambheat_df['state'], name='chamber heat mode', showlegend=False),
  #   row=3, col=1,
  # )

  # Save the html plot
  if args.save == True:
    fig.write_html(os.path.join(args.csv_dir, "ckm_warm_up.html"))
  fig.show()
