import time

import requests
from requests.exceptions import RequestException

from logger import logger
from settings import config


def wait_for_service(url: str, timeout: int = 30) -> None:
    start_time = time.time()

    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logger.debug(f"Service is up and running at {url}")
                break

        except RequestException as ex:
            logger.error(f"RequestException({url}): {ex}")

        if (time.time() - start_time) > timeout:
            raise TimeoutError(
                f"Service at {url} did not become available within {timeout} "
                f"seconds"
            )

        time.sleep(1)


if __name__ == "__main__":
    health_check_urls = (
        f"{config.auth_service_url}/api/v1/auth",
        f"{config.movies_service_url}/api/v1/movies",
    )
    for health_check_url in health_check_urls:
        wait_for_service(url=health_check_url)
