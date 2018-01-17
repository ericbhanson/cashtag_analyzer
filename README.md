# cashtag_analyzer
A Python module to analyze Twitter cashtags.

Makes use of a YAML-based settings file to specify the following user-specific parameters:
- mysql_connection:
  - dbname: The name of the MySQL database where Tweet data will be stored.
  - host: The MySQL database host name.
  - password: The MySQL database password.
  - table: The name of the table where the Tweet data will be stored.
  - user: The MySQL database user name.
- screen_names: a comma-separated list of Twitter screen names the script should query for cashtags.
- twitter_api: the consumer_key, consumer_secret, access_token, and access_token_secret keys provided by Twitter at https://apps.twitter.com.
