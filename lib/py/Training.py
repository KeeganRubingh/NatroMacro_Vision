from ultralytics import YOLO, checks, hub
import Secrets
checks()

hub.login(Secrets.hubLogin)

model = YOLO('https://hub.ultralytics.com/models/sguT8bYek103fOBXaWcq')
results = model.train()