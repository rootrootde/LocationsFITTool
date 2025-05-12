import argparse

from fit_tool.data_message import DataMessage
from fit_tool.fit_file import FitFile
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.location_message import LocationMessage
from fit_tool.profile.messages.location_settings_message import LocationSettingsMessage


def main():
    parser = argparse.ArgumentParser(
        description="Read a Locations.fit file and print waypoint data."
    )
    parser.add_argument("file_path", help="Path to the Locations.fit file")
    args = parser.parse_args()

    try:
        fit_file = FitFile.from_file(args.file_path)
    except Exception as e:
        print(f"Error opening or parsing FIT file: {e}")
        return

    print(f"Successfully opened FIT file: {args.file_path}")

    file_id_found = False
    waypoints_found = 0

    for record_wrapper in fit_file.records:
        actual_message = record_wrapper.message

        if not isinstance(actual_message, DataMessage):
            continue

        definition_for_data = actual_message.definition_message

        if definition_for_data.global_id == FileIdMessage.ID:
            file_id_msg = actual_message  # Use actual_message directly
            print("\n--- File ID ---")
            print(f"  Type: {file_id_msg.type}")
            print(f"  Manufacturer: {file_id_msg.manufacturer}")
            print(
                f"  Product: {file_id_msg.product}"
            )  # Or .garmin_product if appropriate
            print(f"  Time Created: {file_id_msg.time_created}")
            file_id_found = True

        elif definition_for_data.global_id == LocationSettingsMessage.ID:
            waypoint_settings_msg = actual_message
            print("\n--- Waypoint Settings ---")
            print(f"  Waypoint Setting: {waypoint_settings_msg.waypoint_setting}")

        elif definition_for_data.global_id == LocationMessage.ID:
            waypoint_msg = actual_message  # Use actual_message directly
            waypoints_found += 1
            print(f"\n--- Waypoint {waypoints_found} ---")
            print(f"  Name: {waypoint_msg.name}")
            print(f"  Latitude: {waypoint_msg.position_lat}")
            print(f"  Longitude: {waypoint_msg.position_long}")
            print(f"  Altitude: {waypoint_msg.altitude}")
            print(f"  Timestamp: {waypoint_msg.timestamp}")
            print(f"  Symbol: {waypoint_msg.symbol}")
            print(f"  Details: {waypoint_msg.description}")
            print(f"  Message Index: {waypoint_msg.message_index}")

    if not file_id_found:
        print("\nNo File ID message found.")
    if waypoints_found == 0:
        print("\nNo waypoint messages found in the file.")
    else:
        print(f"\nFound {waypoints_found} waypoint(s).")


if __name__ == "__main__":
    main()
