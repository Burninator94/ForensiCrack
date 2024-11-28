
# task 1
import sys
#Get the Python version
python_version = sys.version
#Display the Python version
print("Python Version:", python_version)


# Task 2
from datetime import datetime
#Get the current date and time
now = datetime.now()
#Format the date and time
current_time = now.strftime("%Y-%m-%d %H:%M:%S")
#Display the current date and time
print("Current Date and Time:", current_time)


# Task 3
#Prompt user to input comma-separated number
values = input('Input random comma-separated number')
#Split the input into a list sliced by commas
number_list = values.split(',')
#Convert the list into a tuple
number_tuple = tuple(number_list)
#Print the list  and tuple
print('list', number_list)
print('tuple', number_tuple)


# Task 4
import os

# Accept filename from myself
filename = input("Enter the filename: ")

# Extract the file extension
file_extension = os.path.splitext(filename)[1]

# Print the file extension
print(f"The extension of the file is: {file_extension}")


# Task 5
# Request a string value from program user
user_string = input("Enter a string: ")

# Calculate string length
string_length = len(user_string)

# Print the length 
print(f"The length of the string is: {string_length}")


# Task 6
def string_both_ends(input_string):
    # Is the string length less than 2
    if len(input_string) < 2:
        return ''
    # Return the first and last 2 characters
    return input_string[:2] + input_string[-2:]

# Accept a string from the user
user_string = input("Enter a string: ")

# Get the result
result = string_both_ends(user_string)

# Print the result
print(f"Result: {result}")


# Task 7
def multiply_list(numbers):
    # Initialize the product to 1
    product = 1
    # Iterate throughout the list and multiply each number
    for number in numbers:
        product *= number
    return product

# Program Test
numbers = [2, 100]
result = multiply_list(numbers)
print(f"The product of the numbers in the list is: {result}")


# Task 8
def count_upper_lower(input_string):
    # Initialize counters for uppercase and lowercase letters
    upper_count = 0
    lower_count = 0
    
    # Iterate through each character in the string
    for char in input_string:
        if char.isupper():
            upper_count += 1
        elif char.islower():
            lower_count += 1
    
    return upper_count, lower_count

# Accept a string from the user
user_string = input("Enter a string: ")

# Get the counts of uppercase and lowercase letters
upper, lower = count_upper_lower(user_string)

# Print the results
print(f"Number of uppercase letters: {upper}")
print(f"Number of lowercase letters: {lower}")


# Task 9
import re

def match_string(text):
    # Define the final project pattern
    pattern = r'^a(b*)$'
    
    # Search for the pattern in the text
    if re.search(pattern, text):
        return 'Pattern Match'
    else:
        return 'No Pattern Match'

# Program Test
test_strings = ["a", "ab", "abb", "ac", "abc"]
for string in test_strings:
    print(f"Testing '{string}': {match_string(string)}")


# Task 10
def check_key_exists(dictionary, key):
    if key in dictionary:
        print(f"Key '{key}' is present in the dictionary with value: {dictionary[key]}")
    else:
        print(f"Key '{key}' is not present in the dictionary.")

# Program Test
final_dict = {'a': 1, 'b': 2, 'c': 3}
key_to_check = input("Enter the key to check: ")
check_key_exists(final_dict, key_to_check)


# Task 11
# Create dictionary
final_dict_two = {'a': 1, 'b': 2, 'c': 3}

# Iterate over the dictionary using items() method
for key, value in final_dict.items():
    print(f"Key: {key}, Value: {value}")

# Task 12
n = 3
def read_first_n_lines(filename, n):
    try:
        with open(filename, 'r') as file:
            for i in range(n):
                line = file.readline()
                if not line:
                    break
                print(line.strip())
    except FileNotFoundError:
        print(f"The file {filename} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Task 13
import os

def count_lines_in_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        return len(lines)

# Program Test
file_path = r'C:\Users\taylo\Desktop\College\CYB216\Week 4\Final.txt'
print(f'Total number of lines: {count_lines_in_file(file_path)}')

# Task 14
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9

# Program Test
celsius = 25
fahrenheit = 77

print(f'{celsius}°C is equal to {celsius_to_fahrenheit(celsius):.2f}°F')
print(f'{fahrenheit}°F is equal to {fahrenheit_to_celsius(fahrenheit):.2f}°C')

# Task 15
def list_to_string(items):
    if not items:
        return ''
    elif len(items) == 1:
        return items[0]
    else:
        return ', '.join(items[:-1]) + ', and ' + items[-1]

# Program Test
mylist = ['Brisket', 'Pork Butt', 'Short Rib', 'Tri-Tip']
print(list_to_string(mylist))


