from monk2 import CodeBuilder, MicroTemplate
import re

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
    t = MicroTemplate(text, {'name': 'test'})
    f.close()