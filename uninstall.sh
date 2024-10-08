#!/bin/bash

# Set the variables
USER=$(whoami)
PLIST_DEST="/Users/$USER/Library/LaunchAgents/com.$USER.dailyreport.plist"

# Unload the Launch Agent
if launchctl list | grep -q "com.$USER.dailyreport"; then
    echo "Unloading the launch agent..."
    launchctl unload "$PLIST_DEST"
else
    echo "Launch agent not found. It may have already been unloaded."
fi

# Remove the .plist file
if [ -f "$PLIST_DEST" ]; then
    echo "Removing the .plist file..."
    rm "$PLIST_DEST"
else
    echo ".plist file not found. It may have already been removed."
fi

# Provide feedback to the user
echo "Uninstallation complete. The daily report script has been removed from your system."
echo "Note: This script does not remove the actual report script or any generated reports."
echo "You may want to manually remove those files if you no longer need them."