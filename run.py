from inventory import app

app.debug = True
app.run(host='0.0.0.0', ssl_context='adhoc')

