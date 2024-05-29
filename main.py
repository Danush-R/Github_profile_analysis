import requests
import time
from pymongo import MongoClient

# MongoDB connection string
MONGODB_CONNECTION_STRING = "___________"

# Initialize MongoDB client
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client["github"]
collection = db["users"]

# Replace 'your_token_here' with your actual GitHub personal access token
ACCESS_TOKEN = '_________________'
GITHUB_API_URL = 'https://api.github.com'
HEADERS = {
    'Authorization': f'token {ACCESS_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_rate_limit():
    """Function to get the current rate limit status."""
    response = requests.get(f'{GITHUB_API_URL}/rate_limit', headers=HEADERS)
    rate_limit = response.json()
    return rate_limit['resources']

def handle_rate_limit():
    """Function to handle the rate limit."""
    rate_limit = get_rate_limit()
    remaining_requests = rate_limit['core']['remaining']
    reset_time = rate_limit['core']['reset']

    if remaining_requests == 0:
        # Calculate the time to sleep until the rate limit resets
        sleep_time = reset_time - time.time() + 1  # Adding 1 second buffer
        print(f'Rate limit exceeded. Sleeping for {sleep_time} seconds...')
        time.sleep(sleep_time)

def fetch_user_data(username):
    """Function to fetch specific GitHub user data."""
    response = requests.get(f'{GITHUB_API_URL}/users/{username}', headers=HEADERS)
    if response.status_code == 200:
        user_data = response.json()
        user_info = {
            'Login': user_data['login'],
            'Name': user_data.get('name', ''),
            'Bio': user_data.get('bio', None),
            'Public Repositories': user_data['public_repos'],
            'Followers Count': user_data['followers'],
            'Following Count': user_data['following'],
            'Created At': user_data['created_at'],
            'Updated At': user_data['updated_at'],
            'Avatar URL': user_data['avatar_url'],
            'Profile URL': user_data['html_url']
        }
        # Fetch additional data
        user_info['Total Commits'] = fetch_total_commits(username)
        user_info['Languages'] = fetch_languages(username)
        user_info['Starred Repositories'] = fetch_starred_repositories(username)
        user_info['Subscriptions'] = fetch_subscriptions(username)
        user_info['Organizations'] = fetch_organizations(username)
        user_info['Followers List'] = fetch_followers(username)
        user_info['Following List'] = fetch_following(username)

        # Replace empty lists with 0
        for key, value in user_info.items():
            if isinstance(value, list) and not value:
                user_info[key] = 0

        return user_info
    elif response.status_code == 404:
        return {"error": "User not found"}
    else:
        return None

def fetch_total_commits(username):
    """Function to fetch total commits for a user."""
    repos_response = requests.get(f'{GITHUB_API_URL}/users/{username}/repos', headers=HEADERS)
    if repos_response.status_code == 200:
        repos = repos_response.json()
        total_commits = 0
        for repo in repos:
            commits_response = requests.get(repo['commits_url'].replace('{/sha}', ''), headers=HEADERS)
            if commits_response.status_code == 200:
                total_commits += len(commits_response.json())
        return total_commits
    return 0

def fetch_languages(username):
    """Function to fetch languages for a user."""
    repos_response = requests.get(f'{GITHUB_API_URL}/users/{username}/repos', headers=HEADERS)
    if repos_response.status_code == 200:
        repos = repos_response.json()
        languages = set()
        for repo in repos:
            languages_response = requests.get(repo['languages_url'], headers=HEADERS)
            if languages_response.status_code == 200:
                languages.update(languages_response.json().keys())
        return list(languages)
    return []

def fetch_starred_repositories(username):
    """Function to fetch starred repositories for a user."""
    response = requests.get(f'{GITHUB_API_URL}/users/{username}/starred', headers=HEADERS)
    if response.status_code == 200:
        return [repo['full_name'] for repo in response.json()]
    return []

def fetch_subscriptions(username):
    """Function to fetch subscriptions for a user."""
    response = requests.get(f'{GITHUB_API_URL}/users/{username}/subscriptions', headers=HEADERS)
    if response.status_code == 200:
        return [repo['full_name'] for repo in response.json()]
    return []

def fetch_organizations(username):
    """Function to fetch organizations for a user."""
    response = requests.get(f'{GITHUB_API_URL}/users/{username}/orgs', headers=HEADERS)
    if response.status_code == 200:
        return [org['login'] for org in response.json()]
    return []

def fetch_followers(username):
    """Function to fetch followers for a user."""
    response = requests.get(f'{GITHUB_API_URL}/users/{username}/followers', headers=HEADERS)
    if response.status_code == 200:
        return [user['login'] for user in response.json()]
    return []

def fetch_following(username):
    """Function to fetch following for a user."""
    response = requests.get(f'{GITHUB_API_URL}/users/{username}/following', headers=HEADERS)
    if response.status_code == 200:
        return [user['login'] for user in response.json()]
    return []

def fetch_data_from_db(username):
    """Function to fetch user data from MongoDB."""
    return collection.find_one({"Login": username})
