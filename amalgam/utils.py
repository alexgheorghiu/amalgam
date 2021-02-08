
import string
import random

def random_string(n=10):
    """Based on https://www.educative.io/edpresso/how-to-generate-a-random-string-in-python"""    
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10))
