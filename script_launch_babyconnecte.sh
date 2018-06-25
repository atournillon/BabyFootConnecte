#!/usr/bin/env bash

su pi -c 'sh /home/pi/Documents/BabyFootConnecte/cron_statistique.sh' &
su pi -c 'sh /home/pi/Documents/BabyFootConnecte/cron_match.sh' &
su pi -c 'sh /home/pi/Documents/BabyFootConnecte/cron_app.sh' &

sleep 20
su pi -c 'DISPLAY=:0 chromium-browser http://127.0.0.1:5000/ --start-fullscreen' &
