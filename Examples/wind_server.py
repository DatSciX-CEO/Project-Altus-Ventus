
from flask import Flask, request, render_template_string

app = Flask(__name__)

top_speed = 150  # Default top speed

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>BeamNG Fan Controller</title>
</head>
<body>
<h2>Set In-Game Car Top Speed</h2>
<form method="post">
<input type="number" name="top_speed" value="{{top_speed}}" min="1" max="250" required>
<input type="submit" value="Set">
</form>
<p>Current top speed: {{top_speed}} mph</p>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    global top_speed
    if request.method == 'POST':
        try:
            ts = int(request.form['top_speed'])
            if 1 <= ts <= 250:
                top_speed = ts
        except:
            pass
    return render_template_string(HTML, top_speed=top_speed)

def get_top_speed():
    return top_speed

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
