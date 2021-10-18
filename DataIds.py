
PACKET_HEADERS=["data_id","data_name","frame_num","timestamp"]

DATA_ID_MAP={
  "RSVR_STATUS0"  : 2100, #RSVR_LEVEL
  "RSVR_STATUS1"  : 2101, #RSVR_TEMP
  "CIRCAG_STATUS" : 2200,
  "CIRCAG_DATA0"  : 2250,
  "AMBHEAT_STATUS": 2400,
}

DATA_HEADER_MAP= {
  DATA_ID_MAP["RSVR_STATUS0"]      : ["status_bits",
                                      "level",
                                      "volume",
                                      "target_volume",
                                      "inlet_pump_mode",
                                      "inlet_pump_speed"],
  DATA_ID_MAP["RSVR_STATUS1"]      : ["inlet_temp",
                                      "outlet_temp",
                                      "outlet_pump_mode",
                                      "outlet_pump_speed"],
  DATA_ID_MAP["CIRCAG_STATUS"]     : ["status_bits",
                                      "heat_mode",
                                      "motor_mode",
                                      "meas_mode",
                                      "resin_temp",
                                      "wall_temp",
                                      "level",
                                      "volume",
                                      "agitator_speed"],
  DATA_ID_MAP["CIRCAG_DATA0"]      : ["update_time",
                                      "heat_mode",
                                      "tgt_body_temp",
                                      "body_temp",
                                      "tgt_resin_temp",
                                      "resin_temp",
                                      "inlet_temp",
                                      "duty_cycle"],
  DATA_ID_MAP["AMBHEAT_STATUS"]    : ["state",
                                      "temp",
                                      "inlet_temp"],
}
