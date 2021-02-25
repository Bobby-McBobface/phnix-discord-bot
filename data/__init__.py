import ast

def save_data(data, filename):
  with open(filename, 'w') as file:
    file.write(data)

with open('data/levels.txt', 'r') as level_file:
  level_dict = ast.literal_eval(level_file.read())
