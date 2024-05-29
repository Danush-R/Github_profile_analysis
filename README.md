# Github_profile_analysis

# GitHub User Data Fetcher

This README provides an overview of a Python script that fetches detailed information about GitHub users using the GitHub API and stores the data in a MongoDB database.

## Overview

The script utilizes the GitHub API to retrieve various details about GitHub users, including their profile information, repositories, commits, programming languages used, starred repositories, subscriptions, organizations, followers, and following.

## Features

- Fetches detailed user data from GitHub.
- Handles GitHub API rate limits gracefully.
- Stores user data in a MongoDB database for future reference.

## Usage

1. **Setup MongoDB**: Ensure you have MongoDB installed or access to a MongoDB Atlas cluster. Replace the MongoDB connection string in the script with your own connection details.

2. **Generate GitHub Personal Access Token**: Create a GitHub Personal Access Token with the required permissions. Replace 'your_token_here' in the script with your actual token.

3. **Install Dependencies**: Install the required Python packages using pip:
    ```
    pip install requests pymongo
    ```
