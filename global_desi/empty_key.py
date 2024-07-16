import json

def load_json(filename):
    """Loads JSON data from a file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {filename}.")
        return []

def save_json(data, filename):
    """Saves JSON data to a file."""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def remove_empty_key_elements(data, key):
    """Removes elements from the data where the specified key is empty."""
    return [element for element in data if key in element and element[key]]

def clean_json_file(filename, key):
    """Loads JSON data, removes elements with empty key values, and saves the cleaned data back to the file."""
    data = load_json(filename)
    cleaned_data = remove_empty_key_elements(data, key)
    save_json(cleaned_data, filename)
    print(f"Cleaned data saved to {filename}")

# File to clean
filename = 'global_desi_girls_products.json'
# Key to check for empty values
key_to_check = 'image'

clean_json_file(filename, key_to_check)