import os
from datetime import datetime
timestring = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
dirname = f"Catan/runs/{timestring}"
dirname_models = dirname + '/models'

os.makedirs(os.path.dirname(dirname + '/'), exist_ok=True)
os.makedirs(os.path.dirname(dirname_models + '/'), exist_ok=True)
