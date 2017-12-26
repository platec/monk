import re


class CodeBuilder:
    INDENT_STEP = 4

    def __init__(self, indent=0):
        self.code = []
        self.indent_level = indent

    def add_line(self, line):
        self.code.extend([' ' * self.indent_level + line + '\n'])

    def indent(self):
        self.indent_level += self.INDENT_STEP

    def dedent(self):
        self.indent_level -= self.INDENT_STEP

    def add_section(self):
        section = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section

    def __str__(self):
        return ''.join([str(c) for c in self.code])

    def get_globals(self):
        assert self.indent_level == 0
        python_source = str(self)
        global_namespaces = {}
        exec(python_source, global_namespaces)
        return global_namespaces


class Monk:
    def __init__(self, text, *contexts):
        self.context = {}
        for context in contexts:
            self.context.update(context)

        self.all_vars = set()
        self.loop_vars = set()

        code = CodeBuilder()
        code.add_line('def render_function(context, do_dots):')
        code.indent()
        vars_code = code.add_section()
        code.add_line('result = []')
        code.add_line('append_result = result.append')
        code.add_line('extend_result = result.extend')
        code.add_line('to_str = str')

        tokens = self._generate_tokens(text)
        for token in tokens:
            name = token[0]
            expr = token[1]
            if name == 'html':
                code.add_line('append_result("""%s""")' % expr)
            elif name == 'expression':
                expr = expr.strip()
                code.add_line("c_%s = context['%s']" %(expr, expr))
                code.add_line("append_result(to_str(c_%s))" % expr)
            elif name == 'comment':
                continue
            elif name == 'logic':
                expr = expr.strip()
                if expr.startswith('if'):
                    words = expr.split()
                    jouken = words[1]
                    code.add_line("c_%s = context['%s']" %(jouken, jouken))
                    code.add_line('if c_%s:' % jouken)
                    code.indent()
                elif expr.startswith('end'):
                    code.dedent()
                else:
                    pass
                    
        code.add_line("return ''.join(result)")
        code.dedent()
        print(code.get_globals()['render_function'](self.context, None))
        # print(code)

    def _generate_tokens(self, text):
        pattern = re.compile(
            r'{{(?P<expression>.*?)}}|{%(?P<logic>.*?)%}|{#(?P<comment>.*?)#}')
        matches = pattern.finditer(text)
        start = 0
        end = 0
        for m in matches:
            end = m.span()[0]
            yield 'html', text[start: end]
            start = m.span()[1]
            yield m.lastgroup, m.group(m.lastgroup)
        yield 'html', text[start:]
