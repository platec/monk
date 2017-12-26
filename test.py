import re
from monk import Monk

def test():
    with open('demo01.html', 'rt') as f:
        text = f.read()
        context = {
            'greet': 'hello this is a test', 
            'title': 'shit',
            'show': True,
            'titles': [1,2,3],
            'upper': lambda s: s.upper
        }        
        t = Monk(text, context)


if __name__ == '__main__':
    test()
