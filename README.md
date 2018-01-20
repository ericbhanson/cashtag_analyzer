# Cashtag Analyzer
A Python module to analyze Twitter cashtags. For a given list of Twitter screen names, it will:
* Connect to the Twitter API.
* Download that screen name's Tweets.
* Extract those Tweets that contain a [cashtag](http://money.cnn.com/2012/07/31/technology/twitter-cashtag/index.htm) and store them in a database.
* Determine which cashtags are traded on a specified exchange.
* Get market data for the time period around the timestamp of the Tweet.
* Store both the Tweets and the market data in a database for further analysis.

Makes use of a YAML-based settings file (see included sample) to specify the following user-specific parameters:
* exchange_options: 
    * exchange_id: The ccxt ID of the exchange to query for market data. See the [CCXT wiki](https://github.com/ccxt/ccxt/wiki/Exchange-Markets) for a list of supported exchanges and their IDs.
    * limit: The number of candlesticks to collect from the exchange API.
    * timeframe: The size of the candles (i.e. 1 minute, 5 minutes, 1 hour, etc.). The timeframes attribute of each ccxt.exchange lists the supported timeframes for a given exchange. See the [CCXT](https://github.com/ccxt/ccxt/wiki/Manual#exchange-structure) for additional information.
    * mysql_connection:
        * dbname: The name of the MySQL database where Tweet data will be stored.
        * host: The MySQL database host name.
        * password: The MySQL database password.
        * results_table: The name of the table where market data for each cashtag will be stored.
        * tweets_table: The name of the table where the Tweet data will be stored.
        * user: The MySQL database user name.
    * screen_names: a comma-separated list of Twitter screen names the script should query for cashtags.
    * twitter_api: the consumer_key, consumer_secret, access_token, and access_token_secret keys provided by [Twitter](https://apps.twitter.com).
