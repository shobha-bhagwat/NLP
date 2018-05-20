import oauth2
import config
import urllib.parse as urlparse


# Create a consumer using CONSUMER_KEY and CONSUMER_SECRET to identify our app uniquely

consumer = oauth2.Consumer(config.CONSUMER_KEY, config.CONSUMER_SECRET)


def get_request_token():
    client = oauth2.Client(consumer)

    # Check whether a response is returned
    response, content = client.request(config.REQUEST_TOKEN_URL, 'POST')
    if response.status != 200:
        print("An error occurred while connecting")

    # Parse the response to get the request_token
    return dict(urlparse.parse_qsl(content.decode('utf-8')))


def get_oauth_verifier(request_token):
    # Ask user to authorize our app and give us the pin code
    print("Go to the following site in the browser: ")
    print(get_oauth_verifier_url(request_token))

    return input("What is the PIN? ")


def get_oauth_verifier_url(request_token):
    return "{}?oauth_token={}".format(config.AUTHORIZATION_URL, request_token['oauth_token'])


def get_access_token(request_token, oauth_verifier):
    # Create a token object which contains the request token and the verifier
    token = oauth2.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)

    # Create a client with our consumer (app) and the newly verified token
    client = oauth2.Client(consumer, token)

    # Ask Twitter for an access token
    response, content = client.request(config.ACCESS_TOKEN_URL, 'POST')
    return dict(urlparse.parse_qsl(content.decode('utf-8')))