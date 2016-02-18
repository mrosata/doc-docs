"""/run.py should be used for running the app directly using Python.
When running on Heroku use gunicorn to access doc_docs.app module directly.
"""
import argparse
import os
from doc_docs import app

# Certain command line args
parser = argparse. \
    ArgumentParser(description='Tell the app which config file to use.')
parser.add_argument('-c', type=str, dest='cli_config_opt',
                    help='Config setup should be either testing or debug')

args = parser.parse_args()
if args.cli_config_opt:

    if args.cli_config_opt.startswith('dev'):
        os.environ['FLASK_CONFIGURATION'] = 'development'

    if args.cli_config_opt.startswith('test'):
        os.environ['FLASK_CONFIGURATION'] = 'testing'


if __name__ == '__main__':
    """
    DocDocs has configurations inside module doc_docs.config -- However the app is instanciated
    already by the time the config module is loaded. This behavior makes sense because it uses
    the app object to parse out configuration values from another Python object. So to set the
    port/host use cli arguments. In this way you'll be able to change web address info using
    gunicorn on heroku or add an arg to the cli from vagrant to switch config setups. The config
    set from CLI effects the configuration about to be set here and also effects the config in
    doc_docs.config.py

    vagrant:
       python run.py -c=testing
          or
        python -m run -c test
           or
        export FLASK_CONFIGURATION=development
        python run.py

     gunicorn:
        gunicorn --workers=2 doc_docs:app

    """
    flask_conf = os.environ.get('FLASK_CONFIGURATION')
    if flask_conf == 'testing' or flask_conf == 'development':
        app.run(port=5000, host='0.0.0.0')
    else:
        app.run()

