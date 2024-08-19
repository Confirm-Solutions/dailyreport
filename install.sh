#!/bin/bash

# Set the variables
USER=$(whoami)
PLIST_NAME="com.dailyreport.plist"
PLIST_SOURCE="./$PLIST_NAME"
PLIST_DEST="/Users/$USER/Library/LaunchAgents/com.$USER.dailyreport.plist"

# Replace placeholder in .plist file with actual username
sed -e "s|__USER__|$USER|g" -e "s|__APP_PATH__|$(pwd)|g" "$PLIST_SOURCE" > "$PLIST_DEST"

# Unload the existing Launch Agent if it exists
if launchctl list | grep -q "com.$USER.dailyreport"; then
    echo "Unloading existing launch agent..."
    launchctl unload "$PLIST_DEST"
fi

# Load the new Launch Agent
echo "Loading the new launch agent..."
launchctl load "$PLIST_DEST"

# Provide feedback to the user
echo "Installation complete. The script is scheduled to run daily at 6:00 PM."