import os
from datetime import datetime, timedelta
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)
import config
import garmin_constants


def _resolve_session_paths(session_path):
    if session_path.lower().endswith(".json"):
        session_dir = os.path.dirname(session_path) or "."
        return session_dir, session_path
    return session_path, os.path.join(session_path, garmin_constants.TOKEN_FILE_NAME)


def restore_or_login_session():
    session_path = garmin_constants.SESSION_FILE
    session_dir, token_file = _resolve_session_paths(session_path)

    if not os.path.isdir(session_dir):
        debug_print(f"Session directory does not exist. Creating: {session_dir}")
        os.makedirs(session_dir, exist_ok=True)

    if not os.path.isfile(token_file):
        debug_print(f"Session file not found in: {session_dir}. Logging in...")
        return login_and_save_tokens(session_path)

    try:
        debug_print(f"Attempting to restore session from: {session_path}")
        client = Garmin()
        client.login(session_path)
        user_name = client.get_full_name() or client.display_name
        debug_print(f"Session successfully restored for: {user_name}")
        return client
    except GarminConnectTooManyRequestsError:
        raise
    except (GarminConnectAuthenticationError, GarminConnectConnectionError) as e:
        debug_print(f"Failed to restore session. Error: {e}")
        debug_print("Logging in and creating new session files...")
        return login_and_save_tokens(session_path)


def login_and_save_tokens(session_path):
    try:
        client = Garmin(
            email=config.garmin_email,
            password=config.garmin_password,
            prompt_mfa=lambda: input("MFA code: ").strip(),
        )
        client.login(session_path)
        debug_print(f"Session tokens saved successfully to: {session_path}")
        return client
    except Exception as e:
        debug_print(f"Failed to login and save session tokens. Error: {e}")
        raise


def _format_date(value):
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return str(value)[:10]


def fetch_weight_data(client, start_date, end_date):
    try:
        weight_data = client.get_weigh_ins(
            _format_date(start_date),
            _format_date(end_date),
        )
        if not isinstance(weight_data, dict):
            return []
        return weight_data.get("dailyWeightSummaries", [])
    except Exception as e:
        raise RuntimeError(f"Error retrieving weight data: {e}") from e


def _upload_single_fit_file(client, file_path, display_name):
    uploaded = client.upload_activity(file_path)
    successes = (
        uploaded.get("detailedImportResult", {}).get("successes")
        if isinstance(uploaded, dict)
        else None
    )
    status = "OK" if successes else "Error"
    debug_print(f"File uploaded: {display_name}, Result: {status}")


def upload_fit_files(client, start_date, end_date):
    current_date = start_date

    while current_date <= end_date:
        file_name = get_file_name(current_date)
        file_found = False

        for root, _, files in os.walk(config.folder_path):
            if file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    _upload_single_fit_file(client, file_path, file_name)
                    file_found = True
                except Exception as e:
                    debug_print(f"Error uploading {file_name}: {e}")
                break

        if not file_found:
            debug_print(f"File not found for date {current_date.strftime('%Y-%m-%d')}.")
        current_date += timedelta(days=1)


def upload_all_fit_files(client):
    for root, _, files in os.walk(config.folder_path):
        for file in sorted(files):
            if file.endswith(".fit"):
                file_path = os.path.join(root, file)
                try:
                    _upload_single_fit_file(client, file_path, file)
                except Exception as e:
                    debug_print(f"Error uploading {file}: {e}")


def get_file_name(date):
    date_str = date.strftime("%Y.%m.%d")
    file_name = config.file_name_template.format(
        prefix=config.file_name_config["prefix"],
        date=date_str,
        source=config.file_name_config["source"],
    )
    return file_name


def debug_print(message):
    if config.debug:
        print(message)


def main():
    try:
        client = restore_or_login_session()

        today = datetime.today()
        month_ago = today - timedelta(days=30)

        weight_data = fetch_weight_data(client, month_ago, today)

        if not weight_data:
            debug_print("No weight data found. Uploading all available .fit files...")
            upload_all_fit_files(client)
            return

        last_weight = weight_data[0]
        last_weight_date_str = last_weight.get("summaryDate")
        last_weight_date = datetime.strptime(last_weight_date_str, "%Y-%m-%d")

        start_date = last_weight_date + timedelta(days=1)
        upload_fit_files(client, start_date, today)

    except Exception as e:
        debug_print(f"Error: {e}")


if __name__ == "__main__":
    main()
