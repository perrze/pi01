#!/usr/bin/env bash
python src/brain/main.py &
sleep 1
python src/user_interaction/main_ui.py &
sleep 1
python src/hardware/hardware_client.py &
sleep 1
python src/vision/main_vision.py &