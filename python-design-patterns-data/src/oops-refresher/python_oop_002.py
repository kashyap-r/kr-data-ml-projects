# This program demonstrates the use of classes and objects in Python to model a simple relationship between authors and books.
# It demostrates the concept of encapsulation, inheritance, and composition in object-oriented programming.
# Define the Author class
class Author:
    def __init__(self, name, birth_year):
        self.name = name
        self.birth_year = birth_year
    # returns a string with the author's name and birth year
    def get_author_info(self):
        return f"{self.name} (born {self.birth_year})"

# Define the Book class, that also contains another class object as a property (composition)
class Book:
    def __init__(self, title, publication_year, author: Author):
        self.title = title
        self.publication_year = publication_year
        self.author = author

    def get_book_info(self):
        return f"'{self.title}' by {self.author.get_author_info()}, published in {self.publication_year}"

# Create an Author object
author_obj = Author("George Orwell", 1903)

# Create a Book object with the Author object as a property
book_obj = Book("1984", 1949, author_obj)

# Print the book information, which includes author information
print(book_obj.get_book_info()) 