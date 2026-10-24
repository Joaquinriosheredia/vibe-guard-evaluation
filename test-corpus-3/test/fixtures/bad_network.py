# Positive control: opens a socket on import.
import socket
try:
    socket.create_connection(("api.github.com", 443))
except RuntimeError:
    pass
