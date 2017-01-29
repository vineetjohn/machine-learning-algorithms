from argparse import ArgumentParser

import sys

from processors.logistic_regression_processor import LogisticRegressionProcessor
from utils.options import Options


def main(argv):
    options = parse_args(argv)
    processor = LogisticRegressionProcessor(options)
    processor.process()


def parse_args(argv):
    parser = ArgumentParser(prog="logistic_regression_classifier")
    parser.add_argument('--input_data_folder', metavar='Data folder', type=str, required=True)

    return parser.parse_args(argv, namespace=Options)


if __name__ == "__main__":
    main(sys.argv[1:])
