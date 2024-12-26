import os
import garth
import config
import garmin_constants
from garth.exc import GarthException
from datetime import datetime, timedelta

def restore_or_login_session():
    session_dir = garmin_constants.SESSION_FILE

    if not os.path.isdir(session_dir):
        debug_print(f"Session directory does not exist. Creating: {session_dir}")
        os.makedirs(session_dir, exist_ok=True)

    oauth1_file = os.path.join(session_dir, "oauth1_token.json")
    oauth2_file = os.path.join(session_dir, "oauth2_token.json")
    if not os.path.isfile(oauth1_file) or not os.path.isfile(oauth2_file):
        debug_print(f"Session files not found in: {session_dir}. Logging in...")
        login_and_save_tokens(session_dir)
    else:
        try:
            debug_print(f"Attempting to restore session from: {session_dir}")
            garth.resume(session_dir)
            debug_print(f"Session successfully restored for: {garth.client.username}")
        except GarthException as e:
            debug_print(f"Failed to restore session. Error: {e}")
            debug_print("Logging in and creating new session files...")
            login_and_save_tokens(session_dir)

def login_and_save_tokens(session_dir):
    try:
        garth.login(config.garmin_email, config.garmin_password)
        garth.save(session_dir)
        debug_print(f"Session tokens saved successfully to: {session_dir}")
    except Exception as e:
        debug_print(f"Failed to login and save session tokens. Error: {e}")

def fetch_weight_data(start_date, end_date):
    try:
        url = f"{garmin_constants.GARMIN_CONNECT_WEIGHT_RANGE_URL}/{start_date}/{end_date}"
        params = {"includeAll": True}
        weight_data = garth.connectapi(url, params=params)
        return weight_data.get('dailyWeightSummaries', [])
    except Exception as e:
        raise RuntimeError(f"Error retrieving weight data: {e}")

def upload_fit_files(start_date, end_date):
    current_date = start_date

    while current_date <= end_date:
        file_name = get_file_name(current_date)
        file_found = False

        for root, _, files in os.walk(config.folder_path):
            if file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, "rb") as fit_file:
                        uploaded = garth.client.upload(fit_file)
                        status = "OK" if uploaded.get('detailedImportResult', {}).get('successes') else "Error"
                        debug_print(f"File uploaded: {file_name}, Result: {status}")
                        file_found = True
                except Exception as e:
                    debug_print(f"Error uploading {file_name}: {e}")
                break

        if not file_found:
            debug_print(f"File not found for date {current_date.strftime('%Y-%m-%d')}.")
        current_date += timedelta(days=1)

def upload_all_fit_files():
    for root, _, files in os.walk(config.folder_path):
        for file in files:
            if file.endswith(".fit"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "rb") as fit_file:
                        uploaded = garth.client.upload(fit_file)
                        status = "OK" if uploaded.get('detailedImportResult', {}).get('successes') else "Error"
                        debug_print(f"File uploaded: {file}, Result: {status}")
                except Exception as e:
                    debug_print(f"Error uploading {file}: {e}")

def get_file_name(date):
    date_str = date.strftime("%Y.%m.%d")
    file_name = config.file_name_template.format(
        prefix=config.file_name_config["prefix"],
        date=date_str,
        source=config.file_name_config["source"]
    )
    return file_name

def debug_print(message):
    if config.debug:
        print(message)

def main():
    try:
        restore_or_login_session()

        today = datetime.today()
        month_ago = today - timedelta(days=30)

        weight_data = fetch_weight_data(month_ago.isoformat(), today.isoformat())

        if not weight_data:
            debug_print("No weight data found. Uploading all available .fit files...")
            upload_all_fit_files()
            return

        last_weight = weight_data[0]
        last_weight_date_str = last_weight.get('summaryDate')
        last_weight_date = datetime.strptime(last_weight_date_str, "%Y-%m-%d")

        start_date = last_weight_date + timedelta(days=1)
        upload_fit_files(start_date, today)

    except Exception as e:
        debug_print(f"Error: {e}")

if __name__ == "__main__":
    main()