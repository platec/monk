from monk import Monk, CodeBuilder

def test():
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

    m = Monk(page)

if __name__ == '__main__':
    test()