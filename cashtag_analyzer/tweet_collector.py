## MODULES ##
import cashtag_analyzer	# Import the modules from the __init__ script.
import re				# Import re to do regex operations on tweets.
import tweepy			# Tweepy is the Python wrapper for Twitter's API.


## FUNCTIONS ##
# Connect to the Twitter API using the authorization information provided in the settings file.
def connect_to_twitter(twitter_settings):
	access_token = twitter_settings['access_token']
	access_token_secret = twitter_settings['access_token_secret']
	consumer_key = twitter_settings['consumer_key']
	consumer_secret = twitter_settings['consumer_secret']
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

	return api


# Get the timeline for each user in the screen name list and examine their Tweets for cashtags using the re module.
# Assemble information about those cashtagged Tweets in a list for storage in a database.
def get_cashtag_tweets(screen_names, twitter_api):
	cashtag_tweets_list = []

	for name in screen_names:
		timeline = tweepy.Cursor(twitter_api.user_timeline, screen_name=name, include_rts=False).items()

		for status in timeline:
			tweet_text = status.text
			regex_result = re.findall('\$([A-Z]+)', tweet_text)

			if regex_result:
				created_at = status.created_at
				cashtags = ', '.join(regex_result)
				screen_name = status.user.screen_name
				tweet_id = status.id
				cashtag_tweets_dict = {'cashtags': cashtags, 'created_at': created_at,
									   'screen_name': screen_name, 'tweet_id': tweet_id, 'tweet_text': tweet_text}
				cashtag_tweets_list.append(cashtag_tweets_dict)

				print(cashtag_tweets_dict)

	return cashtag_tweets_list


## MAIN CODE BODY ##
# Load the settings from the settings file.
settings = cashtag_analyzer.load_settings(
	'/Users/eric/Google Drive/Digital Currency Product/Settings Files/Careless Cashtag/')

# Connect to the database.
db_connection = cashtag_analyzer.connect_to_db(settings['mysql_connection'])

# Connect to Twitter's API.
twitter_api = connect_to_twitter(settings['twitter_api'])

# Load the list of screen names to examined from the settings file.
screen_names = settings['screen_names']

# Get the list of cashtagged Tweets and store them in a list.
cashtag_tweets_list = get_cashtag_tweets(screen_names, twitter_api)

# Insert the contents of the cashtag Tweets list into the MySQL table.
table_name = settings['mysql_connection']['table']
cashtag_tweets_table = cashtag_analyzer.get_table(db_connection, table_name)
insert_query = cashtag_tweets_table.insert(cashtag_tweets_list)
db_connection.execute(insert_query)

# Do a SELECT * on the table name to get a count of the number of rows that were inserted.
select_query = cashtag_tweets_table.select()
results = db_connection.execute(select_query)
results_text = '{} row(s) were successfully inserted into the MySQL database.'.format(len(results.fetchall()))
print(results_text)