import random
from math import floor
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from cockroachdb.sqlalchemy import run_transaction

Base = declarative_base()

VERBOSE = False  # Set to True for printed summaries of account balances


# The Account class corresponds to the "accounts" database table.
class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    balance = Column(Integer)


# Create an engine to communicate with the database. The
# "cockroachdb://" prefix for the engine URL indicates that we are
# connecting to CockroachDB using the 'cockroachdb-python' dialect.
# For more information, see
# https://github.com/cockroachdb/cockroachdb-python.

engine = create_engine(
    'cockroachdb://maxroach@localhost:26257/bank',
    connect_args={
        'sslmode': 'require',
        'sslrootcert': 'certs/ca.crt',
        'sslkey': 'certs/client.maxroach.key',
        'sslcert': 'certs/client.maxroach.crt',
    },
    echo=True                   # Set to True to log SQL queries to stdout
)

Sessionmaker = sessionmaker(bind=engine)

# Automatically create the "accounts" table based on the Account class.
Base.metadata.create_all(engine)

# Insert rows into the "accounts" table.  The code below makes
# sure this script (1) checks the DB for existing IDs, and (2)
# generates random IDs for new accounts, while ensuring the new IDs
# don't collide with any existing ones.

session = Sessionmaker()

seen = {}

# Get and store existing account IDs for later collision checks during
# random account ID creation.

res = engine.execute('SELECT id from accounts;')
for elem in res:
    val = elem[0]
    if val not in seen:
        seen[val] = 1

# Create new accounts with random IDs and random account balances.

new_accounts = []
elems = iter(range(100))
for i in elems:
    maybe_id = floor(random.random()*1_000_000)
    if maybe_id not in seen:
        new_accounts.append(
            Account(
                id=maybe_id,
                balance=floor(random.random()*1_000_000)
            )
        )
        seen[maybe_id] = 1
    else:
        # Skip account IDs that already exist.
        next(elems)

session.add_all(new_accounts)
session.commit()


# Helper for getting random value from the seen hash
def get_random_account_id():
    # https://www.pythoncentral.io/select-random-item-list-tuple-data-structure-python/
    return random.choice(list(seen.keys()))


# The following functions are the transaction(s) we may want to run
# using `run_transaction`.

def transfer_funds(session, frm, to, amount):
    """Transfer AMOUNT funds between accounts FRM and TO (during SESSION).

    TODO: Consider updating this to accept account objects as args
    since we're doing duplicate work when called by
    TRANSFER_FUNDS_RANDOMLY.
    """
    source = session.query(Account).filter_by(id=frm).one()
    sink = session.query(Account).filter_by(id=to).one()

    if source.balance < amount:
        raise "Insufficient funds"

    source.balance -= amount
    session.query(Account).filter_by(id=to).update(
        {"balance": (Account.balance + amount)}
    )
    if VERBOSE:
        print("Balance after:  id {} => ${}, id {} => ${}"
              .format(source.id, source.balance, sink.id, sink.balance))


def transfer_funds_randomly(session):
    """Transfer money randomly between accounts (during SESSION).

    Just for fun, cut a randomly selected account's balance in half,
    and give that half to some other randomly selected account.
    """
    frm_id = get_random_account_id()
    to_id = get_random_account_id()
    if VERBOSE:
        print("from => {}, to => {}".format(frm_id, to_id))
    frm_acc = session.query(Account).filter_by(id=frm_id).one()
    to_acc = session.query(Account).filter_by(id=to_id).one()
    amt_to_transfer = floor(frm_acc.balance/2)
    if VERBOSE:
        print("Balance before: id {} => ${}, id {} => ${}"
              .format(frm_id, frm_acc.balance, to_id, to_acc.balance))
    transfer_funds(session, frm_id, to_id, amt_to_transfer)


# Transfer funds (randomly) between accounts.

# Note: the CockroachDB dialect's driver *must* be passed a
# sessionmaker object (instead of a session, like most other dialects)
# to ensure that a new session is created for each transaction.  This
# is necessary because, in order to support the ANSI isolation level
# SERIALIZABLE, CockroachDB needs to retry transactions more often
# than other databases that default to less safe isolation levels.
# Note that this need for additional transaction retries is a
# characteristic of SERIALIZABLE isolation and not specific to
# CockroachDB's implementation -- it's inherent in the model, since
# SERIALIZABLE implies that transactions will be "pushed" more often
# to ensure correct ordering, and will thus need to be retried more
# often by clients.

# Note: don't use
# [Session.flush()](https://docs.sqlalchemy.org/en/latest/orm/session_api.html#sqlalchemy.orm.session.Session.flush)
# inside CockroachDB transactions!  Even though `flush()` is not
# technically considered a "session lifecycle method", it relies on
# the underlying database supporting nested transactions.  if the call
# to `flush()` fails,
# you will likely get an error like the following:

# sqlalchemy.exc.NotSupportedError: (psycopg2.NotSupportedError) SAVEPOINT not supported except for COCKROACH_RESTART
#  [SQL: 'ROLLBACK TO SAVEPOINT sa_savepoint_1'] (Background on this error at: http://sqlalche.me/e/tw8g)

# This happens because CockroachDB does not have support for nested
# transactions (a.k.a. subtransactions), nor renaming savepoints (only
# the one is supported), so if the call to `flush()` fails and you are
# working with objects which are also using the same Session (xxx: use
# full name) object to store their state, you may see an error like:

# sqlalchemy.orm.exc.DetachedInstanceError: Instance <FooObjectModel at 0x7f49c5a0c0b8> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: http://sqlalche.me/e/bhk3)```

run_transaction(Sessionmaker, transfer_funds_randomly)

# Print out the balances.
if VERBOSE:
    for account in session.query(Account):
        print(account.id, account.balance)



from __future__ import print_function
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# The Account class corresponds to the "accounts" database table.
class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    balance = Column(Integer)

# Create an engine to communicate with the database. The "cockroachdb://" prefix
# for the engine URL indicates that we are connecting to CockroachDB.
engine = create_engine('cockroachdb://maxroach@localhost:26257/bank',
                       connect_args = {
                           'sslmode' : 'require',
                           'sslrootcert': 'certs/ca.crt',
                           'sslkey':'certs/client.maxroach.key',
                           'sslcert':'certs/client.maxroach.crt'
                       })
Session = sessionmaker(bind=engine)

# Automatically create the "accounts" table based on the Account class.
Base.metadata.create_all(engine)

# Insert two rows into the "accounts" table.
session = Session()
session.add_all([
    Account(id=1, balance=1000),
    Account(id=2, balance=250),
])
session.commit()

# Print out the balances.
for account in session.query(Account):
    print(account.id, account.balance)
