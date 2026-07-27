"""Testing this out 


Sessions: Always verify flask.session.get('username') on restricted routes (like /, /posts/<id>, /explore/). If absent, redirect to /accounts/login/ or return a 403 status where specified.

Redirects: Every POST route must return an HTTP redirect (flask.redirect(target)) rather than rendering dynamic HTML directly.





"""