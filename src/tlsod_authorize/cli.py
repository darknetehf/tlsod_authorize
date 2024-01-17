import argparse
import contextlib
import logging
import logging.config
import logging.handlers
import os
import sqlite3
import sys
from pathlib import Path

import yaml

from tlsod_authorize import __version__
from tlsod_authorize.database import create_db
from tlsod_authorize.webserver import TlsodHTTPServer, WebRequestHandler

# constants
LOGGING_CONFIG_FILE = "logging.yml"


def setup_logging(yaml_file):
    logger = logging.getLogger(__name__)

    if not Path.exists(yaml_file):
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        logging.warning(
            f"File {yaml_file} not found, using default configuration for logging"
        )
    else:
        with open(yaml_file, "r") as f:
            yaml_config = yaml.safe_load(f.read())
            logging.config.dictConfig(yaml_config)

    return logger


def is_valid_file(file):
    if os.path.isfile(file):
        return file
    else:
        raise argparse.ArgumentTypeError("File missing or not a valid path")


def is_valid_port(port):
    if port.isdecimal():
        port = int(port)
    if port in range(1, 65536):
        return port
    else:
        raise argparse.ArgumentTypeError(
            "Invalid port, should be in the range 1-65535"
        )


def parse_arguments():
    parser = argparse.ArgumentParser(allow_abbrev=False)

    parser.add_argument(
        "--db",
        dest="db_path",
        # type=is_valid_file,
        help="Path to the DB file",
        required=True,
    )

    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        type=is_valid_port,
        default=8080,
        help="HTTP server port",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    args = parser.parse_args()

    return args


def main():
    logger = logging.getLogger(__name__)

    try:
        # check command line arguments
        args = parse_arguments()

        # get current application dir and set up logger from YAML config
        current_dir = os.path.dirname(os.path.realpath(__file__))

        logger = setup_logging(Path(current_dir) / LOGGING_CONFIG_FILE)

        # create DB if it doesn't exist yet
        if not os.path.isfile(args.db_path):
            logger.info(f"Create database: {args.db_path}")
            create_db(args.db_path)

        logger.info(f"Starting web server on port {args.port}")
        # permit access from other threads
        db = sqlite3.connect(args.db_path, check_same_thread=False)
        server = TlsodHTTPServer(db, ("", args.port), WebRequestHandler)

        with contextlib.closing(db):
            server.serve_forever()

    except KeyboardInterrupt:
        logger.warning("Shutdown requested (KeyboardInterrupt)...")

    except Exception as ex:
        exception_type = ex.__class__.__name__
        logger.exception(f"Unhandled exception: {exception_type}")
        sys.exit(1)
    finally:
        logger.info("Application terminating")


if __name__ == "__main__":
    main()
