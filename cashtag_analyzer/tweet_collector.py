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
settings = cashtag_analyzer.load_settings()

# Connect to the database.
db_connection = cashtag_analyzer.connect_to_db(settings['mysql_connection'])

# Connect to Twitter's API.
twitter_api = connect_to_twitter(settings['twitter_api'])

# Load the list of screen names to examined from the settings file.
screen_names = settings['screen_names']

# Get the list of cashtagged Tweets and store them in a list.
cashtag_tweets_list = get_cashtag_tweets(screen_names, twitter_api)

# As a sanity check, get the number of rows in the table before executing the INSERT statement and print the results.
results_text = 'Pre-INSERT row count: ' + cashtag_analyzer.get_row_count(db_connection, table)
print(results_text)

# Insert the list of cashtagged Tweets into the database.
cashtag_analyzer.insert_data(db_connection, cashtag_tweets_list, table)