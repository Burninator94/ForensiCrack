import os

def count_lines_in_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        return len(lines)

# Program Test
file_path = r'C:\Users\taylo\Desktop\College\CYB216\Week 4\Final.txt'
print(f'Total number of lines: {count_lines_in_file(file_path)}')