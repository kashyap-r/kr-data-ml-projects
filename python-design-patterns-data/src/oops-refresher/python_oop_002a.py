# Demostrating inheritance and method overriding in Python.

# Base Class 
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        # the attribute 'name' is inherited from the class animal and is accessed using 'self' to print the sound 
        # the animal makes
        print (f"{self.name} makes a sound.")

# Derived Class 
class Dog(Animal):
    def speak(self):
        print (f"{self.name} says Woof!")

# Derived class 
class Cat(Animal):
    def speak(self):
        print (f"{self.name} says Meow!")

# Create the objects of the derived classes and call the speak method to see the output.
dog = Dog("Buddy")
cat = Cat("Whiskers")

dog.speak()  # Output: Buddy says Woof!
cat.speak()  # Output: Whiskers says Meow!