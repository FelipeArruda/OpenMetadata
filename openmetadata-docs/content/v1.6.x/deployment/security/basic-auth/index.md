---
title: Basic Authentication
slug: /deployment/security/basic-auth
collate: false
---

# UserName/Password Login

Out of the box, OpenMetadata comes with a Username & Password Login Mechanism.

The default Username and Password for Login are:

```commandline
Username - admin@open-metadata.org
Password - admin
```
When using a custom domain, configure the principal domain as follows:

```yaml
config:
    authorizer:
      adminPrincipals: [admin]
      principalDomain: "yourdomain.com"
```

With this setup, the default Username will be `admin@yourdomain.com`.

{%important%}

Security requirements for your **production** environment:
- **DELETE** the admin default account shipped by OM.
- **UPDATE** the Private / Public keys used for the [JWT Tokens](/deployment/security/enable-jwt-tokens) in case it is enabled.

{%/important%}

# Setting up Basic Auth Manually

Below are the required steps to set up the Basic Login:

## Set up Configurations in openmetadata.yaml

### Authentication Configuration

The following configuration controls the auth mechanism for OpenMetadata. Update the mentioned fields as required.

```yaml
authenticationConfiguration:
  provider: ${AUTHENTICATION_PROVIDER:-basic}
  publicKeyUrls: ${AUTHENTICATION_PUBLIC_KEYS:-[{your domain}/api/v1/system/config/jwks]} # Update with your Domain and Make sure this "/api/v1/system/config/jwks" is always configured to enable JWT tokens
  authority: ${AUTHENTICATION_AUTHORITY:-https://accounts.google.com}
  enableSelfSignup : ${AUTHENTICATION_ENABLE_SELF_SIGNUP:-true}
```

For the Basic auth we need to set:
 
-  `provider`: basic
-  `publicKeyUrls`: {http|https}://{your_domain}:{port}}/api/v1/system/config/jwks
-  `authority`: {your_domain}
-  `enableSelfSignup`: This flag indicates if users can come and signup by themselves on the OM

### Authorizer Configuration

This configuration controls the authorizer for OpenMetadata:

```yaml
authorizerConfiguration:
  adminPrincipals: ${AUTHORIZER_ADMIN_PRINCIPALS:-[admin]}
  allowedEmailRegistrationDomains: ${AUTHORIZER_ALLOWED_REGISTRATION_DOMAIN:-["all"]}
  principalDomain: ${AUTHORIZER_PRINCIPAL_DOMAIN:-"open-metadata.org"}
```

For the Basic auth we need to set:

- `adminPrincipals`: admin usernames to bootstrap the server with, comma-separated values.
- `allowedEmailRegistrationDomains`: This controls what all domain are allowed for email registration can be your {principalDomain} as well, for example gmail.com, outlook.comm etc.
- `principalDomain`: This controls what all domain are allowed for email registration, for example gmail.com, outlook.comm etc. When `AUTHORIZER_ENFORCE_PRINCIPAL_DOMAIN` is set to `true`, only users with email addresses from the `AUTHORIZER_PRINCIPAL_DOMAIN` can log in.

{%note%}

Please note the following are the formats to bootstrap admins on server startup: `[admin1,admin2,admin3]`

This works for SMTP-enabled servers, Login Password for these are generated randomly and sent to the mail `adminName`@`principalDomain`. 

If SMTP is not enabled for OpenMetadata, please use the method below to create admin users: `[admin1, admin2, admin3]`. The default password for all admin users will be admin.

After logging into the OpenMetadata UI, admin users can change their default password by navigating to `Settings > Members > Admins`.

{%/note%}

## Metadata Ingestion

For ingesting metadata when Basic Auth is enabled, it is mandatory to configure the `ingestion-bot` account with the JWT 
configuration. To know how to enable it, you can follow the documentation of [Enable JWT Tokens](/deployment/security/enable-jwt-tokens).


### Setting up SMTP Server

Basic Authentication is successfully set. For a better login experience, we can also set up the SMTP server to allow the 
users to Reset Password, Account Status Updates, etc. as well.

```yaml
email:
  emailingEntity: ${OM_EMAIL_ENTITY:-"OpenMetadata"} -> Company Name (Optional)
  supportUrl: ${OM_SUPPORT_URL:-"https://slack.open-metadata.org"} -> SupportUrl (Optional)
  enableSmtpServer : ${AUTHORIZER_ENABLE_SMTP:-false} -> True/False
  openMetadataUrl: ${OPENMETADATA_SERVER_URL:-""} -> {http/https}://{your_domain}
  senderMail: ${OPENMETADATA_SMTP_SENDER_MAIL:-""} -> Sender's email
  serverEndpoint: ${SMTP_SERVER_ENDPOINT:-""} -> (Ex :- smtp.gmail.com)
  serverPort: ${SMTP_SERVER_PORT:-""} -> (SSL/TLS port)
  username: ${SMTP_SERVER_USERNAME:-""} -> (SMTP Server Username)
  password: ${SMTP_SERVER_PWD:-""} -> (SMTP Server Password)
  transportationStrategy: ${SMTP_SERVER_STRATEGY:-"SMTP_TLS"}
```

Following are valid value for transportation strategy:

- `SMTP`: If SMTP port is 25 use this
- `SMTPS`: If SMTP port is 465 use this
- `SMTP_TLS`: If SMTP port is 587 use this

{% partial file="/v1.6/deployment/configure-ingestion.md" /%}
