#!/usr/bin/python3

import argparse

from src.logger import logging


def print_dict(input_dict, prefix="\t", postfix="", redirect_to_str=False):
    rslt_str = ""
    for key, val in sorted(input_dict.items()):
        val = f"{val:.1f}" if isinstance(val, float) else val
        tmp_str = f"{prefix}- {key}: {val}{postfix}"
        if not redirect_to_str:
            logging.info(tmp_str)
        else:
            rslt_str += f"{tmp_str}\n"

    if redirect_to_str:
        return rslt_str.rstrip()


class CustomArgParser(argparse.ArgumentParser):
    def add_bool_argument(
        self, flag=None, name=None, default=False, required=False, help=None
    ):
        if not isinstance(default, bool):
            raise ValueError()

        feature_parser = self.add_mutually_exclusive_group(required=required)

        name_or_flags = []
        if flag is not None:
            name_or_flags.append(flag)
        if name is not None:
            name_or_flags.append(name)

        # remove the `--` at the front
        argname = name[2:]

        feature_parser.add_argument(
            *name_or_flags,
            dest=argname,
            action="store_true",
            help=help,
            default=default,
        )

        feature_parser.add_argument(
            f"--no_{argname}", dest=argname, action="store_false"
        )

        feature_parser.set_defaults(name=default)

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)

        print()
        logging.info("Benchmark arguments:")
        print_dict(vars(args))
        print()

        return args
