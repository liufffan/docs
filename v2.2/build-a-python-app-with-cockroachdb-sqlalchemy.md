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

The code below uses the [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/latest/) to map Python objects and methods to SQL operations.  Specifically, it:

1. Read in existing account IDs (if any) from the "bank" database.
2. Create additional accounts with randomly generated IDs.  Then, add a randomly generated amount of money to each new account.
3. Choose two accounts at random from the list of accounts and take half of the money from the first and deposit it into the second.

You can run this script as many times as you want; on each run, it will create some new accounts and shuffle some money around between accounts.  (This is why Step 1 needs to check for existing account IDs to avoid collisions.)

It does all of the above using the recommended practices for using SQLAlchemy with the CockroachDB dialect, which are listed below:

- **DO** use the [`cockroachdb.sqlalchemy.run_transaction`](https://github.com/cockroachdb/cockroachdb-python/blob/master/cockroachdb/sqlalchemy/transaction.py) method defined by the dialect, which abstracts the details of [transaction retries](transactions.html#transaction-retries) away from you having to care about them (too much). Note that there are more frequent retries in CockroachDB than in databases that do not offer the ANSI [SERIALIZABLE](XXX) isolation level.  This is because XXX

- **DO** follow the recommendation of the [SQLAlchemy FAQs](https://docs.sqlalchemy.org/en/latest/orm/session_basics.html#session-frequently-asked-questions), which affirm the previous point by stating (among other things) that
    > As a general rule, the application should manage the lifecycle of the session externally to functions that deal with specific data. This is a fundamental separation of concerns which keeps data-specific operations agnostic of the context in which they access and manipulate that data ... keep the lifecycle of the session (and usually the transaction) separate and external

- **DON'T** do any explicit munging of the transaction state inside the callback function passed to `run_transaction`

- **DON'T** make calls to [`Session.flush()`][session.flush] inside `run_transaction`.  This does not work as expected with CockroachDB because CockroachDB does not support nested transactions (subtransactions) or named savepoints (see [known limitations](known-limitations.html)), both of which are necessary for `Session.flush()` to work properly.  If `Session.flush()` encounters an error and aborts, it will try to rollback, which will not be allowed by CockroachDB and result in an error message that looks like the following:

    ~~~
    sqlalchemy.orm.exc.DetachedInstanceError: Instance <FooModel at 0x12345678> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: http://sqlalche.me/e/bhk3)
    ~~~

- **DO** prefer to use the query-builder side of SQLAlchemy over the Session/ORM side if at all possible.  There is a lot of hairy magic in Sessions that will make debugging your interactions with CockroachDB harder than if you build queries and pass them to [`Engine.execute()`](XXX), for example.  Of course, this may not be possible, in which case your application code should work as expected provided you follow the guidance given here.  This will provide the added benefit of keeping your application code portable across different databases.  For example, the sample code given on this page works identically when run against Postgres.

- XXX something something txn too large errors

{{site.data.alerts.callout_info}}
Use the `cockroachdb://` prefix in the URL passed to [`sqlalchemy.create_engine()`](XXX) to cause the [`cockroachdb-python` dialect](https://github.com/cockroachdb/cockroachdb-python") to be used. Using the `postgres://` URL prefix to connect to your CockroachDB cluster will not work.
{{site.data.alerts.end}}

Copy the code from below or
<a href="https://raw.githubusercontent.com/cockroachdb/docs/master/_includes/v2.2/app/sqlalchemy-basic-sample.py">download it directly</a>.

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

<!-- Reference Links -->

[session.flush]: https://docs.sqlalchemy.org/en/latest/orm/session_api.html#sqlalchemy.orm.session.Session.flush
