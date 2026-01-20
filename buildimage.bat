@echo off 
docker build -t fraction-collector-actuator:1.0.3 . 
docker save -o ".\\images\\fraction-collector-actuator-1.0.3.tar" fraction-collector-actuator:1.0.3