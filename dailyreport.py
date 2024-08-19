import os
print(os.getcwd())
import sys
print(sys.executable)

try:
    import discord
except ImportError:
    import subprocess
    import sys

    print("Discord module not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "discord"])
    import discord
import subprocess
import re
import argparse
import sys


# Function to run the AppleScript and get the timing data
def run_applescript():
    script = """
    tell application "TimingHelper"
        set currentDate to current date
        set startOfDay to currentDate - (time of currentDate)
        set endOfDay to startOfDay + (86399 as integer)
        
        try
            set summary to get time summary between startOfDay and endOfDay
            set projectTimes to times per project of summary
            return projectTimes
        on error errorMessage
            return "Error: " & errorMessage
        end try
    end tell
    """

    try:
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing AppleScript: {e.stderr}"


# Function to parse and sort the timing data
def parse_timing_data(data_string):
    # Remove curly braces and split by comma
    items = data_string.strip("{}").split(",")

    # Parse each item
    project_times = {}
    for item in items:
        # Split by colon, handling project names with spaces
        match = re.match(r"(\|.+\||[^:]+):(.+)", item.strip())
        if match:
            project, time = match.groups()
            project = project.strip("|").strip()
            project_times[project] = float(time)

    # Sort projects alphabetically
    sorted_projects = sorted(project_times.items())

    # Categorize time
    bad_projects = ["bad"]  # Replace with actual project names for "bad" time
    work_projects = [
        "deep work",
        "other work",
        "unsure",
    ]  # Replace with actual project names for "work" time

    bad_time = 0
    work_time = 0

    # Generate report string
    report = ""
    total_hours = 0
    for project, seconds in sorted_projects:
        hours = round(seconds / 3600, 2)
        report += f"    {project}: {hours} hours\n"
        total_hours += hours

        # Categorize time
        if project in bad_projects:
            bad_time += hours
        elif project in work_projects:
            work_time += hours

    # Add summary
    report += f"\nSummary:\n    Bad time: {round(bad_time, 2)} hours\n    Work time: {round(work_time, 2)} hours"
    report += f"\n    Total time: {round(total_hours, 2)} hours"
    return report


# Function to confirm sending the message
def confirm_sending():
    while True:
        response = (
            input("Do you want to send this report to Discord? (y/n): ").strip().lower()
        )
        if response in ["y", "n"]:
            return response == "y"
        print("Please respond with 'y' or 'n'.")


# Command-line argument parsing
parser = argparse.ArgumentParser(description="Send Timing report to Discord.")
parser.add_argument(
    "-y", "--yes", action="store_true", help="Send the report without confirmation."
)
args = parser.parse_args()

# Main logic
print("Retrieving data from Timing app...")
raw_data = run_applescript()

if raw_data.startswith("Error"):
    message_content = raw_data
else:
    username = os.environ["USER"]
    message_content = f"Today's Timing Report for {username}:\n" + parse_timing_data(raw_data)

# Print the report locally
print("\n" + message_content + "\n")

# Confirmation before sending
if not args.yes:
    if not confirm_sending():
        print("Report not sent.")
        sys.exit()

# Discord bot setup
intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

    # Send message to the Discord channel
    channel = client.get_channel(1234603860971094036)
    await channel.send(message_content)

    # Close the bot connection after sending the message
    await client.close()


# Run the bot using your token
token = "MTI3NDg3MjA4OTExMDc3Mzc5MA.G52mcZ.7zxndSW6A85epojueX1OnJUWIlrVrujEj9fu_I"
client.run(token)
