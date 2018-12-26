"""
e.g. python -m pymylibrary
"""


__all__ = ('main','setup_logging','setup_database')

# to get resources
import os
import errno
import sys
from pkg_resources import resource_filename
_get_file = lambda filename: resource_filename(__name__,filename)


def setup_logging(log_fd, config):
    """Setup logging"""
    # https://github.com/zzzeek/sqlalchemy/blob/master/lib/sqlalchemy/log.py
    #import logging
    import logging.config

    # create logs folder if needed
    if not os.path.exists(log_fd):
        os.makedirs(log_fd, exist_ok=True) 
    
    # load config
    logging.config.dictConfig(config)

    # init logger
    log = logging.getLogger(__name__)

    # set logging level if not explicit
    if log.level == logging.NOTSET:
        log.setLevel(logging.DEBUG)
    
    # add null handler if none exists to avoid "No handler found" warnings.
    if not log.handlers:
        try:  # Python 2.7+
            from logging import NullHandler
        except ImportError:
            class NullHandler(logging.Handler):
                def emit(self, record):
                    pass
    log.addHandler(NullHandler())

    # necessary import for exception hooking
    # log all myexceptions!
    # NOTE: threads... https://stackoverflow.com/questions/1643327/sys-excepthook-and-threading
    def exception_hook(*args): #exctype, exc, tb
        """this method just handles the output, not raising the error... """
        # for i in args: logging.error(i)
        logging.critical('unhanlded exception!', exc_info=args) #f'{exctype}: {exc}'
        # import traceback
        # logging.critical('\n'+''.join(traceback.format_tb(args[2])))
    sys.excepthook = exception_hook
    logging.handlers.RotatingFileHandler
    # return main logger
    log.debug('logging setup')

    return log


def setup_database(log, db_file):
    """https://docs.sqlalchemy.org/en/latest/orm/tutorial.html"""
    log.debug("setting up the database (%s) ...", db_file)
    # from sqlalchemy import create_engine
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from .types import Base #, Track, File, Movie

    # engine = create_engine('sqlite:///:memory:')
    engine = create_engine('sqlite:///'+db_file)
    # Create all tables in the engine. This is equivalent to "Create Table"
    # https://docs.sqlalchemy.org/en/latest/faq/performance.html#i-m-inserting-400-000-rows-with-the-orm-and-it-s-really-slow
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    #Base.metadata.bind = engine

    DbSession = sessionmaker(bind=engine)
    #Session.configure(bind=engine)
    #sess = DbSession()
    # sess.bulk_insert_mappings(Track,
    #     [dict(name="NAME " + str(i)) for i in range(1, 100)])
    # sess.commit()
    # https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping
    log.info("database setup")

    return DbSession


def main():
    """Main routine of pymylibrary"""
    
    # load default config
    import json
    with open(_get_file('config.json'), 'r') as f:
        default_config = json.load(f)
    
    # does user settings folder exists?
    app_fd = os.path.expanduser(default_config['app.folder'])
    if app_fd and not os.path.exists(app_fd):
        # DNE - create folder
        print('creating app folder',app_fd,'...')
        os.makedirs(app_fd, exist_ok=True)
    # change cwd to the app folder
    if app_fd: os.chdir(app_fd)
    config_file = default_config['app.config']
    del default_config

    # check if config exists
    if not os.path.exists(config_file):
        # copy config
        from shutil import copy
        copy(_get_file('config.json'), config_file)
        print('config copied')
    
    # load user config
    with open(config_file, 'r') as f:
        config = json.load(f)
    #del config_file
    
    # setup logging
    log = setup_logging(os.path.expanduser( config['logging.folder'] ), config['logging.config'])

    # setup database
    db_file = config['app.dbfile']
    try: os.remove(db_file)
    except: pass
    db_dir = os.path.dirname(db_file)
    # create folder if needed
    if not os.path.exists(db_dir):
        log.debug('creating db directory, %s ...', db_dir)
        os.makedirs(db_dir, exist_ok=True)
    DbSession = setup_database(log, db_file)
    del db_file, db_dir
    sess = DbSession()

    # library file
    lib_file = os.path.expanduser( config['pymediainfo.library_file'] )
    if not os.path.isabs(lib_file):
        lib_file = os.path.abspath(lib_file)
    # exists?
    if not os.path.exists(lib_file):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT) +
            '. Download the dll/lib from https://mediaarea.net/en/MediaInfo/Download', lib_file)
    

    # test db by adding several files
    from pymediainfo import MediaInfo
    from .types import Track, File, Movie # pylint: disable=W0612

    # walk though all out testing files...
    counter = 0
    for fd in config['app.watch.folders']:
        for root, dirs, files in os.walk(fd, topdown=True): # pylint: disable=W0612
            log.debug('looking at folder, %s', root)
            for fn in files:
                counter += 1 # counter for bulk save (flush)

                fullname = os.path.join(root, fn)
                # get media info
                media_info = MediaInfo.parse(fullname, library_file=lib_file)
                
                # # dump track info
                # with open(os.path.join(app_fd,'resources', fn + '.json'), 'w') as w:
                #     json.dump(media_info.to_data()['tracks'], w, indent=4, sort_keys=True)
                # log.debug(f'{fn} exported w/ {len(media_info.tracks)}')

                # create file and tracks
                f = File.from_mediainfo(media_info)
                # add to db
                # https://docs.sqlalchemy.org/en/latest/faq/performance.html#i-m-inserting-400-000-rows-with-the-orm-and-it-s-really-slow
                sess.add(f)
                map(sess.add,f.tracks)
                
                # should we flush? don't just commit at the end!
                if counter % 1000 == 0:
                    sess.flush()
    
    # commit
    sess.commit()

    # # query all 1080p
    # import sqlalchemy as sa
    # files = sess.query(File).join(File.tracks).filter(
    #     sa.or_(
    #         File.original_complete_name.contains('1080p'),
    #         sa.and_(Track.track_type == 'Video', Track.width >= 1920)
    #     )
    # ).all()
    # for f in files:
    #     log.debug(f)


if __name__ == '__main__':
    #from .core import main
    main()