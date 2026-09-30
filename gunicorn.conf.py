# Gunicorn reads this file automatically when started from this folder
# (e.g. Render start command: gunicorn app:app).
#
# The default gunicorn worker handles ONE request at a time. The speed test
# opens several download/upload streams in parallel, so with the default
# worker they queue behind each other and time out. Threads fix that.
worker_class = "gthread"
workers = 1        # Render free tier = 512 MB RAM, one process is plenty
threads = 16       # parallel streams + ping
timeout = 120      # a slow 8 MB upload must not get the worker killed
keepalive = 5
