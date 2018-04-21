# Identity Exchange

Exchanges a Google identity for AWS identity (credentials)

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

## Into the weeds

[IdentityExchange](identityexchange/)

## Terraform AWS Requirements

In order to exchange Google and AWS credentials there needs to be an IAM Role in the AWS account to assume.
The IAM Role's permissions will tied to the temporary AWS credentials.

The [terraform/](terraform/) directory can be used to provision an IAM Role that provides EC2 access.
