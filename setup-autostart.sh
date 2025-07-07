#!/bin/bash

echo "Setting up solar monitor auto-start service..."

sudo cp solar-monitor.service /etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl enable solar-monitor.service

sudo systemctl start solar-monitor.service

sudo systemctl status solar-monitor.service

echo ""
echo "Auto-start setup complete!"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status solar-monitor    # Check service status"
echo "  sudo systemctl stop solar-monitor     # Stop the service"
echo "  sudo systemctl start solar-monitor    # Start the service"
echo "  sudo systemctl restart solar-monitor  # Restart the service"
echo "  sudo systemctl disable solar-monitor  # Disable auto-start"
echo "  sudo journalctl -u solar-monitor -f   # View live logs"
