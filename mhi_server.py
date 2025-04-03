from flask import Flask, request, Response, current_app
import os
import sys
import configparser
import logging
import shutil
import re
from pathlib import Path


def create_app():
    '''Application factory for WSGI compatibility.'''
    # Set up logging format.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    app = Flask(__name__)
    
    # Initialize components.
    ensure_config_file()
    configure_app(app)
    initialize_cache(app)
    register_routes(app)
    
    return app


def ensure_config_file():
    '''Create config.ini from dist file if missing.'''
    if not os.path.exists('config.ini') and os.path.exists('config.ini.dist'):
        try:
            shutil.copyfile('config.ini.dist', 'config.ini')
            logging.info('Created config.ini from config.ini.dist.')
        except Exception as e:
            logging.error(f'Failed to create config.ini: {str(e)}.')


def configure_app(app):
    '''Configure application settings.'''
    # Load config file if exists.
    if config := load_configuration():
        app.config.update(config)
    else:
        logging.error(f'Configuration not possible. Exiting.')
        sys.exit(1)

def load_configuration():
    '''Load configuration from file.'''
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
        return {
            'DATA_DIRECTORY': config.get('server', 'data_directory', fallback='./data'),
            'HOST': config.get('server', 'host', fallback='0.0.0.0'),
            'PORT': config.getint('server', 'port', fallback=80)
        }
    except Exception as e:
        logging.error(f'Config read error: {str(e)}.')
        return None


def initialize_cache(app):
    '''Load files into memory cache.'''
    cache = {}
    for subdir in ['recreated', 'original_dumps']:
        dir_path = os.path.join(app.config['DATA_DIRECTORY'], subdir)
        if not os.path.exists(dir_path):
            logging.warning(f'Missing directory: {dir_path}.')
            continue
            
        for root, _, files in os.walk(dir_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'rb') as f:
                        cache[filename] = f.read()
                    logging.debug(f'Cached: {filename} from {subdir}.')
                except Exception as e:
                    logging.error(f'Failed loading {file_path}: {str(e)}.')
    
    app.config['FILE_CACHE'] = cache
    logging.info(f'Loaded {len(cache)} files into cache.')


def register_routes(app):
    '''Register all application routes.'''
    
    # Special endpoints.
    # Logic taken from https://github.com/Yuvi-App/Keitai-Servers/
    @app.route('/sreg/imh_sreg.php', methods=['GET'])
    def handle_sreg():
        ty = request.args.get('ty', '').lower()
        if ty == 'load':
            # 0x8c: OK, allowed!
            # 0x6e: Membership required.
            hex_response = '8c000000'
        else:
            # 0x01: OK, allowed!
            # 0x6e: Membership required.
            hex_response = '01000000'
        
        return Response(
            bytes.fromhex(hex_response),
            status=200,
            mimetype='application/octet-stream',
            headers={'X-CAPCOM-STATUS': 'OK'}
        )
    
    @app.route('/ac_check', methods=['GET'])
    def handle_ac_check():
        return Response('1', status=200)
    
    @app.route('/info.txt', methods=['GET'])
    def handle_info():
        return Response('OK', status=200)
    
    # MHi file handling.
    @app.route('/sh/i/mh/up/appli_904i/<pc>/<filename>', methods=['GET'])
    def handle_mh_files(pc, filename):
        return serve_file(filename)
    
    # Default routes.
    @app.route('/', methods=['GET'])
    def handle_root():
        return empty_ok_response()
    
    @app.route('/<path:path>', methods=['GET'])
    def handle_generic(path):
        logging.info(f'Unknown GET: {path}.')
        return empty_ok_response()
    
    @app.route('/', defaults={'path': ''}, methods=['POST'])
    @app.route('/<path:path>', methods=['POST'])
    def handle_post(path):
        return Response(status=501)


def serve_file(filename):
    '''Handle file serving logic.'''
    cache = current_app.config['FILE_CACHE']
    logging.info(f'Requested file: {filename}.')

    # Exact match check.
    if filename in cache:
        logging.info(f'Serving exact match: {filename}.')
        return file_response(cache[filename])
    
    # If requested file is pcX_gard_YY.dat and was not found, 
    # try to find a matching .mbac file of the same weapon type to send as placeholder.
    if (match := re.match(r'^(pc\d+_gard)_\d+\.dat$', filename)):
        pattern = re.compile(r'^{}.*\.dat$'.format(re.escape(match.group(1))))
        if matches := [f for f in cache if pattern.match(f)]:
            placeholder = sorted(matches)[0]  # Simply get the first one.
            logging.info(f'Serving placeholder: {placeholder} for {filename}.')
            return file_response(cache[placeholder])
    
    logging.info(f'File not found: {filename}.')
    return empty_ok_response()


def file_response(data):
    '''Create standard file response.'''
    return Response(
        data,
        status=200,
        mimetype='application/octet-stream',
        headers={'X-CAPCOM-STATUS': 'OK'}
    )


def empty_ok_response():
    '''Create empty 200 OK response.'''
    return Response(
        status=200,
        headers={'X-CAPCOM-STATUS': 'OK'}
    )


# Application instance.
app = create_app()

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=False
    )
