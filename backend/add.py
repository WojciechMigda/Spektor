#!/usr/bin/python3

DEBUG = False

__all__ = []
__version__ = "0.0.1"
__date__ = '2018-09-17'
__updated__ = '2018-09-17'


def main(argv=None): # IGNORE:C0111
    '''Command line options.'''
    from sys import argv as Argv

    if argv is None:
        argv = Argv
        pass
    else:
        Argv.extend(argv)
        pass

    from os.path import basename
    program_name = basename(Argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    try:
        program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    except:
        program_shortdesc = __import__('__main__').__doc__
    program_license = '''%s

  Created by Spektor on %s.
  Copyright 2018 Spektor. All rights reserved.

  Licensed under the MIT License

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        from argparse import ArgumentParser
        from argparse import RawDescriptionHelpFormatter
        from argparse import FileType
        from sys import stdout, stdin

        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)


        parser.add_argument("--first",
            type=str, action='store', dest="FIRST",
            default=None,
            help="First name of the persona")


        parser.add_argument("--last",
            type=str, action='store', dest="LAST",
            default=None,
            help="Last name of the persona")


        parser.add_argument("--note", "--description",
            type=str, action='store', dest="NOTE",
            default=None,
            help="Description for the persona")


        parser.add_argument("infile",
            type=FileType('rb'),
            default=None,
            nargs='?',
            help="input image")


        parser.add_argument("-i", "--interactive",
            action='store_true', dest="UI",
            help="Interactive input")


        # Process arguments
        args = parser.parse_args()

        for k, v in args.__dict__.items():
            print(str(k) + ' => ' + str(v))
            pass


        if not args.UI:
            required = {'FIRST': 'first name (--first)', 'LAST': 'last name (--last)', 'infile': 'input image'}
            err = False
            for k, v in required.items():
                if args.__dict__[k] is None:
                    err = True
                    print('(E) Interactive mode was not requested but {} was not specified'.format(v))
            if err:
                import sys
                sys.exit(1)

        from add_app import work

        work(
            args.UI,
            args.FIRST,
            args.LAST,
            args.NOTE,
            args.infile
            )

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG:
            raise(e)
            pass
        indent = len(program_name) * " "
        from sys import stderr
        stderr.write(program_name + ": " + repr(e) + "\n")
        stderr.write(indent + "  for help use --help")
        return 2

    pass


if __name__ == "__main__":
    if DEBUG:
        from sys import argv
        argv.append("-h")
        pass
    from sys import exit as Exit
    Exit(main())
    pass
