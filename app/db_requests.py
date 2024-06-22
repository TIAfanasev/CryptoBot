from sqlalchemy import update, and_

from database import sync_engine, session_factory, Base
from db_models import UsersTable


def create_tables():
    Base.metadata.drop_all(sync_engine)

    Base.metadata.create_all(sync_engine)


def check_user(u_id):
    with session_factory() as session:
        user_counter = session.query(UsersTable).where(UsersTable.id == u_id).count()
        return bool(user_counter)


def create_new_user(u_id):
    with session_factory() as session:
        user = UsersTable(id=u_id)
        session.add(user)
        session.commit()


def add_threshold(u_id, coin_id, th_type, value):
    with session_factory() as session:
        user_coin_exist = session.query(UsersTable).where(and_(UsersTable.coin_id == coin_id, UsersTable.id == u_id)).count()
        if user_coin_exist:
            if th_type:
                user = update(UsersTable).where(and_(UsersTable.coin_id == coin_id, UsersTable.id == u_id)).values(max=value)
            else:
                user = update(UsersTable).where(and_(UsersTable.coin_id == coin_id, UsersTable.id == u_id)).values(min=value)
            session.execute(user)
        else:
            if th_type:
                user = UsersTable(id=u_id, coin_id=coin_id, max=value)
            else:
                user = UsersTable(id=u_id, coin_id=coin_id, min=value)
            session.add(user)
        session.commit()


def check_min(coin_id, cur_price):
    with session_factory() as session:
        users = session.query(UsersTable.id).where(and_(UsersTable.coin_id == coin_id, UsersTable.min >= cur_price)).all()
        return users


def check_max(coin_id, cur_price):
    with session_factory() as session:
        users = session.query(UsersTable.id).where(and_(UsersTable.coin_id == coin_id, UsersTable.max <= cur_price)).all()
        return users


def reset_threshold(u_id, coin_id, th_type):
    with session_factory() as session:
        if th_type:
            user = update(UsersTable).where(and_(UsersTable.coin_id == coin_id, UsersTable.id == u_id)).values(max=None)
        else:
            user = update(UsersTable).where(and_(UsersTable.coin_id == coin_id, UsersTable.id == u_id)).values(min=None)
        session.execute(user)
        session.commit()


def main():
    create_tables()
    create_new_user(1)
    create_new_user(2)
    print(check_user(1))
    min_users = check_min(0, 0)
    add_threshold(1, True, 3)
    reset_threshold(1, True)
    max_users = check_max(0, 4)
    print([x[0] for x in min_users])
    print([x[0] for x in max_users])


#Base.metadata.drop_all(sync_engine)
# Base.metadata.create_all(sync_engine)
