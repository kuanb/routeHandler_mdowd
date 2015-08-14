from application import app

from flask import render_template

from application import operations

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/run/<filename>')
def run(filename):
    print "got here", filename
    result = operations.runTest(fileName)
    print result
    return result

if __name__ == '__main__':
    app.run()