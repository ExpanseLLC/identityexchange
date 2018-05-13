# Identity Exchange

[![Build Status](https://travis-ci.org/ExpanseLLC/identityexchange.svg?branch=master)](https://travis-ci.org/ExpanseLLC/identityexchange)

IdentityExchange authenticates a user via a Google identity then creates temporary AWS credentials
for each configured profile.

## Development Setup

Make handles the environment setup and commands.

### Initialize environment

```bash
make init
```

### Running tests

```bash
make test
```

### Cleaning environment

```bash
make clean
```

## Running the exchange

### First time

The first time you run `identityexchange` you will be walked through the setup process.
After the setup process, the `identityexchange` will open a browser tab where you will
login with your Google account.

After log in your browser will show `The authentication flow has completed.` and your terminal
will show `Authentication successful.`

This completes the setup and first login.

### Subsequent times

After the first login with Google, a Google token is cached on your filesystem in the below
location. Each execution of `identityexchange` after the first will no longer require a browser.

The cached Google token will be refreshed and exchanged for AWS credentials.

```bash
~/.config/identityexchange/credentials.json
```

Each time `identityexchange` is invoked the contents of `~/.aws/credentials` is rewritten.
All configured profiles will have their credentials regenerated.

## Configuration

Before you can use the `identityexchange` you will need to create a set of OAuth2 Google credentials.
These credentials are configured [here](https://bitbucket.org/expansellc/identityexchange/src/4c9e9ad78bc1923e90b3be8c817af196f53ec30d/identityexchange/config.py#lines-45)

1. Update the client identifier
2. Update the project identifier
3. Update the client secret

The first time you run `identityexchange` you will be walked through the setup process.
When the setup process is completed you will have a couple of new files on your filesystem.

```bash
$ identityexchange
Enter Google domain (only users from this domain will be allowed): gsuite-domain.com
Let's configure your first AWS Profile...
Enter the profile name: admin
Enter AWS account identifier: 1234567890101
Enter AWS role name: admin-role
```

Resulting configuration after walking through the setup process.

```yaml
# ~/.config/identityexchange/application.yaml

aws:
  duration: 3600
  profiles:
  - name: admin
    role: arn:aws:iam::1234567890101:role/admin-role
google:
  credentials_file: /Users/ryanscott/.config/identityexchange/google_credentials.json
  domain: gsuite-domain.com
```

Adding additional AWS accounts or IAM Role is done through adding additional profiles to the
list in the configuration file.

```yaml
aws:
  duration: 3600
  profiles:
  - name: admin
    role: arn:aws:iam::1234567890101:role/admin-role
  - name: new-profile
    role: arn:aws:iam::098765432111:role/new-role
```

## Components

### Login with Google

The first step is getting a token for an authenticated Google user.
This is described in detail [here](https://developers.google.com/api-client-library/python/auth/installed-app).

### Token verification

Once we have a token we need to verify the token. During verification the following steps are performed:

1. API call to Google is made to decode token and ensure the token is still valid
2. The token issuer matches the expected value (must have been issued by Google)
3. If configured to restrict to a GSuite domain, the domain is checked as well
4. The user's email address is extracted from the decoded token

The code for this can be seen [here](identityexchange/main.py?at=master&fileviewer=file-view-default#main.py-12)

### Login to AWS

At this point we have authenticated and ensured our Google credentials are valid.
Now we need to exchange our Google credentials for a set of AWS credentials.
This is done with the AWS [Secure Token Service](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithWebIdentity.html).

In order to exchange Google -> AWS credentials you will need an IAM Role that the user will be assuming.
This Role defines what permissions the user will have with their AWS credentials.

#### Role Assume Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "accounts.google.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "accounts.google.com:aud": "{google-app-client-id}"
        }
      }
    }
  ]
}
```

#### Role Policies

The Role should also have either a managed policy or custom policy attached that describes what permissions the user will have in AWS.
An example of this would be:

```
# Managed Policy
arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Custom Policy
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:Get*",
        "s3:List*"
      ],
      "Resource": "*"
    }
  ]
}
```

## Terraform AWS Requirements

In order to exchange Google and AWS credentials there needs to be an IAM Role in the AWS account to assume.
The IAM Role's permissions will tied to the temporary AWS credentials.

The [terraform/](terraform/) directory can be used to provision an IAM Role that provides EC2 access.
