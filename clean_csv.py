file_name = "full_data.csv"

encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1']

for encoding in encodings_to_try:
    try:
        with open(file_name, 'r', encoding=encoding) as file:
            lines = file.readlines()
            filtered_lines = [line for line in lines if line.strip().split(',')[0] == "liga-portugal"]

        with open(file_name, 'w', encoding=encoding) as file:
            file.writelines(filtered_lines)

        print(f"Lines not containing 'liga-portugal' in the first column have been removed using encoding: {encoding}")
        break
    except UnicodeDecodeError:
        continue

print("Done.")
