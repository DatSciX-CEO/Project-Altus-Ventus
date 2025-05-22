from flask import Flask, request, render_template_string, jsonify # Added jsonify

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
<label for="top_speed_input">Top Speed (mph, 1-250):</label>
<input type="number" id="top_speed_input" name="top_speed" value="{{top_speed}}" min="1" max="250" required>
<input type="submit" value="Set">
</form>
<p>Current top speed: {{top_speed}} mph</p>
</body>
</html>
''' #

@app.route('/', methods=['GET', 'POST'])
def index():
    global top_speed
    if request.method == 'POST':
        try:
            ts = int(request.form['top_speed'])
            if 1 <= ts <= 250:  # Validation from HTML form
                top_speed = ts
        except ValueError: # More specific exception
            pass # Keep current top_speed if input is invalid
    return render_template_string(HTML, top_speed=top_speed)  #

# New API endpoint for the fan controller simulator
@app.route('/get_top_speed_api', methods=['GET'])
def get_top_speed_api():
    global top_speed
    return jsonify({"top_speed": top_speed})

# This function can be used if other Python modules on the same server need it.
def get_top_speed_py_func(): # Renamed to avoid conflict if imported
    global top_speed
    return top_speed

if __name__ == '__main__':
    print("Starting Wind Server for Simulation on http://0.0.0.0:5000")
    print("Access web UI at http://127.0.0.1:5000")
    print("API for top speed at http://127.0.0.1:5000/get_top_speed_api")
    app.run(host='0.0.0.0', port=5000) #