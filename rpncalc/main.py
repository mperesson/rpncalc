import argparse
from pathlib import Path

from rpncalc.calc import Calc, commands, print_commands
from rpncalc.utils import error_text


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="A RPN Calculator\n"
        "Developed for Roon interview."
    )

    parser.add_argument(
        "-l", "--list", help="list all available operators and functions", action="store_true")
    parser.add_argument(
        "--ignore-local-config", help="ignore ~/.rpncalc config file.",
        action="store_true")
    parser.add_argument(
        '-c', "--config", type=str, nargs="+",
        help="use a specific config file")
    parser.add_argument(
        'input', type=str, nargs="*",
        help="calc input for non interactive mode")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.list:
        print_commands()

    interactive = False
    if not len(args.input):
        interactive = True

    if not args.ignore_local_config:
        configs = [Path.home().joinpath(Path('.rpnrc'))]
    else:
        configs = []

    if args.config:
        for config in args.config:
            file = Path(config)
            if file.is_file():
                configs.append(file)
            else:
                print(error_text('Config file {} not found'.format(config)))

    calc = Calc(interactive, configs)

    if interactive:
        calc.loop()
    else:
        try:
            calc.compute(args.input)
            print(calc.stack[-1])
        except Exception as e:
            print(error_text(e))
            return 1
    return 0


if __name__ == '__main__':
    main()
