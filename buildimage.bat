@echo off
docker build -t fraction-collector-actuator:1.0.0 .
docker save -o ".\\images\\fraction-collector-actuator-1.0.0.tar" fraction-collector-actuator:1.0.0
