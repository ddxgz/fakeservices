from fakeservices.fitbit_app import app as fitbitapp

if __name__ == '__main__':

    fitbitapp.debug = True
    # app.run(host='0.0.0.0', threaded=True)
    fitbitapp.run(host='0.0.0.0')