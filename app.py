from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Test App</title></head>
<body>
    <h1>Stress Test Target</h1>
    <form method="POST" action="/submit">
        <input type="text" name="username" id="username" placeholder="Enter name">
        <button type="submit" id="submit-btn">Send Data</button>
    </form>
    <div id="result">{{ result }}</div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, result="")

@app.route('/submit', methods=['POST'])
def submit():
    user = request.form.get('username', 'Anonymous')
    return render_template_string(HTML_TEMPLATE, result=f"Saved: {user}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)