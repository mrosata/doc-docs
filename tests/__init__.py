"""
Tests are ran from the command line using one of the following commands from cli. To run all the
test  at once run:  "python -m unittest discover". To only run a single set of tests use the
command pattern: "python -m unittest test.<test_module>" where <test_module> is one of the
modules listed in tests.__all__
"""
__all__ = ['test_authentication', 'test_reviews']
