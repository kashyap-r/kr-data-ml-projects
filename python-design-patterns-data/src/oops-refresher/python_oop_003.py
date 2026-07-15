"""
Demostrating Interfaces and Abstract classes (refer to the jupyter notebook for more details on the concept of interfaces and abstract classes in Python)

A "contract" is like a promise to provide some specific behaviour or functionality. In programming, 
we can use interfaces and abstract classes to define these contracts.


This program demonstrates the use of abstract classes and method overriding in Python. 
We define an abstract class 'Animal' with an abstract method 'sound' and a concrete method 'description'. 
The 'Dog' class overrides both the 'sound' and 'description' methods, while the 'Cat' class only overrides 
the 'sound' method, inheriting the default implementation of 'description' from the 'Animal' class. 

When we create instances of 'Dog' and 'Cat', we see how the overridden methods behave differently for each class.
"""

from abc import ABC, abstractmethod

# interface contract - any class that inherits from 'Animal' must implement the 'sound' method, and can optionally 
# override the 'description' method.

# Define an abstract class 'Animal'
class Animal(ABC):
    @abstractmethod
    def sound(self):
        pass

    # Make the 'description' method abstract but provide a basic implementation
    def description(self):
        print(f"{self.__class__.__name__} says: {self.sound()}")

# Define a concrete class 'Dog' that inherits from 'Animal'
class Dog(Animal):
    def sound(self):
        return "Woof!"
    
    def description(self):
        print(f"My little dog says: {self.sound()}")

# Define a concrete class 'Cat' that inherits from 'Animal'
class Cat(Animal):
    def sound(self):
        return "Meow!"

# Create instances of concrete classes and use the overridden 'description' method
dog = Dog()
dog.description()

cat = Cat()
cat.description()