---
title: Build a Python App with CockroachDB
summary: Learn how to use CockroachDB from a simple Python application with the SQLAlchemy ORM.
toc: true
twitter: false
---

<div class="filters filters-big clearfix">
    <a href="build-a-python-app-with-cockroachdb.html"><button style="width: 28%" class="filter-button">Use <strong>psycopg2</strong></button></a>
    <a href="build-a-python-app-with-cockroachdb-sqlalchemy.html"><button style="width: 28%" class="filter-button current">Use <strong>SQLAlchemy</strong></button></a>
</div>

This tutorial shows you how build a simple Python application with CockroachDB using a PostgreSQL-compatible driver or ORM.

We have tested the [Python psycopg2 driver](http://initd.org/psycopg/docs/) and the [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/latest/) enough to claim **beta-level** support, so those are featured here. If you encounter problems, please [open an issue](https://github.com/cockroachdb/cockroach/issues/new) with details to help us make progress toward full support.

{{site.data.alerts.callout_success}}
For a more realistic use of SQLAlchemy with CockroachDB, see our [`examples-orms`](https://github.com/cockroachdb/examples-orms) repository.
{{site.data.alerts.end}}

## Before you begin

{% include {{page.version.version}}/app/before-you-begin.md %}

{{site.data.alerts.callout_danger}}
**Upgrading from CockroachDB 2.0 to 2.1?** If you used SQLAlchemy with your 2.0 cluster, you must [upgrade the adapter to the latest release](https://github.com/cockroachdb/cockroachdb-python) before upgrading to CockroachDB 2.1.
{{site.data.alerts.end}}

## Step 1. Install the SQLAlchemy ORM

To install SQLAlchemy, as well as a [CockroachDB Python package](https://github.com/cockroachdb/cockroachdb-python) that accounts for some minor differences between CockroachDB and PostgreSQL, run the following command:

{% include copy-clipboard.html %}
~~~ shell
$ pip install sqlalchemy cockroachdb
~~~

For other ways to install SQLAlchemy, see the [official documentation](http://docs.sqlalchemy.org/en/latest/intro.html#installation-guide).

<section class="filter-content" markdown="1" data-scope="secure">

## Step 2. Create the `maxroach` user and `bank` database

{% include {{page.version.version}}/app/create-maxroach-user-and-bank-database.md %}

## Step 3. Generate a certificate for the `maxroach` user

Create a certificate and key for the `maxroach` user by running the following command.  The code samples will run as this user.

{% include copy-clipboard.html %}
~~~ shell
$ cockroach cert create-client maxroach --certs-dir=certs --ca-key=my-safe-directory/ca.key
~~~

## Step 3. Run the Python code

The following code uses the [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/latest/) to map Python objects and methods to SQL operations. 

Specifically, `Base.metadata.create_all(engine)` creates an `accounts` table based on the Account class, `session.add_all([Account(),...
])` inserts rows into the table, and `session.query(Account)` selects from the table so that balances can be printed.

{{site.data.alerts.callout_info}}
Use of the [`cockroachdb-python` package](https://github.com/cockroachdb/cockroachdb-python") is triggered by the `cockroachdb://` prefix in the engine URL shown below. Using `postgres://` to connect to your CockroachDB cluster will not work.
{{site.data.alerts.end}}

Copy the code or
<a href="https://raw.githubusercontent.com/cockroachdb/docs/master/_includes/v2.2/app/sqlalchemy-basic-sample.py" download>download it directly</a>.

The script below does a number of things.  At a high level, it:

1. Reads the existing account IDs.
2. Creates a number of accounts with random IDs and adds a randomly generated amount of money to each account.  (Step #1 was necessary to avoid collisions during the account creation in this step.)
3. Chooses two accounts at random from the list of accounts and takes half of the money from the first, and deposits it into the second.

It does all of the above using the recommended practices for using SQLAlchemy with the CockroachDB dialect's driver, which are (but are not limited to):

- DO use the `run_transaction` interface defined by the driver, which abstracts the details of [transaction retries](XXX) away from you having to care about them, but which are more frequent than in some other database for reasons which are described below.
- DON'T do any explicit munging of the transaction state inside the callback function passed to `run_transaction` - this includes calls to [`Session.flush`](XXX), which does not work as expected with CockroachDB because CockroachDB does not support nested transactions (subtransactions) or named savepoints, both of which are necessary for the `flush()` method to work properly.
- DO follow the recommendation of the [SQLAlchemy FAQs](https://docs.sqlalchemy.org/en/latest/orm/session_basics.html#session-frequently-asked-questions), which affirm the previous point by stating (among other things) that
> As a general rule, the application should manage the lifecycle of the session externally to functions that deal with specific data. This is a fundamental separation of concerns which keeps data-specific operations agnostic of the context in which they access and manipulate that data.
> Keep the lifecycle of the session (and usually the transaction) separate and external


{% include copy-clipboard.html %}
~~~ python
{% include {{page.version.version}}/app/sqlalchemy-basic-sample.py %}
~~~

Then run the code:

{% include copy-clipboard.html %}
~~~ shell
$ python sqlalchemy-basic-sample.py
~~~

The output should be:

~~~ shell
1 1000
2 250
~~~

To verify that the table and rows were created successfully, start the [built-in SQL client](use-the-built-in-sql-client.html):

{% include copy-clipboard.html %}
~~~ shell
$ cockroach sql --certs-dir=certs --database=bank
~~~

Then, issue the following statement:

{% include copy-clipboard.html %}
~~~ sql
> SELECT id, balance FROM accounts;
~~~

~~~
+----+---------+
| id | balance |
+----+---------+
|  1 |    1000 |
|  2 |     250 |
+----+---------+
(2 rows)
~~~

</section>

<section class="filter-content" markdown="1" data-scope="insecure">

## Step 2. Create the `maxroach` user and `bank` database

{% include {{page.version.version}}/app/insecure/create-maxroach-user-and-bank-database.md %}

## Step 3. Run the Python code

The following code uses the [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/latest/) to map Python-specific objects to SQL operations. Specifically, `Base.metadata.create_all(engine)` creates an `accounts` table based on the Account class, `session.add_all([Account(),...
])` inserts rows into the table, and `session.query(Account)` selects from the table so that balances can be printed.

{{site.data.alerts.callout_info}}
The <a href="https://github.com/cockroachdb/cockroachdb-python">cockroachdb python package</a> installed earlier is triggered by the <code>cockroachdb://</code> prefix in the engine URL. Using <code>postgres://</code> to connect to your cluster will not work.
{{site.data.alerts.end}}

Copy the code or
<a href="https://raw.githubusercontent.com/cockroachdb/docs/master/_includes/v2.2/app/insecure/sqlalchemy-basic-sample.py" download>download it directly</a>.

{% include copy-clipboard.html %}
~~~ python
{% include {{page.version.version}}/app/insecure/sqlalchemy-basic-sample.py %}
~~~

Then run the code:

{% include copy-clipboard.html %}
~~~ shell
$ python sqlalchemy-basic-sample.py
~~~

The output should be:

~~~ shell
1 1000
2 250
~~~

To verify that the table and rows were created successfully, start the [built-in SQL client](use-the-built-in-sql-client.html):

{% include copy-clipboard.html %}
~~~ shell
$ cockroach sql --insecure --database=bank
~~~

Then, issue the following statement:

{% include copy-clipboard.html %}
~~~ sql
> SELECT id, balance FROM accounts;
~~~

~~~
+----+---------+
| id | balance |
+----+---------+
|  1 |    1000 |
|  2 |     250 |
+----+---------+
(2 rows)
~~~

</section>

## What's next?

Read more about using the [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/latest/), or check out a more realistic implementation of SQLAlchemy with CockroachDB in our [`examples-orms`](https://github.com/cockroachdb/examples-orms) repository.

{% include {{page.version.version}}/app/see-also-links.md %}
