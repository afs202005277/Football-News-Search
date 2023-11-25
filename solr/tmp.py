input_file_path = 'pri_synonyms.txt'  # Replace with the path to your text file

output_lines = []

with open(input_file_path, 'r') as file:
    for line in file:
        formatted_line = f'[{line.strip()}]'
        output_lines.append(formatted_line)

# Save the modified content to a new file
output_file_path = 'out.txt'  # Replace with the desired output file path

with open(output_file_path, 'w') as output_file:
    output_file.write('\n'.join(output_lines))

print(f"Formatted content saved to {output_file_path}")

