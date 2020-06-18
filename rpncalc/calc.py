import functools
import math
import readline
from collections import OrderedDict
from pathlib import Path

from rpncalc.utils import *
from rpncalc.enums import modes


commands = OrderedDict()


def print_commands():
    for name, content in commands.items():
        print('{}\n\t{}'.format(text(name), green_text(content['desc'])))


def register(name=None, args_count=0, desc=''):
    def decorator_register(func):
        if name is None:
            fname = func.__name__
        else:
            fname = name

        commands[fname] = {
            'function': func,
            'args_count': args_count,
            'desc': desc
        }

        @functools.wraps(func)
        def wrapper_register(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper_register

    return decorator_register


class Calc(object):
    def __init__(self, interactive = False, configs=[]):
        self.stack = []
        self.inputs = []
        self.parameters_stack = []
        self.variables = {}
        self.macros = {}
        self.interactive = interactive
        self.mode = modes.DEC

        for config in configs:
            self.load_config(config)

    def load_config(self, config):
        file = Path(config)
        if file.is_file():
            with open(str(file)) as reader:
                lines = reader.read().splitlines()
                for line in lines:
                    values = line.split(' ')
                    try:
                        self.compute(values)
                    except Exception as e:
                        print(error_text(e))

    #@TODO: find a way to keep floating point representation.
    def to_mode_output(self, value):
        if self.mode == modes.HEX:
            return value.hex()
        elif self.mode == modes.OCT:
            return oct(int(value))
        elif self.mode == modes.BIN:
            return bin(int(value))
        else:
            return value

    def get_input_message(self):
        stack_text = ' '.join([str(self.to_mode_output(x)) for x in self.stack])
        msg = '{} {} '.format(text(stack_text), green_text('>'))

        if len(self.variables) > 0:
            variables_text = ' '.join(['{}={}'.format(name, self.to_mode_output(value)) for name, value in self.variables.items()])
            msg = '{} {} {} {}'.format(green_text('['), variables_text, green_text(']'), msg)
        return msg

    def loop(self):
        def completer(text, state):
            options = [i for i in commands if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer)

        while self.interactive:
            val = input(self.get_input_message())
            values = val.split(' ')
            try:
                self.compute(values)
            except Exception as e:
                print(error_text(e))

    def compute(self, inputs):
        self.inputs = self.check_values(inputs)
        while len(self.inputs) > 0:
            i = self.inputs.pop(0)
            if type(i) == dict:
                min_size = i['args_count']
                if len(self.stack) < min_size:
                    raise ValueError('Command {} needs at least {} values in the stack'.format(i['function'].__name__, min_size))
                else:
                    i['function'](self)
            else:
                self.stack.append(i)

    def check_values(self, inputs):
        new_inputs = []
        for i in inputs:
            if i in commands:
                new_inputs.append(commands[i])
            elif len(i) > 1 and i.endswith('='):
                #variable assignment
                #put variable name in parameters stack
                self.parameters_stack.append(i.split('=')[0])
                new_inputs.append(commands['variable_assign'])
            elif i == 'macro':
                #macro creation
                #put rest of the inputs in the parameters stack
                index = inputs.index(i)
                params = inputs[index+1:]
                self.parameters_stack += params
                new_inputs.append(commands['macro_creation'])

                #rest of the input is for the macro creation, we return
                return new_inputs
            elif i in self.variables:
                new_inputs.append(self.variables[i])
            elif i in self.macros:
                new_inputs += self.check_values(self.macros[i])
            else:
                try:
                    if self.mode == modes.DEC:
                        num = float(i)
                    elif self.mode == modes.HEX:
                        num = int(i, 16)
                    elif self.mode == modes.OCT:
                        num = int(i, 8)
                    elif self.mode == modes.BIN:
                        num = int(i, 2)
                    else:
                        raise Exception('Unknown mode.')

                    new_inputs.append(num)
                except ValueError:
                    raise ValueError('Input is not a command nor a numerical value.')

        return new_inputs

    @register(name='+', args_count=2, desc='Add')
    def add(self):
        value1 = self.stack.pop()
        value2 = self.stack.pop()
        self.stack.append(value1 + value2)

    @register(name='-', args_count=2, desc='Subtract')
    def sub(self):
        value1 = self.stack.pop()
        value2 = self.stack.pop()
        self.stack.append(value2 - value1)

    @register(name='*', args_count=2, desc='Multiply')
    def mul(self):
        value1 = self.stack.pop()
        value2 = self.stack.pop()
        self.stack.append(value1 * value2)

    @register(name='/', args_count=2, desc='Divide')
    def div(self):
        value1 = self.stack.pop()
        value2 = self.stack.pop()
        self.stack.append(value2 / value1)

    @register(name='%', args_count=1, desc='Modulus')
    def mod(self):
        value1 = self.stack.pop()
        value2 = self.stack.pop()
        self.stack.append(value2 % value1)

    @register(name='++', args_count=1, desc='Increment')
    def increment(self):
        value = self.stack.pop()
        self.stack.append(value+1)

    @register(name='--', args_count=1, desc='Decrement')
    def decrement(self):
        value = self.stack.pop()
        self.stack.append(value-1)

    @register(desc='Push e')
    def e(self):
        self.stack.append(math.e)

    @register(desc='Push Pi')
    def pi(self):
        self.stack.append(math.pi)

    @register(args_count=1, desc='Generate a random number between last to stack values')
    def rand(self):
        value1 = self.stack.pop()
        value2 = self.stack.pop()
        import random
        self.stack.append(random.randint(value2, value1))

    @register(desc='Switch display mode to decimal (default)')
    def dec(self):
        self.mode = modes.DEC

    @register(desc='Switch display mode to hexadecimal')
    def hex(self):
        self.mode = modes.HEX

    @register(desc='Switch display mode to binary')
    def bin(self):
        self.mode = modes.BIN

    @register(desc='Switch display mode to octal')
    def oct(self):
        self.mode = modes.OCT

    @register(args_count=1, desc='Factorial')
    def fact(self):
        self.stack.append(math.factorial(self.stack.pop()))

    @register(args_count=1, desc='Exponentiation')
    def exp(self):
        self.stack.append(math.exp(self.stack.pop()))

    @register(args_count=1, desc='Square Root')
    def sqrt(self):
        self.stack.append(math.sqrt(self.stack.pop()))

    @register(args_count=1, desc='Natural Logarithm')
    def ln(self):
        self.stack.append(math.log(self.stack.pop()))

    @register(args_count=1, desc='Logarithm')
    def log(self):
        self.stack.append(math.log10(self.stack.pop()))

    @register(args_count=2, desc='Raise a number to a power')
    def pow(self):
        value1 = self.stack.pop()
        value2 = self.stack.pop()
        self.stack.append(math.pow(value2, value1))

    @register(desc='Clear the stack and variables')
    def cla(self):
        self.stack.clear()
        self.variables.clear()

    @register(desc='Clear the stack')
    def clr(self):
        self.stack.clear()

    @register(desc='Clear the variables')
    def clv(self):
        self.variables.clear()

    @register(args_count=1, desc='Pick the -n\'th item from the stack')
    def pick(self):
        self.stack.append(self.stack.pop(self.stack.pop()))

    @register(args_count=1, desc='Repeat an operation n times, e.g. "3 repeat +"')
    def repeat(self):
        if not len(self.inputs) > 0:
            raise ValueError('No command to repeat')

        input = self.inputs.pop(0)
        for _ in range(int(self.stack.pop())):
            self.inputs.insert(0, input)

    @register(args_count=0, desc='Push the current stack depth')
    def depth(self):
        self.stack.append(len(self.stack))

    @register(args_count=0, desc='Drops the top item from the stack')
    def drop(self):
        self.stack.pop()

    @register(args_count=1, desc='Drops n items from the stack')
    def dropn(self):
        for _ in range(int(self.stack.pop())):
            self.stack.pop()

    @register(args_count=1, desc='Drops the top item from the stack')
    def dup(self):
        self.stack.append(self.stack[-1])

    @register(args_count=1, desc='Duplicates the top n stack items in order')
    def dupn(self):
        n = self.stack.pop()
        for _ in range(n):
            self.stack.append(self.stack[-n])

    @register(args_count=2, desc='Swap the top 2 stack items')
    def swap(self):
        self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]

    @register(args_count=0, desc='Assigns a variable, e.g. "1024 x="')
    def variable_assign(self):
        name = self.parameters_stack.pop()
        if name in commands or name in self.macros:
            raise ValueError('Variable name already assign as a command or a macro')
        self.variables[name] = self.stack.pop()

    @register(args_count=0, desc='Show all available macros')
    def macros_list(self):
        for v, value in self.macros.items():
            print(green_text('{}: {}'.format(v, ' '.join(value))))

    @register(args_count=0, desc='Defines a macro, e.g. "macro kib 1024 *"')
    def macro_creation(self):
        name = self.parameters_stack.pop(0)
        if name in commands or name in self.variables:
            self.parameters_stack.clear()
            raise ValueError('Macro name already assign as a command or a variable')

        self.macros[name] = [x for x in self.parameters_stack]
        self.parameters_stack.clear()

    @register(desc='Print all commands')
    def help(self):
        print_commands()

    @register(desc='Exit the calculator')
    def exit(self):
        self.interactive = False
