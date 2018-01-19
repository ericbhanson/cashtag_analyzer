## MODULES ##
import cashtag_analyzer	# Import the modules from the __init__ script.
import ccxt
import collections
import datetime
import re
import sqlalchemy


## FUNCTIONS ##
def create_match_list(exchange, twitter_base_list, twitter_dict):
	print('Checking list of cashtags against supported symbols in {}...'.format(exchange.name))

	match_list = []
	base_set = set()
	base_dict = collections.defaultdict(list)
	markets = exchange.load_markets()

	for symbol in markets:
		base = markets[symbol]['base']
		base_set.add(base)
		base_dict[base].append(symbol)

	base_list = list(base_set)
	match = np.isin(base_list, twitter_base_list, assume_unique=True)

	for i in range(len(base_list)):

		if (match[i] == True):

			for created_at in twitter_dict[base_list[i]]:
				match_list.append([created_at, base_list[i], base_dict[base_list[i]]])

	print('Supported symbols check complete.')

	return match_list


def create_market_data_list(exchange, match_list, limit=2, timeframe='1d'):
	print('Getting market data for each cashtag...')

	market_data_list = []

	for i in range(len(match_list)):
		base = match_list[i][1]
		created_at = match_list[i][0]
		since = int((created_at - datetime.timedelta(days=1)).timestamp() * 1000)
		symbols = match_list[i][2]

		for symbol in symbols:
			uohlcv_list = exchange.fetch_ohlcv(symbol, limit=limit, since=since, timeframe=timeframe)

			if uohlcv_list:

				for item in uohlcv_list:
					row_list = [base, created_at, symbol]
					row_list.extend(item)

				market_data_list.append(row_list)

	print('Market data collection complete.')

	return market_data_list


def create_twitter_lists(screen_name, table):
	print('Creating list of cashtags...')

	select_query = table.select(whereclause="`screen_name` = '{}'".format(screen_name))
	results = db_connection.execute(select_query)
	twitter_base_set = set()
	twitter_dict = collections.defaultdict(list)

	for result in results.fetchall():
		regex_result = re.findall('(\w+)', result[0])

		for r in regex_result:
			twitter_base_set.add(r)
			twitter_dict[r].append(result['created_at'])

	twitter_base_list = list(twitter_base_set)

	print('Cashtag list created.')

	return twitter_base_list, twitter_dict


## MAIN CODE BODY ##
# Load the settings from the settings file.
settings = cashtag_analyzer.load_settings()

# Connect to the database.
db_connection = cashtag_analyzer.connect_to_db(settings['mysql_connection'])

table_name = settings['mysql_connection']['table']
table = cashtag_analyzer.get_table(db_connection, table_name)

exchange_id = settings['exchange_options']['exchange_id']
exchange_method = getattr(ccxt, exchange_id)
exchange = exchange_method()
limit = settings['exchange_options']['limit']
timeframe = settings['exchange_options']['timeframe']

select_query = sqlalchemy.select([table.c['screen_name']]).distinct()
results = db_connection.execute(select_query)

for result in results:
	screen_name = result[0]

	print('Getting results for screen name {}...'.format(screen_name))

	twitter_base_list, twitter_dict = create_twitter_lists(screen_name, table)
	match_list = create_match_list(exchange, twitter_base_list, twitter_dict)
	market_data_list = create_market_data_list(exchange, match_list, limit=limit, timeframe=timeframe)

	print('Results collected and available for analysis.')