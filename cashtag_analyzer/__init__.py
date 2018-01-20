import sqlalchemy
import sys
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


def get_row_count(db_connection, table):
	select_query = table.select()
	results = db_connection.execute(select_query)
	results_text = '{} row(s) are currently in MySQL database.'.format(len(results.fetchall()))

	return results_text


def get_table(db_connection, table_name):
	table = sqlalchemy.Table(table_name, sqlalchemy.MetaData(), autoload=True, autoload_with=db_connection)

	return table


def insert_data(db_connection, data_to_insert, table):
	insert_query = table.insert(data_to_insert)

	try:
		db_connection.execute(insert_query)

	except sqlalchemy.SQLAlchemyError:
		raise

	else:
		results_text = 'Post-INSERT row count: ' + get_row_count(db_connection, table)
		print(results_text)
		print('Results collected and available for analysis.')


def load_settings(file_location=sys.argv[1], file_name='settings.yaml'):
	with open(file_location + file_name, 'rb') as settings_file:
		yaml_settings = settings_file.read()
		settings = yaml.load(yaml_settings)

	return settings