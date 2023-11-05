from datetime import  datetime
import helpers as h

print(datetime.now().strftime('%H:%M:%S'))
print(f'Adjacent networks are {h.get_adjacent_networks()}')