import os
import argparse
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from DataIds import *

def float_converter(value_string):
  try:
    return np.float64(value_string)
  except:
    return None

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("csv_dir", help="data csv directory")
  parser.add_argument("-s", "--save", help="save output",
                      action="store_true")
  args = parser.parse_args()

  # attempt to locate data files
  zload_csv = []
  for filename in os.listdir(args.csv_dir):
    if "Data_1004" in filename and ".csv" in filename:
      zload_csv.append(os.path.join(args.csv_dir, filename))

  data_dict = load_data_dict()

  headers = get_headers_by_id(data_dict, 1004)
  # create data frames and append any extra found files
  zload_df = pd.read_csv(zload_csv[0],
                         names=headers,
                         sep="[,;]",
                         converters={'z_arm_load': float_converter, 'z_arm_load_unfiltered': float_converter},
                         engine='python')
  for csv_file in zload_csv[1:]:
    next_df = pd.read_csv(csv_file,
                          names=headers,
                          sep="[,;]",
                          converters={'z_arm_load': float_converter, 'z_arm_load_unfiltered': float_converter},
                          engine='python')
    zload_df = zload_df.append(next_df)
  zload_df.dropna(inplace=True)

  fig = make_subplots(x_title="Timestamp(s)",
                      specs=[[{"secondary_y": True}]])
  fig.update_layout(title="Load Cell Data")
  fig.update_yaxes(title_text="Load (N)")
  fig.update_yaxes(title_text="Position (um)", secondary_y=True)

  fig.add_trace(
    go.Scatter(x=zload_df['timestamp']/1000, y=zload_df['z_load_n'], name='z_arm_load', mode='markers'),
    row=1, col=1,
  )
  fig.add_trace(
    go.Scatter(x=zload_df['timestamp']/1000, y=zload_df['z_load_raw_n'], name='z_arm_load_unfiltered', mode='markers'),
    row=1, col=1,
  )
  fig.add_trace(
    go.Scatter(x=zload_df['timestamp']/1000, y=zload_df['z_micron_n'], name='z_position'),
    row=1, col=1, secondary_y=True,
  )
  fig.add_trace(
    go.Scatter(x=zload_df['timestamp']/1000, y=zload_df['z_bp_micron'], name='z_bp_position'),
    row=1, col=1, secondary_y=True,
  )
  # Save the html plot
  if args.save == True:
    fig.write_html(os.path.join(args.csv_dir, "load_cell_plot.html"))
  fig.show()
