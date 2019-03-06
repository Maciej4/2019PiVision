# 2019PiVision
## Summary
Retro-reflective tape tracking program in python using pnp
## Tracking Target
Tracks retro-reflective tape, with length 14cm and width 5cm.
It is currently optimized for a green LED ring around the camera
to change this the HSV high and low values need to be changed.
The camera needs to be placed level with the vision tape, and will
calculate its X and Y relative to it in cm.
## Setup
### Make folder:
sudo mkdir /run/vision

### Add service config file:
sudo vim /etc/systemd/system/vision.service

```
[Unit]
Description=vision daemon
After=network.target

[Service]
PIDFile=/run/vision/pid
User=pi
Group=pi
RuntimeDirectory=vision
WorkingDirectory=/home/pi/shared/streaming
ExecStart=/usr/bin/python app.py
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
```

### To start it on boot:
sudo systemctl enable vision

### To start it now:
sudo systemctl start vision

### To stop it now
sudo systemctl stop vision

### To reload settings
sudo systemctl daemon-reload
sudo systemctl restart vision

### To view logs:
tailf /var/log/syslog
