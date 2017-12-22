from monk import Monk, CodeBuilder

def test():
    page = """
    <h1>{{greet}}</h1>
    <ul>
        {% for title in titles %}
            <li>{{ title | upper | local }}</li>
        {% endfor %}
    </ul>
    {% if shown %}
        <div>show something</div>
    {% endif %}
    """

    page2 = """
<h1>{{greet}}</h1>
    """

    m = Monk(page)
    result = m.render({'greet': 'hello'})
    print(result)

if __name__ == '__main__':
    test()