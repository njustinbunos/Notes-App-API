import sys
import argparse
import unittest


# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class ColoredTextTestResult(unittest.TextTestResult):
    """Custom test result class with colored output"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.verbosity = verbosity
        self.success_count = 0
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        if self.verbosity >= 1:
            self.stream.write(f"{Colors.GREEN}{self.getDescription(test)}{Colors.RESET}\n")
            self.stream.flush()
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity >= 1:
            self.stream.write(f"{Colors.YELLOW}{self.getDescription(test)}{Colors.RESET}\n")
            self.stream.flush()
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity >= 1:
            self.stream.write(f"{Colors.RED}{self.getDescription(test)}{Colors.RESET}\n")
            self.stream.flush()
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity >= 1:
            self.stream.write(f"{Colors.BLUE}{self.getDescription(test)} (skipped){Colors.RESET}\n")
            self.stream.flush()
    
    def printErrors(self):
        if self.verbosity >= 1:
            self.stream.writeln()
        self.printErrorList(f'{Colors.RED}{Colors.BOLD}ERRORS{Colors.RESET}', self.errors)
        self.printErrorList(f'{Colors.RED}{Colors.BOLD}FAILURES{Colors.RESET}', self.failures)
    
    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln(f"{flavour}: {self.getDescription(test)}")
            self.stream.writeln(self.separator2)
            self.stream.writeln(f"{err}")


class ColoredTextTestRunner(unittest.TextTestRunner):
    """Custom test runner with colored output"""
    resultclass = ColoredTextTestResult
    
    def run(self, test):
        result = super().run(test)
        
        print("\n" + "=" * 70)
        
        if result.wasSuccessful():
            print(f"{Colors.GREEN}{Colors.BOLD} All tests passed!{Colors.RESET}")
        else:
            print(f"{Colors.RED}{Colors.BOLD} Some tests failed{Colors.RESET}")

        print(f"\n{Colors.BOLD}Test Results:{Colors.RESET}")
        print(f"  {Colors.GREEN}Passed:{Colors.RESET}  {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
        print(f"  {Colors.RED}Failed:{Colors.RESET}  {len(result.failures)}")
        print(f"  {Colors.YELLOW}Errors:{Colors.RESET}  {len(result.errors)}")
        print(f"  {Colors.BLUE}Skipped:{Colors.RESET} {len(result.skipped)}")
        print(f"  {Colors.BOLD}Total:{Colors.RESET}   {result.testsRun}")
        print("=" * 70)
        
        return result


def runserver(host="127.0.0.1", port=8000, reload=True):
    """Start the development server"""
    import uvicorn
    uvicorn.run("core.app:app", host=host, port=port, reload=reload)


def test(verbosity=2):
    """Run tests"""
    print(f"\n{Colors.BOLD}Running tests...{Colors.RESET}\n")
    
    # Load the test module
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('core.tests')
    
    runner = ColoredTextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


def main():
    parser = argparse.ArgumentParser(description='Management commands for Notes API')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # runserver command
    parser_runserver = subparsers.add_parser('runserver', help='Start the development server')
    parser_runserver.add_argument('--host', default='127.0.0.1', help='Host (default: 127.0.0.1)')
    parser_runserver.add_argument('--port', type=int, default=8000, help='Port (default: 8000)')
    parser_runserver.add_argument('--no-reload', action='store_true', help='Disable auto-reload')
    
    # test command
    parser_test = subparsers.add_parser('test', help='Run tests')
    parser_test.add_argument('-v', '--verbosity', type=int, choices=[0, 1, 2], default=2,
                            help='Verbosity level (default: 2)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'runserver':
            runserver(host=args.host, port=args.port, reload=not args.no_reload)
        elif args.command == 'test':
            return test(verbosity=args.verbosity)
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())