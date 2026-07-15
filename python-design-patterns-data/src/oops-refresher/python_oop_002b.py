import math 

class circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        # calculate and return the area of the circle using the formula A = πr^2
        return math.pi * self.radius ** 2

    def circumference(self):
        # calculate and return the circumference of the circle using the formula C = 2πr
        return 2 * math.pi * self.radius
        

    def diameter(self):
        # calculate and return the diameter of the circle using the formula D = 2r
        return 2 * self.radius
        
# Create an instance of the circle class with a radius of 5
my_circle = circle(5)   
# Print the area, circumference, and diameter of the circle
print(f"Area of the circle: {my_circle.area()}")
print(f"Circumference of the circle: {my_circle.circumference()}")
print(f"Diameter of the circle: {my_circle.diameter()}")

circle2 = circle(10)
print(f"Area of the circle: {circle2.area()}")
print(f"Circumference of the circle: {circle2.circumference()}")    
print(f"Diameter of the circle: {circle2.diameter()}")
