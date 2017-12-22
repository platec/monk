page = """
<h1>this is a test</h1>
<ul>
    {% for title in titles %}
        <li>{{ title | upper | local }}</li>
    {% endfor %}
</ul>
{% if shown %}
    <div>show something</div>
{% endif %}
"""


from monk import Monk, CodeBuilder

# # m = Monk('test')
# code = CodeBuilder()

# buffered = []


# def flush_output():
#     if len(buffered) == 1:
#         code.add_line('append_result(%s)' % buffered[0])
#     elif len(buffered) > 1:
#         code.add_line('extend_result([%s])' % ''.join(buffered))
#     del buffered[:]


# buffered.append([1, 2, 3, 4, 5])
# flush_output()
# print(code)
m = Monk(page)