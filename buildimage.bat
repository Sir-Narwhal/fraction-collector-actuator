@echo off 
docker build -t fraction-collector-actuator:1.0.2 . 
docker save -o ".\\images\\fraction-collector-actuator-1.0.2.tar" fraction-collector-actuator:1.0.2