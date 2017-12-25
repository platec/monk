import re

class CodeBuilder:
    INDENT_STEP = 4
    def __init__(self, indent=0):
        self.indent_level = indent
        self.code = []

    def add_line(self, line):
        self.code.append(self.indent_level * ' ' + line + '\n')
    
    def indent(self):
        self.indent_level += self.INDENT_STEP

    def dedent(self):
        self.indent_level -= self.INDENT_STEP

    def __str__(self):
        return ''.join(str(c) for c in self.code)

    def get_globals(self):
        source = str(self)
        globals = {}
        eval(source, globals)
        return globals

class MicroTemplate:
    def __init__(self, text, *contexts):
        self.context = {}
        self.text = text
        for context in contexts:
            self.context.update(context)
        
        code = CodeBuilder()
        code.add_line("def render_function(context, do_dots):")
        code.indent()
        code.add_line("result = []")
        code.add_line("append_result = result.append")
        code.add_line("extend_result = result.extend")
        code.add_line("to_str = str")
        
        for key in self.context.keys():
            code.add_line("c_%s = context['%s']" % (key, key))

        print(code)
        print(self._tokenize(text))
        
    def _tokenize(self, text):
        return re.split(r'({{.*?}}|{%.*?%}|{#.*?#})', text)
