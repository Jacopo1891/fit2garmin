# Fit2Garmin

**Fit2Garmin** is a Python script designed to automatically upload `.fit` files to the [*Garmin Connect*](https://connect.garmin.com/) platform. The script streamlines the process by fetching `.fit` files from a specified folder, checking for new files, and uploading them to *Garmin Connect*. It utilizes the `garth` library for handling the authentication and upload process. Additionally, the script ensures robust session management, either restoring an existing session or logging in and saving the session if necessary. 

The goal is to make the upload process seamless and efficient, ensuring that fitness data is synchronized with *Garmin Connect* with minimal user intervention.

# Table of contents
- [The problem](#the-problem)
- [The solution](#the-solution)
- [Getting Started](#getting-started)
- [Suggestions](#suggestions)
- [Buy me a coffee](#buy-me-a-coffee)

  
## The problem

I own a [*Huawei Scale 3*](https://consumer.huawei.com/it/accessories/wifi-body-fat-scale/buy/) smart scale, which records weight and other metrics in the *Huawei Health* app. Unfortunately, this scale is not natively supported by *Garmin Connect*, and there are no third-party applications capable of syncing data directly between *Huawei Health* and *Garmin Connect*. After exploring various options, I found no solutions to bridge this gap.

The only viable approach was to work with `.fit` files. These files can be exported from *Huawei Health* using external tools and then uploaded to *Garmin Connect*. This script automates that process.

## The solution

Here’s how the process works:

1. **Exporting Data**: I use [*Health Sync*](https://play.google.com/store/apps/details?id=nl.appyhapps.healthsync) to extract weight and health data from *Huawei Health*. *Health Sync* uploads the data as `.fit` files to a designated folder on *Google Drive*.
   
2. **Syncing Locally**: The `.fit` files on *Google Drive* are synchronized to a local folder using [*rclone*](https://rclone.org/). A cron job ensures this synchronization happens regularly.

3. **Uploading to Garmin Connect**: The Fit2Garmin script monitors the local folder, identifies new `.fit` files, and uploads them to *Garmin Connect*. This ensures that my weight and health metrics are always up-to-date on *Garmin Connect*.

## Getting Started

Follow these steps to set up and run the script:

### 1. Install Dependencies

Before running the script, ensure you have Python installed on your system. Then, install the required libraries with the following command:

```bash
pip install garth
```
### 2. Configure `config.py`

The project includes an example configuration file named `config.example.py`. To set up your configuration:

2. Make a copy of the example file:

```bash
cp config.example.py config.py
```
- debug: Set to True to enable debug messages or False to suppress them.
- garmin_email and garmin_password: Replace with your Garmin Connect account credentials.
- folder_path: Specify the local directory where .fit files are stored.
- session_file_path: The path where the script will save the Garmin session file.
- file_name_template and file_name_config: Adjust these fields if your .fit files have a different naming structure.

  
# Suggestions
Please feel free to raise an issue on GitHub for any features you would like to see or usage issues you experience and I will endeavour to address them.

# Buy me a coffee
Find it useful? Please consider buying me or other contributors a coffee.

<a href="https://www.buymeacoffee.com/jacopo1891d">
<img style="height: 51px; width: 181px; max-width: 100%;" alt="blue-button" src="https://github.com/Jacopo1891/MMM-GoogleTrafficTimes/assets/5861330/43f41b8d-13e5-4711-877d-cab090bc56b0">
</a>
