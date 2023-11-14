def extract_unique_ids(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            ids = set(line.strip() for line in f)

        with open(output_file, 'w') as f:
            for unique_id in ids:
                f.write(unique_id + '\n')

        print(f"Unique IDs have been written to {output_file}")
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


input_filename = 'qrels_files/visiting.txt'  # Change this to your input file name
output_filename = 'qrels_files/visiting_output.txt'  # Change this to your desired output file name

extract_unique_ids(input_filename, output_filename)
