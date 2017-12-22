import re
INDENT_STEP = 4


class CodeBuilder:
    def __init__(self, indent=0):
        self.code = []
        self.indent_level = indent

    def add_line(self, line):
        self.code.extend([' ' * self.indent_level + line + '\n'])

    def indent(self):
        self.indent_level += INDENT_STEP

    def dedent(self):
        self.indent_level -= INDENT_STEP

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
        section = code.add_section()
        section.add_line('result = []')
        section.add_line('append_result = result.append')
        section.add_line('extend_result = result.extend')
        section.add_line('to_str = str')

        buffered = []

        def flush_output():
            if len(buffered) == 1:
                code.add_line('append_result(%s)' % buffered[0])
            elif len(buffered) > 1:
                code.add_line('extend_result([%s])' % ''.join(buffered))
            del buffered[:]

        template_settings = {
            'expression': r'{{.*?}}',  # 表达式
            'logic': r'{%.*?%}',  # 逻辑控制
            'comment': r'{#.*?#}'  # 注释
        }

        pattern = '(?s)' +'(' + '|'.join([template_settings[key] for key in template_settings]) + ')'
        print(pattern)
        tokens = re.split(pattern, text)
        print(tokens)
        for token in tokens:
            if token.startswith('{#'):
                continue
            if token.startswith('{{'):
                print(self._expr_code(token[2:-2].strip()))
    

    def _expr_code(self, expr):
        if '|' in expr:
            pipes = expr.split('|')
            code = self._expr_code(pipes[0])
            for func in pipes[1:]:
                func = func.strip()
                self._variable(func, self.all_vars)
                code = 'c_%s(%s)' % (func, code)
        elif '.' in expr:
            dots = expr.split('.')
            code = self._expr_code(dots[0])
            args = ', '.join(repr(d) for d in dots[1:])
            code = 'do_dots(%s, %s)' % (code, args)

    def _do_dots(self, value, *dots):
        for dot in dots:
            try:
                value = getattr(value, dot)
            except AttributeError:
                value = value[dot]
            if callable(value):
                value = value()
        return value
    
    def _syntax_error(self, msg, thing):
        raise MonkException('%s: %r' % (msg, thing))


    def _variable(self, name, vars_set):
        if not re.match(r'[_a-zA-Z][_a-zA-Z0-9]*$', name):
            self._syntax_error('Not a valid name', name)
        else:
            vars_set.add(name)

class MonkException(Exception):
    pass