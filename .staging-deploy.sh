#!/usr/bin/env bash
# Install AWS CLI
pip install awsebcli --upgrade --ignore-installed
# Prepare deployment
mkdir ~/.aws/
touch ~/.aws/credentials
printf "[eb-cli]\naws_access_key_id = %s\naws_secret_access_key = %s\n" "$AWS_ACCESS_KEY_ID" "$AWS_SECRET_ACCESS_KEY" >> ~/.aws/credentials
touch ~/.aws/config
printf "[profile eb-cli]\nregion=us-east-1\noutput=json" >> ~/.aws/config