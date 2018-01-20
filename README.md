# Cashtag Analyzer
A Python module to analyze Twitter cashtags.

Makes use of a YAML-based settings file to specify the following user-specific parameters:
- exchange_options: 
 - exchange_id: The ccxt ID of the exchange to query for market data. See https://github.com/ccxt/ccxt/wiki/Exchange-Markets for a list of supported exchanges and their IDs.
 - limit: The number of candlesticks to collect from the exchange API.
 - timeframe: The size of the candles (i.e. 1 minute, 5 minutes, 1 hour, etc.). The timeframes attribute of each ccxt.exchange lists the supported timeframes for a given exchange. See https://github.com/ccxt/ccxt/wiki/Manual#exchange-structure for additional information.
- mysql_connection:
  - dbname: The name of the MySQL database where Tweet data will be stored.
  - host: The MySQL database host name.
  - password: The MySQL database password.
  - table: The name of the table where the Tweet data will be stored.
  - user: The MySQL database user name.
- screen_names: a comma-separated list of Twitter screen names the script should query for cashtags.
- twitter_api: the consumer_key, consumer_secret, access_token, and access_token_secret keys provided by Twitter at https://apps.twitter.com.
