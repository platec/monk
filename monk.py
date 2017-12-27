import re


class CodeBuilder:
    INDENT_STEP = 4

    def __init__(self, indent=0):
        self.code = []
        self.indent_level = indent

    def add_line(self, line):
        self.code.extend([" " * self.indent_level + line + "\n"])

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
        code.add_line("extend_result = result.extend")
        code.add_line("to_str = str")

        self.loop_vars_stack = []
        
        render_context = dict(self.context)                    
        for name in render_context.keys():
            code.add_line("c_%s = context['%s']" % (name, name))           

        tokens = self._generate_tokens(text)
        for token in tokens:
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
                    self.loop_vars_stack.append(expr)
                    words = expr.split()
                    if len(words) == 1:
                        self._syntax_error("can not parse if", expr)
                    jouken = words[1]
                    code.add_line("c_%s = context['%s']" % (jouken, jouken))
                    code.add_line("if c_%s:" % jouken)
                    code.indent()
                elif expr == "else":
                    code.dedent()
                    code.add_line("else:")
                    code.indent()
                elif expr.startswith("for"):
                    words = expr.split()
                    if words[2] != "in" or len(words) != 4:
                        self._syntax_error("can not parse for", expr)
                    self.loop_vars_stack.append(expr)
                    item = words[1]
                    items = words[3]
                    # for i in range(3), for i in [1,2,3]
                    if getattr(eval(items), "__iter__", None) is not None:
                        code.add_line("for %s in %s:" %(item, items))
                    else:
                        code.add_line("for %s in c_%s:" %(item, items))
                    code.indent()
                elif expr.startswith("end"):
                    self.loop_vars_stack.pop()
                    code.dedent()
            elif name == "comment":
                continue                    
                         
        code.add_line("return ''.join(result)")
        code.dedent()
        self._render_function = code.get_globals()["render_function"]

    def _generate_tokens(self, text):
        pattern = re.compile(r'{{(?P<expression>.*?)}}|{%(?P<logic>.*?)%}|{#(?P<comment>.*?)#}')
        matches = pattern.finditer(text)
        start = 0
        end = 0
        for m in matches:
            end = m.span()[0]
            yield "html", text[start: end]
            start = m.span()[1]
            yield m.lastgroup, m.group(m.lastgroup)
        yield "html", text[start:]

    def _expr_code(self, expr):
        if "|" in expr:
            pipes = expr.split("|")
            code = pipes[0]
            self.all_vars.add(code.strip())
            for pipe in pipes[1:]:
                code = "%s(c_%s)" %(pipe.strip(), code.strip())
                self.all_vars.add(pipe.strip())
            code = "c_" + code
        elif "." in expr:
            dots = expr.split(".")
            code = dots[0]
            code = "do_dots(c_%s, '%s')" % (code.strip(), "','".join(c.strip() for c in dots[1:]))
        else:
            code = "c_" + expr if len(self.loop_vars_stack) == 0 else expr
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
