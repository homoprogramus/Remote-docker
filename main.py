import pydevd

pydevd.settrace('i17dhcp-1-128.epfl.ch', port=50621, stdoutToServer=True, stderrToServer=True)
print('Hello World')
