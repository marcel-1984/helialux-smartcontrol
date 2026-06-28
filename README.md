# HeliaLux SmartControl for Home Assistant

Custom Home Assistant integration for the **Juwel HeliaLux SmartControl** aquarium light controller.

This integration communicates locally with the HeliaLux SmartControl over HTTP.  
No cloud service is required.

## Features

- Local connection to HeliaLux SmartControl
- Device setup through the Home Assistant UI
- Live color channel sensors:
  - White
  - Blue
  - Green
  - Red
- Light entity
- Manual channel sliders
- Cloud Simulation switch
- Time Simulation switch
- Controller time sensors
- HACS-ready structure

## Current status

This project is under active development.

Working in the current test version:

- Config flow
- Local API connection
- Sensors
- Light entity
- Number sliders
- Cloud Simulation switch
- Time Simulation switch

Planned features:

- Better brightness support
- Profile support
- Program editor
- Sunrise and sunset editor
- Lovelace dashboard card

See [ROADMAP.md](ROADMAP.md) for the full roadmap.

## Installation with HACS

This repository can be added to HACS as a custom repository.

1. Open Home Assistant.
2. Go to **HACS**.
3. Open the menu in the top right.
4. Choose **Custom repositories**.
5. Add this repository URL:

```text
https://github.com/marcel-1984/helialux-smartcontrol