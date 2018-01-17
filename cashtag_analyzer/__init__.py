import sqlalchemy
import yaml

def connect_to_db(db_settings):
	protocol = db_settings['protocol']
	user = db_settings['user']
	password = db_settings['password']
	host = db_settings['host']
	dbname = db_settings['dbname']
	engine = sqlalchemy.create_engine(protocol + '://' + user + ':' + password + '@' + host + '/' + dbname,
									  pool_recycle=30)
	db_connection = engine.connect()

	return db_connection


def get_table(db_connection, table_name):
	table = sqlalchemy.Table(table_name, sqlalchemy.MetaData(), autoload=True, autoload_with=db_connection)

	return table


def load_settings(file_location, file_name = 'settings.yaml'):
	with open(file_location + file_name, 'rb') as settings_file:
		yaml_settings = settings_file.read()
		settings = yaml.load(yaml_settings)

	return settings