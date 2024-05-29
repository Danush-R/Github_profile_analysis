import streamlit as st
from main import handle_rate_limit, fetch_user_data, fetch_data_from_db, collection
import plotly.express as px
import pandas as pd
import requests
import matplotlib.pyplot as plt

# Replace 'your_token_here' with your actual GitHub personal access token
ACCESS_TOKEN = '__________________________'
GITHUB_API_URL = 'https://api.github.com'
HEADERS = {
    'Authorization': f'token {ACCESS_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Streamlit UI
st.title("GitHub User Data Fetcher")

username = st.text_input("Enter a GitHub username:")
data_source = st.selectbox("Choose data source:", ["GitHub API", "MongoDB"])
if st.button("Fetch Data"):
    if username:
        if data_source == "GitHub API":
            handle_rate_limit()  # Check and handle rate limits before making the API call
            user_data = fetch_user_data(username)
            if user_data:
                if 'error' in user_data:
                    st.error(user_data['error'])
                else:
                    collection.insert_one(user_data)
                    st.success("User data fetched and saved to MongoDB")
        else:
            user_data = fetch_data_from_db(username)
            if user_data:
                st.success("User data fetched from MongoDB")
            else:
                st.error("User data not found in MongoDB")

        if user_data:
            st.subheader(user_data['Login'])
            st.image(user_data['Avatar URL'], width=150)
            st.write(f"**Name:** {user_data['Name']}")
            st.write(f"**Bio:** {user_data['Bio']}")
            st.write(f"**Public Repositories:** {user_data['Public Repositories']}")
            st.write(f"**Followers Count:** {user_data['Followers Count']}")
            st.write(f"**Following Count:** {user_data['Following Count']}")
            st.write(f"**Joined:** {user_data['Created At']}")
            st.write(f"**Updated:** {user_data['Updated At']}")
            st.write(f"**View Profile :** [Link]({user_data['Profile URL']})")
            st.write(f"**Total Commits:** {user_data['Total Commits']}")
            st.write(f"**Languages:** {', '.join(user_data['Languages'])}")
            st.write(f"**Starred Repositories:** {', '.join(user_data['Starred Repositories'])}")
            st.write(f"**Subscriptions:** {', '.join(user_data['Subscriptions'])}")

            # Visualization

            # Fetch repositories
            repos_response = requests.get(f'https://api.github.com/users/{username}/repos', headers={
                'Authorization': f'token {ACCESS_TOKEN}',
                'Accept': 'application/vnd.github.v3+json'
            })
            if repos_response.status_code == 200:
                repos = repos_response.json()
                language_counts = {}
                commits_per_language = {}
                stars_per_language = {}
                stars_per_repo = {}
                commits_per_repo = {}

                for repo in repos:
                    language = repo['language']
                    if language:
                        language_counts[language] = language_counts.get(language, 0) + 1
                        stars_per_language[language] = stars_per_language.get(language, 0) + repo['stargazers_count']

                        commits_response = requests.get(repo['commits_url'].replace('{/sha}', ''), headers={
                            'Authorization': f'token {ACCESS_TOKEN}',
                            'Accept': 'application/vnd.github.v3+json'
                        })
                        if commits_response.status_code == 200:
                            commits_per_language[language] = commits_per_language.get(language, 0) + len(commits_response.json())

                        stars_per_repo[repo['name']] = repo['stargazers_count']
                        commits_per_repo[repo['name']] = len(commits_response.json())
               
                # Top 10 Languages used
                top_10_languages = sorted(language_counts.items(), key=lambda item: item[1], reverse=True)[:10]
                top_10_lang_df = pd.DataFrame(top_10_languages, columns=['Language', 'Repo Count'])
                fig = px.bar(top_10_lang_df, x='Repo Count', y='Language', orientation='h', title='Top 10 Languages Used')
                st.plotly_chart(fig)

                if language_counts:
                    lang_df = pd.DataFrame(language_counts.items(), columns=['Language', 'Repo Count'])
                    fig = px.pie(lang_df, names='Language', values='Repo Count', title='Repositories per Language')
                    st.plotly_chart(fig)

                if commits_per_language:
                    commits_lang_df = pd.DataFrame(commits_per_language.items(), columns=['Language', 'Commits'])
                    fig = px.pie(commits_lang_df, names='Language', values='Commits', title='Commits per Language')
                    st.plotly_chart(fig)

                if stars_per_language:
                    stars_lang_df = pd.DataFrame(stars_per_language.items(), columns=['Language', 'Stars'])
                    fig = px.pie(stars_lang_df, names='Language', values='Stars', title='Stars per Language')
                    st.plotly_chart(fig)

                if stars_per_repo:
                    stars_repo_df = pd.DataFrame(stars_per_repo.items(), columns=['Repository', 'Stars'])
                    fig = px.pie(stars_repo_df, names='Repository', values='Stars', title='Stars per Repository')
                    st.plotly_chart(fig)

                if commits_per_repo:
                    commits_repo_df = pd.DataFrame(commits_per_repo.items(), columns=['Repository', 'Commits'])
                    fig = px.pie(commits_repo_df, names='Repository', values='Commits', title='Commits per Repository')
                    st.plotly_chart(fig)

        else:
            st.error("Failed to fetch data.")
    else:
        st.warning("Please enter a GitHub username.")
