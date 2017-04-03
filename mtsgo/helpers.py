import logging

logger = logging.getLogger('mtsgo')


def handle_exception(exception, request):
    logger.error('[ERROR] : ' + exception.__str__())
