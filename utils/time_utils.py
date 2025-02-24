from datetime import datetime
import re

def calculate_time_difference(time_str):
    """计算时间差"""
    pattern = r"(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)"
    match = re.match(pattern, time_str)
    year, month, day, hour, minute, second = map(int, match.groups())

    target_time = datetime(year, month, day, hour, minute, second)
    current_time = datetime.now()
    time_difference = current_time - target_time

    hours = time_difference.total_seconds() // 3600
    minutes = (time_difference.total_seconds() % 3600) // 60
    return int(hours), int(minutes)