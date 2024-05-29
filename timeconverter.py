from datetime import datetime
import time

# Пример Unix-времени
unix_time = 1661600346  # Это время в формате Unix


readable_time_datetime = datetime.fromtimestamp(unix_time)
print("Readable time (datetime):", readable_time_datetime.strftime(
    '%Y-%m-%d %H:%M:%S'))


readable_time_time = time.strftime(
    '%Y-%m-%d %H:%M:%S', time.localtime(unix_time))
print("Readable time (time):", readable_time_time)
