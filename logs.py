import datetime, logging

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formater = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:ligne_%(lineno)d -> %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formater)

logger.addHandler(stream_handler)

def Timer(func):
    """
    :decorator: retourne le temps d execution de la fonction obsevee.
    """
    def wrapper(*args, **kwargs):
        msg: str = f"Debut de {func.__name__!r}"
        logger.debug(f'{"*"*10} {msg:^30} {"*"*10}')
        t1: datetime.datetime = datetime.datetime.now()
        res = func(*args, **kwargs)
        t2: datetime.timedelta = datetime.datetime.now() - t1
        msg = f"Arret de{func.__name__!r}"
        logger.debug(f'{"*"*10} {msg:^30} {"*"*10}')
        logger.info(f'Fonction {func.__name__!r} executee en {(t2)}s')
        return res
    return wrapper