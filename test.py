import re
from monk import Monk

def generate_tokens():
    pattern = re.compile(r'{{(?P<expression>.*?)}}|{%(?P<logic>.*?)%}|{#(?P<comment>.*?)#}')
    f = open('index.html', 'rt')
    page = f.read()
    scanner = pattern.scanner(page)
    for token in iter(scanner.search, None):
        yield token.lastgroup, token.group(token.lastgroup).strip()
    f.close()

def test():
    for t in generate_tokens():
        if t[0] != 'comment':
            print(t)


if __name__ == '__main__':
    f = open('index.html', 'rt')
    text = f.read()
    import templite
    context = {
        'greet': 'hello this is a test', 
        'title': 'shit',
        'show': True,
        'titles': [1,2,3],
        'upper': lambda s: s.upper
    }
    t = templite.Templite(text)
    # t = Monk(text)
    result = t.render(context)
    print(result)
    f.close()

