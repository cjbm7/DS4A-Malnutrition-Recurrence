import logging

app_log = logging

app_log.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s] %(message)s',
                   datefmt='%I:%M:%S %p',
                   handlers=[
                       logging.FileHandler('flasker.log'),
                       logging.StreamHandler()
                   ])

if __name__ == '__main__':
	pass