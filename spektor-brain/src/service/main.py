#!/usr/bin/python3

DEBUG = False

__all__ = []
__version__ = "0.0.1"
__date__ = '2018-04-22'
__updated__ = '2018-04-22'


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


        parser.add_argument("--app-host",
            type=str, action='store', dest="APP_HOST",
            default=None,
            help="Host IP address to be used by Flask for the service")


        parser.add_argument("--app-port",
            type=int, action='store', dest="APP_PORT",
            default=5000,
            help="Host IP port to be used by Flask for the service")


        parser.add_argument("--dim",
            type=int, action='store', dest="DIM",
            default=96,
            help="face square bounding box dimension")


        parser.add_argument("-V", "--verbose",
            action='store_true', dest="DEBUG",
            default=False,
            help="use DEBUG level logging")


        # Process arguments
        args = parser.parse_args()

        for k, v in args.__dict__.items():
            print(str(k) + ' => ' + str(v))
            pass

        from spektor_core import work
        work(
            args.DEBUG,
            args.APP_HOST,
            args.APP_PORT,
            args.DIM
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
