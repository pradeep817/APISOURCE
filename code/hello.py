from flask import Flask


app=Flask(__name__)


app.route('/'):
def hello():
    retrun "it's works"





if __name__=='__main__':
    app.run(debug=True)
    app.run(port=5000)    
