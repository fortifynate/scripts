import os
import argparse
import datetime
import re
from DataIds import *

class DataLogPacket(object):
  def __init__(self, attr_dict):
    for key in attr_dict:
      setattr(self, key, attr_dict[key])
  def get_header_string(self):
    return ",".join([self.data_id, self.data_name, self.frame_num, self.timestamp])

class DataLog(object):
  """docstring for DataLog"""
  header_pattern_string = r"{(?P<data_id>\d+),(?P<data_name>\w+),(?P<rev>\d+),(?P<data_len>\d+),(?P<frame_num>\d+),(?P<timestamp>\d+),(?P<serial_num>\d*),(?P<job_id>\d+),0}"
  packet_pattern_string = r"(?P<packet>[^|]*)\|(?P<crc>.{4})"
  packet_regex = re.compile(header_pattern_string + packet_pattern_string)
  headers=PACKET_HEADERS

  def __init__(self, data_id, data_headers):
    self.packets = []
    self.data_id = data_id
    self.data_headers = data_headers

  def add_data_packet(self, data_packet):
    packet_match = DataLog.packet_regex.match(data_packet)
    self.packets.append(DataLogPacket(packet_match.groupdict()))

  def get_header_string(self):
    return ",".join(self.headers + self.data_headers)

  def write_to_csv(self, filepath, headers):
    filename = "%s/Data_%d.csv" % (filepath, self.data_id)
    print("Writing Data ID %d to %s" % (self.data_id, filename))
    with open(filename, 'w') as f:
      if headers:
        f.write(self.get_header_string() + '\n')
      for p in self.packets:
        f.write (p.get_header_string() + "," + p.packet + '\n')

DATA_LOG_MAP = {}
for data_id_name in DATA_ID_MAP.keys():
  data_id = DATA_ID_MAP[data_id_name]
  DATA_LOG_MAP[data_id] = DataLog(data_id, DATA_HEADER_MAP[data_id])

class DataLogSet(object):
  """docstring for DataLogSet"""
  data_id_pattern_string = r"{(?P<data_id>\d+),"
  data_id_regex = re.compile(data_id_pattern_string)

  def __init__(self):
    self.data_logs = {}

  def add_data_packet(self, data_packet):
    # identify data ID
    data_id_match = DataLogSet.data_id_regex.match(data_packet)
    if data_id_match:
      data_id = int(data_id_match.group('data_id'))
      # skip packets for which we don't have data log info
      if data_id not in DATA_LOG_MAP.keys():
        return
      # create a data log object if not already added
      if data_id not in self.data_logs.keys():
        self.data_logs[data_id] = DATA_LOG_MAP[data_id]
      # add data packet to DataLog object
      self.data_logs[data_id].add_data_packet(data_packet)

  def write_to_csv(self, output_dir, headers):
    for data_id in self.data_logs.keys():
      self.data_logs[data_id].write_to_csv(output_dir, headers)

  def __str__(self):
    return "DataLogSet: %d data_logs %s" % (len(self.data_logs.keys()), list(self.data_logs.keys()))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("logfile", help="teraterm logfile")
  parser.add_argument("-o","--output_dir", default=datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), help="output csv directory")
  parser.add_argument("--headers", dest='headers', action='store_true', help="output csv headers")
  args = parser.parse_args()

  data_log_set = DataLogSet()

  # Using readlines()
  logfile = open(args.logfile, 'r')
  data_packet_str=''
  data_packet_num = 0
  i = 0
  for raw_line in logfile:
    processed_line = raw_line.strip()
    if len(processed_line):
      data_packet_str += processed_line
      if data_packet_str[-5]=='|':
        data_packet_num = data_packet_num+1
        data_log_set.add_data_packet(data_packet_str)
        # reset data_packet_str
        data_packet_str=''
    i += 1
  print ("Found %d data packets" % data_packet_num)
  print (data_log_set)

  # make output dir
  try:
    os.mkdir(args.output_dir)
  except FileExistsError:
    pass
  data_log_set.write_to_csv(args.output_dir, headers=args.headers)
