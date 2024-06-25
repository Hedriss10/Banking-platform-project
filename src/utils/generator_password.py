import random
import string

def generator_password(size=8):
    cha = string.ascii_letters + string.digits  
    password = ''.join(random.choice(cha) for i in range(size))
    return password

