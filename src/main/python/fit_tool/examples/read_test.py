from fit_tool.data_message import DataMessage
from fit_tool.fit_file import FitFile

fit_file = FitFile.from_file(
    "/Users/chris/Coding/python_fit_tool/fit_tool/examples/Locations.fit"
)


for record_wrapper in fit_file.records:
    actual_message = record_wrapper.message

    if not isinstance(actual_message, DataMessage):
        continue

    print(actual_message.global_id)
