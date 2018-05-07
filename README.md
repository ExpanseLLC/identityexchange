# Identity Exchange

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

## Components

### Login with Google

The first step is getting a token for an authenticated Google user.
This is described in detail [here](https://developers.google.com/api-client-library/python/auth/installed-app).

The code for this can be seen [here](identityexchange/main.py?at=master&fileviewer=file-view-default#main.py-38)

### Token verification

Once we have a token we need to verify the token. During verification the following steps are performed:

1. API call to Google is made to decode token and ensure the token is still valid
2. The token issuer (client id) matches the expected value (from client_credentials.json)
3. The user's email address is extracted from the decoded token

The code for this can be seen [here](identityexchange/main.py?at=master&fileviewer=file-view-default#main.py-12)

### Login to AWS

At this point we have authenticated and ensured our Google credentials are valid.
Now we need to exchange our Google credentials for a set of AWS credentials.
This is done with the AWS [Secure Token Service](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithWebIdentity.html).

The code for this can be seen [here](identityexchange/main.py?at=master&fileviewer=file-view-default#main.py-60)

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
