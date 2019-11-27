from fakeservices.fitbit_app import app as fitbitapp
from fakeservices.ihealth_app import app as ihealthapp
from fakeservices.home_app import app as homeapp

if __name__ == '__main__':

    # fitbitapp.debug = True
    # # app.run(host='0.0.0.0', threaded=True)
    # fitbitapp.run(host='0.0.0.0')

    # ihealthapp.debug = True
    # # app.run(host='0.0.0.0', threaded=True)
    # ihealthapp.run(host='0.0.0.0')

    homeapp.debug = True
    # app.run(host='0.0.0.0', threaded=True)
    homeapp.run(host='0.0.0.0')