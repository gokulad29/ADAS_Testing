#printing all the combination of signal values directly to log
import json
from itertools import product

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def generate_test_case(test_case_name, can_message_ID, signals):
    """
    Generate a test case with given parameters and write it to a file.
    """
    #for signal in signals:
    #    signal_name = signal.get("name", "")
    #   value_range = signal.get("value_range", [])

    if test_case_name and can_message_ID and signals:
        signal_names = [signal["name"] for signal in signals]
        signal_value_ranges = [range(signal["value_range"][0], signal["value_range"][1] + 1) for signal in signals]

        for values in product(*signal_value_ranges):
            iteration_str = f"{test_case_name}_{can_message_ID}: "
            iteration_str += ', '.join([f"{signal_names[i]}={values[i]}" for i in range(len(signal_names))])
            print(iteration_str)       
    
    
    '''===================================================================================================='''
    '''
    generated_code = f"import pytest\n\n# Predefined CAN message:\n# {can_message}\n\n{assertion_code}"

    file_name = f"generated_assertion_tests_{function_name.replace(' ', '_').lower()}.py"
    with open(file_name, 'w') as file:
        file.write(generated_code)

    print(f"Generated pytest assertion tests in '{file_name}' successfully.")
    '''

def main():
    json_file_path = "Signals_Data.json"
    json_data = read_json_file(json_file_path)

    for message_data in json_data.get("Messages", []):
        function_name = message_data.get("function_name", "")
        can_message_ID = message_data.get("can_message_ID", "")
        signals = message_data.get("signals", [])

        test_case_name = f"test_{function_name}_{can_message_ID}"
        generate_test_case(test_case_name, can_message_ID, signals)

if __name__ == "__main__":
    main()
