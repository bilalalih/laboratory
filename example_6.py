numbers = [1, 3, 4, 5, 8, 0, 9]
# Return the smallest or largest item within the given iterable.
maximum = max(numbers)
minimum = min(numbers)

print(f"max: {maximum}, min: {minimum}")

# Example with strings
words = ["apple", "banana", "pear", "zuava", "cherry", "date"]
smallest_word = min(words)
largest_word = max(words)

print(f"Largest word: {largest_word}, Smallest_word: {smallest_word}")

# Optional arguments
# key: A function that is called on each element to determine the comparison criteria
largest_word = max(words, key=len)
print(f"Largest by length: {largest_word}")

# Example: find the dictionary with the lowest "id" values
entries = [{"id": 9}, {"id": 7}, {"id": 1}]
lowest_id_entry = min(entries, key=lambda x: x["id"])
print(f"lowest id: {lowest_id_entry}")

# default: a value to return if the iterable is empty
empty_list = []
minimum = min(empty_list, default="N/A")
print(minimum)