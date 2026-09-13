import subprocess, sys
subprocess.check_call([sys.executable, "create_dataset.py"])
subprocess.check_call([sys.executable, "train_model.py"])
