import re
import time


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

        code = CodeBuilder()
        code.add_line("def render_function(context, do_dots):")
        code.indent()
        vars_code = code.add_section()
        code.add_line("result = []")
        code.add_line("append_result = result.append")
        code.add_line("to_str = str")

        #save loop function name
        self.for_loop_func = []
        
        render_context = dict(self.context)                    
        for name in render_context.keys():
            vars_code.add_line('%s = context["%s"]' % (name, name))           

        for token in self._generate_tokens(text):
            name = token[0]
            expr = token[1]
            if name == "html":
                code.add_line('append_result("""%s""")' % expr)
            elif name == "expression":
                expr = expr.strip()
                code.add_line("append_result(to_str(%s))" % self._expr_code(expr))
            elif name == "logic":
                expr = expr.strip()
                if expr.startswith("if"):
                    code.add_line("%s:" % expr)
                    code.indent()
                elif expr == "else":
                    code.dedent()
                    code.add_line("else:")
                    code.indent()
                elif expr.startswith('elif'):
                    code.dedent()
                    code.add_line("%s:" % expr)
                elif expr.startswith("for"):
                    function_name = 'f' + str(int(time.time()))
                    self.for_loop_func.append(function_name)
                    code.add_line("def %s():" % function_name)
                    code.indent()
                    code.add_line("for %s:" % expr[3:].strip())
                    code.indent()
                elif expr.startswith("end"):
                    code.dedent()
                    if expr == 'endfor':
                        code.dedent()
                        code.add_line(self.for_loop_func.pop() + "()")
            elif name == "comment":
                continue                    
                         
        code.add_line("return ''.join(result)")
        code.dedent()
        print(code)
        self._render_function = code.get_globals()["render_function"]

    def _generate_tokens(self, text):
        pattern = re.compile(r'{{(?P<expression>.*?)}}|{%(?P<logic>.*?)%}|{#(?P<comment>.*?)#}')
        matches = pattern.finditer(text)
        start = 0
        end = 0
        for m in matches:
            span = m.span()
            end = span[0]
            yield "html", text[start: end]
            start = span[1]
            yield m.lastgroup, m.group(m.lastgroup)
        yield "html", text[start:]

    def _expr_code(self, expr):
        if "|" in expr:
            pipes = expr.split("|")
            code = pipes[0]
            for pipe in pipes[1:]:
                code = "%s(%s)" %(pipe.strip(), code.strip())
        elif "." in expr:
            dots = expr.split(".")
            code = dots[0]
            code = "do_dots(%s, '%s')" % (code.strip(), "','".join(c.strip() for c in dots[1:]))
        else:
            code = expr
        return code

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
        raise TempliteSyntaxError("%s: %r" % (msg, thing))

    def render(self, context=None):
        render_context = dict(self.context)
        if context:
            render_context.update(context)
        return self._render_function(render_context, self._do_dots)


class TempliteSyntaxError(ValueError):
    pass
