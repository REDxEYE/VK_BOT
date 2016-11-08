import ctypes

php = ctypes.windll.LoadLibrary('php5ts.dll')
a = getattr(php, 'PHP_5HAVAL256Init')
