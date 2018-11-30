---
title: Overview of CockroachDB security
summary: Learn about the authentication, encryption, authorization, and audit log features for secure CockroachDB clusters.
toc: true
---

An insecure CockroachDB cluster comes with serious risks:

- Your cluster is open to any client that can access any node's IP addresses.
- Any user, even `root`, can log in without providing a password.
- Any user, connecting as `root`, can read or write any data in your cluster.
- There is no network encryption or authentication, and thus no confidentiality.

To avoid these security risks, CockroachDB provides the following authentication, authorization, encryption, and audit log features to deploy secure clusters:

Security feature | Description
-------------|------------
[Authentication](#authentication) | <ul><li>Inter-node and node identity authentication using [TLS 1.2](https://en.wikipedia.org/wiki/Transport_Layer_Security)</li><li>Client identity authentication using TLS 1.2 or username/password</li></ul>
[Authorization](#authorization) | <ul><li>Users and privileges</li><li> Role-based access control (Enterprise feature)</li></ul>
[Encryption](#encryption) | <ul><li>Encryption in flight using TLS 1.2</li><li> Encryption at rest using AES in counter mode (Enterprise feature)</li></ul>
[Audit log](#audit-logs-experimental) | `ALTER TABLE...EXPERIMENTAL AUDIT` to get detailed information about queries being executed against your system.

## Authentication

Authentication is the act of verifying the identity of the other party in a communication. In a CockroachDB cluster, the nodes communicate with each other, with SQL clients, and the Admin UI. Therefore for secure clusters, we perform the following identity checks:

- Node identity checks using TLS digital certificates.
- Client identity checks using either TLS digital certificates or passwords.

### Node identity check

CockroachDB uses TLS digital certificates for inter-node and client-node authentication, which requires the following:

- CA certificate and key
- Node certificate and key
- (Optional) UI certificate and key

You can use [`cockroach cert` commands](create-security-certificates.html) , [`openssl` commands](create-security-certificates-openssl.html), or a custom CA to generate all the keys and certificates.

### Client identity check

CockroachDB offers two methods for client identity check:

- (Recommended) Client certificate and key authentication, which is available to all users.
- Password authentication, which is available to non-root users who you've created passwords for. To create a user with a password, use the `WITH PASSWORD` clause of [`CREATE USER`](create-user.html#create-a-user-with-a-password). To add a password to an existing user, use the [`cockroach user`](create-and-manage-users.html#update-a-users-password) command.

### Authentication best practice

As a security best practice, we recommend that you rotate the node, client, or CA certificates in the following scenarios:

- The node, client, or CA certificates are expiring soon.
- Your organization's compliance policy requires periodical certificate rotation.
- The key (for a node, client, or CA) is compromised.
- You need to modify the contents of a certificate, for example, to add another DNS name or the IP address of a load balancer through which a node can be reached. In this case, you would need to rotate only the node certificates.

For details about when and how to change security certificates without restarting nodes, see [Rotate Security Certificates](rotate-certificates.html).

## Encryption

Data encryption and decryption is the process of transforming plaintext data to cipher-text and vice versa using a key or password.

### Encryption in flight

For a secure CockroachDB cluster, all inter-node and client-node network communication is encrypted using TLS 1.2. This feature is enabled by default for all secure clusters and needs no additional configuration.

### Encryption at Rest (Experimental)(Enterprise)

[Encryption at Rest](encryption.html) allows encryption of all files on disk using  [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)  in  [counter mode](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Counter_(CTR)), with all key sizes allowed.

Encryption is performed in the  [storage layer](https://www.cockroachlabs.com/docs/v2.1/architecture/storage-layer.html)  and configured per store. All files used by the store, regardless of contents, are encrypted with the desired algorithm.

To allow arbitrary rotation schedules and ensure security of the keys, the keys are split into user-provided **Store keys** and dynamically-generated **Data keys**. **Store keys** are used to encrypt the **Data keys**. **Data keys** are used to encrypt the actual data.

You can change the encryption type from plaintext to encryption, between different encryption algorithms (using various key sizes), or from encryption to plaintext.

CockroachDB does not currently force re-encryption of older files but instead relies on normal RocksDB churn to slowly rewrite all data with the desired encryption.

### Encryption at Rest best practices

Key management is the most important aspect of encryption. The following rules should be kept in mind:

- Make sure that only the UNIX user running the `cockroach` process has access to the keys.
- Do not store the keys on the same partition/drive as the CockroachDB data. It is best to load keys at run time from a separate system (e.g., [Keywhiz](https://square.github.io/keywhiz/), [Vault](https://www.hashicorp.com/products/vault)).
- Rotate store keys frequently (every few weeks to months).
- Keep the data key rotation period low (default is one week).
- Do not switch from encrypted to plaintext, this leaks data keys. When plaintext is selected, all previously encrypted data must be considered reachable.
- Do not copy the encrypted files, as the data keys are not easily available.

Additionally, if encryption is desired, start a node with it enabled from the first run, without ever running in plaintext.

## Authorization

User authorization is the act of defining access policies for authenticated CockroachDB users. CockroachDB provides two methods of user authorization:

- CockroachDB allows you to create, manage, and remove your cluster's users (which lets you control SQL-level [privileges](https://www.cockroachlabs.com/docs/stable/privileges.html)) using use the `cockroach user` [command](https://www.cockroachlabs.com/docs/stable/cockroach-commands.html) with appropriate flags.  
- If you have an [Enterprise license](get-started-with-enterprise-trial.html), you can use [role-based access management (RBAC)](https://www.cockroachlabs.com/docs/stable/roles.html) for simplified user management.

## Audit logs (Experimental)

CockroachDB's SQL audit logging gives you detailed information about queries being executed against your system, including:

- Full text of the query (which may include personally identifiable information (PII))
- Date/Time
- Client address
- Application name

This feature is especially useful when you want to log all queries that are run against a table containing personally identifiable information (PII). For more information, see [SQL Audit Logging](https://www.cockroachlabs.com/docs/v2.1/sql-audit-logging.html).

## CockroachDB security known issues

### Row-level/column-level permissioning (workaround: views and grants on views)

### Unencrypted backups

Backups taken with the `BACKUP` statement are not encrypted even if Encryption at Rest is enabled. Encryption at Rest only applies to the CockroachDB node's data on the local disk. If you want encrypted backups, you will need to encrypt your backup files using your preferred encryption method.

### Encryption for touchpoints with other services:

-  S3 backup encryption
- encrypted comms with Kafka

## See also

- [Client Connection Parameters](connection-parameters.html)
- [Manual Deployment](manual-deployment.html)
- [Orchestrated Deployment](orchestration.html)
- [Local Deployment](secure-a-cluster.html)
- [Test Deployment](deploy-a-test-cluster.html)
- [Other Cockroach Commands](cockroach-commands.html)
