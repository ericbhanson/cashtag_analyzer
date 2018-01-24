import cashtag_analyzer		# Import the modules from the __init__ script.
import ccxt					# Import ccxt to connect to exchange APIs.
import collections			# Import collections to create lists within dictionaries on the fly.
import datetime				# Import datetime for the timedelta and utcfromtimestamp functions.
import numpy				# Import numpy to compare the contents of lists.
import re					# Import re to split up the lists of symbols into individual items.
import sqlalchemy			# Import sqlalchemy to do specific data selection from the MySQL database.


# Determines what symbols in the cashtag list are traded on the selected exchange.
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
	match = numpy.isin(base_list, twitter_base_list, assume_unique=True)

	for i in range(len(base_list)):

		if (match[i] == True):

			for created_at in twitter_dict[base_list[i]]:
				match_list.append([created_at, base_list[i], base_dict[base_list[i]]])

	print('Supported symbols check complete.')

	return match_list


# Queries the exchange for market data for the time period around the Tweet each symbol in the match list.
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

			if (uohlcv_list and len(uohlcv_list) == 2):

				for uohlcv in uohlcv_list:
					print(since, uohlcv)
					candle_ts = datetime.datetime.utcfromtimestamp(uohlcv[0] // 1000)
					close_price = float(uohlcv[4])
					high_price = float(uohlcv[2])
					low_price = float(uohlcv[3])
					open_price = float(uohlcv[1])
					volume = float(uohlcv[5])
					uohlcv_dict = {'base': base, 'candle_ts': candle_ts, 'close': close_price, 'high': high_price,
								   'low': low_price, 'open': open_price, 'symbol': symbol, 'tweet_ts': created_at,
								   'volume': volume}
					market_data_list.append(uohlcv_dict)

	print('Market data collection complete.')

	return market_data_list


# Get a list of cashtags for the current screen name and turn it into a list (for direct processing) and a dictionary
# (for lookup purposes during the direct processing).
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


# Load the settings from the settings file and turn them into variables.
settings = cashtag_analyzer.load_settings()
exchange_id = settings['exchange_options']['exchange_id']
limit = settings['exchange_options']['limit']
results_table = settings['mysql_connection']['results_table']
timeframe = settings['exchange_options']['timeframe']
tweets_table = settings['mysql_connection']['tweets_table']

# Dynamically load the exchange method from the ccxt module.
exchange_method = getattr(ccxt, exchange_id)
exchange = exchange_method()

# Connect to the database.
db_connection = cashtag_analyzer.connect_to_db(settings['mysql_connection'])
table = cashtag_analyzer.get_table(db_connection, tweets_table)

# Select a list of screen names from the database.
select_query = sqlalchemy.select([table.c['screen_name']]).distinct()
results = db_connection.execute(select_query)

# Loop through the screen name list and collect market data for each cashtag.
for result in results:
	screen_name = result[0]

	print('Getting results for screen name {}...'.format(screen_name))

	twitter_base_list, twitter_dict = create_twitter_lists(screen_name, table)
	match_list = create_match_list(exchange, twitter_base_list, twitter_dict)
	market_data_list = create_market_data_list(exchange, match_list, limit=limit, timeframe=timeframe)

	# As a sanity check, get the number of rows in the table before executing the INSERT statement and print the results.
	results_text = 'Pre-INSERT row count: ' + cashtag_analyzer.get_row_count(db_connection, table)
	print(results_text)

	# Insert the market data into the database.
	cashtag_analyzer.insert_data(db_connection, market_data_list, table)
