import logging
def set_logger(log_file):
    logger = logging.getLogger('BrikoTranslationService')
    logger.setLevel(logging.INFO)
    FORMAT = '%(asctime)s %(message)s'
    handlers = [
        logging.FileHandler(log_file),
        logging.StreamHandler(),
    ]
    logging.basicConfig(format=FORMAT, handlers=handlers)
    return logger