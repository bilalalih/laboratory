import json

# Convert from json to python dict
# Some JSON
x = '{ "name": "Bilal Alih", "age": 20, "date-of-birth": "2005-08-04"}'

# parse x
y = json.loads(x)

print(y["name"])

# Convert from python dict to JSON
# a Python object (dict):
x = {
  "name": "John",
  "age": 30,
  "city": "New York"
}

# convert into JSON:
y = json.dumps(x)

# the result is a JSON string:
print(y)

"""
You can convert python objects of the following type to JSON
dict
list
tuple
string
int
float
True
False
None
"""

x = {
  "name": "John",
  "age": 30,
  "married": True,
  "divorced": False,
  "children": ("Ann","Billy"),
  "pets": None,
  "cars": [
    {"model": "BMW 230", "mpg": 27.5},
    {"model": "Ford Edge", "mpg": 24.1}
  ]
}
# The indent parameter defines the number of indents
print(json.dumps(x, indent=2))