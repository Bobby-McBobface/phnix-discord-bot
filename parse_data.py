import ast

with open('data/levels.txt', 'r') as level_file:
  level_dict = ast.literal_eval(level_file.read())
