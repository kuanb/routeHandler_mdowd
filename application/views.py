from application import app

from flask import render_template, jsonify

from application import operations

@app.route('/')
def main():
	return render_template('main.html')

@app.route('/run/<filename>')
def run(filename):
	result = operations.runRoutes(filename)
	return jsonify({'result': result})

@app.route('/getoutput')
def sendoutput():
	print "eee"
	return app.send_static_file('output.csv')


if __name__ == '__main__':
	app.run()