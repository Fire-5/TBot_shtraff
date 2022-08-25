#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Как запускать тест: из командной строки проекта, из корневого каталога,
командой `pytest`.
"""

import os
import io
import atexit
import unittest

import pytest
import sqlalchemy as sa
import sqlalchemy.exc

import data

from data import User, Project, Task

DB_FILENAME = "db_test_111.sqlite"
KEEP_TEST_DB_FILE_ON_EXIT = True
PRINT_ON_EXIT = []


def _print(*msg, **kwargs):
    string_file = io.StringIO()
    print(*msg, **kwargs, file=string_file)
    PRINT_ON_EXIT.append(string_file.getvalue())


def print_info():
    print(*PRINT_ON_EXIT)


atexit.register(print_info)


class Test01BasicSqlAlchemy(unittest.TestCase):
    """
    Demonstrates the basic DB operations (create DB, insert and read records).
    """

    @classmethod
    def setUpClass(cls) -> None:
        if os.path.exists(DB_FILENAME):
            os.remove(DB_FILENAME)

        data.db_session.global_init(DB_FILENAME)

        session = data.db_session.create_session()
        session.add(data.User(username="Dmitry", tg_id=1, chat_id=1))
        session.add(data.User(username="Eugin", tg_id=2, chat_id=2))
        session.commit()
        session.close()

        # Use `help` on sqlalchemy objects!
        #   https://stackoverflow.com/a/6226404/774971
        # help(sa.orm.relationship)
        # help(sa.ForeignKey)

    @classmethod
    def tearDownClass(cls) -> None:
        data.db_session.global_shutdown()

        if not KEEP_TEST_DB_FILE_ON_EXIT and os.path.exists(DB_FILENAME):
            os.remove(DB_FILENAME)

    def test_1_session_smoke_test(self):
        session = data.db_session.create_session()
        session.add(data.User(username="Yuri", tg_id=3, chat_id=3))
        session.commit()
        session.close()

    def test_2_user_reading(self):
        session = data.db_session.create_session()
        user1 = session.query(data.User).get(1)
        self.assertEqual(user1.username, "Dmitry")
        user1 = session.query(data.User).get(3)
        self.assertEqual(user1.username, "Yuri")
        session.close()

    def test_3_username_is_unique(self):
        session = data.db_session.create_session()
        session.add(data.User(username="Petr", tg_id=4, chat_id=4))
        session.commit()
        with self.assertRaises(sa.exc.IntegrityError):
            session.add(data.User(username="Petr", tg_id=4, chat_id=4))
            session.commit()

        session.close()


class Test02ProjectUserManyToManyReference(unittest.TestCase):
    """
    Demonstrates the basic DB operations (create DB, insert and read records).
    """

    @classmethod
    def setUpClass(cls) -> None:
        if os.path.exists(DB_FILENAME):
            os.remove(DB_FILENAME)

        data.db_session.global_init(DB_FILENAME)

        # Use `help` on sqlalchemy objects!
        #   https://stackoverflow.com/a/6226404/774971
        # help(sa.orm.relationship)
        # help(sa.ForeignKey)

    @classmethod
    def tearDownClass(cls) -> None:
        data.db_session.global_shutdown()

        if not KEEP_TEST_DB_FILE_ON_EXIT and os.path.exists(DB_FILENAME):
            os.remove(DB_FILENAME)

    def test_1_create_users(self):
        session = data.db_session.create_session()
        session.add(data.User(username="Yuri", tg_id=1, chat_id=1))
        session.add(data.User(username="Alex", tg_id=2, chat_id=2))
        session.add(data.User(username="Roman", tg_id=3, chat_id=3))
        session.add(data.User(username="Dima", tg_id=4, chat_id=4))
        session.commit()
        session.close()

    def test_2_create_projects(self):
        session = data.db_session.create_session()
        session.add(data.Project(title="Neuromarketing"))
        session.add(data.Project(title="Chemodan"))
        session.add(data.Project(title="Bot"))
        session.commit()
        session.close()

    @pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SAWarning')
    def test_3_add_users_to_projects(self):
        session = data.db_session.create_session()

        def find_user(name):
            return session.query(User).filter(User.username == name).one()

        dima = find_user("Dima")
        sasha = find_user("Alex")
        yura = find_user("Yuri")
        roma = find_user("Roman")

        def find_project(name):
            return session.query(Project).filter(Project.title == name).one()

        chemodan = find_project("Chemodan")
        nm = find_project("Neuromarketing")
        bot = find_project("Bot")

        dima.add_to_project(bot)
        dima.add_to_project(nm)
        dima.add_to_project(chemodan)
        session.commit()

        def users(project):
            return [a.user for a in project.users]

        self.assertEqual(len(chemodan.users), 1)
        self.assertEqual(chemodan.users[0].user.username, "Dima")
        self.assertIn(dima, users(nm), "Dima должен быть в этом проекте")
        self.assertIn(dima, users(bot), "Dima должен быть в этом проекте")
        self.assertIn(dima, users(chemodan), "Dima должен быть в этом проекте")

        # Не могу добавить связь, потому что я уже в этом проекте.
        with self.assertRaises(sa.exc.IntegrityError):
            # при тестировании будет warning, это нормально
            nm.add_user(dima)
            session.commit()
        # Попытка добавить меня второй раз выбросила исключение => надо
        # откатиться, иначе сессия не даст работать с БД.
        session.rollback()

        nm.add_user(roma)
        nm.add_user(yura)
        session.commit()

        # ... она видна и со стороны пользователя, причём мгновенно (объекты
        # всегда содержат актуальную информацию после `session.commit()`).
        def projects(user):
            return [a.project for a in user.projects]

        self.assertIn(nm, projects(dima), "Dima должен быть в проекте nm")
        self.assertIn(nm, projects(roma), "Roma должен быть в проекте nm")
        self.assertIn(nm, projects(yura), "Yura должен быть в проекте nm")

        session.close()

    def test_4_delete_users_from_projects(self):
        session = data.db_session.create_session()

        def find_user(name):
            return session.query(User).filter(User.username == name).one()

        def find_project(name):
            return session.query(Project).filter(Project.title == name).one()

        sasha = find_user("Alex")

        def user_to_project(user, project):
            a = data.project.Association(nick=user.username)
            a.user = user
            a.project = project
            project.users.append(a)

        # Саша в проекте
        def users(project):
            return [a.user for a in project.users]

        def projects(user):
            return [a.project for a in user.projects]

        def add_sasha_to_project(nm):
            user_to_project(sasha, nm)
            session.commit()
            self.assertIn(sasha, users(nm), "Саша должен быть в этом проекте")
            self.assertIn(nm, projects(sasha), "Саша должен быть в этом проекте")

        def sasha_dropped_nicely(nm):
            self.assertNotIn(nm, users(nm), "Саша должен дропнуть проект nm")
            self.assertNotIn(sasha, projects(sasha), "Саша должен дропнуть проект nm")

        nm = find_project("Neuromarketing")
        add_sasha_to_project(nm)

        # Старое удаление просто выкидывало из коллекции проект/юзер с другой
        # стороны связи, и связь исчезала.
        # nm.users.remove(sasha)
        #
        # В Обсидиане есть все доки, ссылки просто до кучи:
        # https://docs.sqlalchemy.org/en/14/orm/cascades.html
        # https://docs.sqlalchemy.org/en/14/orm/cascades.html#using-foreign-key-on-delete-with-many-to-many-relationships
        # https://qastack.ru/programming/5033547/sqlalchemy-cascade-delete

        # Удаление №1, через метод.
        nm.remove_user(session, sasha)
        session.commit()
        sasha_dropped_nicely(nm)

        # Удаление №2, прямое удаление связи.
        add_sasha_to_project(nm)
        a = next(filter(lambda a: a.user == sasha and a.project == nm, nm.users))
        # TODO: Это лишнее, я уже по проекту всё отфильтровал ^^^
        session.delete(a)
        sasha_dropped_nicely(nm)

        # Удаление №3, удаление благодаря каскадным удалениям.
        add_sasha_to_project(nm)
        nm.users.remove(a)
        session.commit()
        sasha_dropped_nicely(nm)

        self.assertNotIn(nm, users(nm), "Саша должен дропнуть проект nm")
        self.assertNotIn(sasha, projects(sasha), "Саша должен дропнуть проект nm")

        session.close()


class Test03TaskUser(unittest.TestCase):
    """
    User->Task one to many ORM test.
    """

    @classmethod
    def setUpClass(cls) -> None:
        if os.path.exists(DB_FILENAME):
            os.remove(DB_FILENAME)

        data.db_session.global_init(DB_FILENAME)

    @classmethod
    def tearDownClass(cls) -> None:
        data.db_session.global_shutdown()

        if not KEEP_TEST_DB_FILE_ON_EXIT and os.path.exists(DB_FILENAME):
            os.remove(DB_FILENAME)

    def test_1_create_users(self):
        session = data.db_session.create_session()
        session.add(data.User(username="Alex", tg_id=1, chat_id=1))
        session.add(data.User(username="Yuri", tg_id=2, chat_id=2))
        session.add(data.User(username="Dima", tg_id=3, chat_id=3))
        session.add(data.User(username="Roman", tg_id=4, chat_id=4))
        session.commit()
        session.close()

    def test_2_create_task(self):
        session = data.db_session.create_session()

        task = data.Task(title="test_task")
        user = session.query(User).get(1)
        user.author.append(task)
        session.commit()
        session.close()

    def test_3_assign_task(self):
        session = data.db_session.create_session()

        task = session.query(Task).filter(Task.title == "test_task").one()
        user = session.query(User).get(1)

        self.assertEqual(task.worker, None)
        self.assertEqual(task.author, user)

        task.worker = user
        session.commit()
        session.close()

    def test_4_check_worker(self):
        session = data.db_session.create_session()

        task = session.query(Task).filter(Task.title == "test_task").one()
        user = session.query(User).get(1)

        self.assertEqual(task.worker, user)
        self.assertEqual(task.author, user)

        session.commit()
        session.close()

# TODO: enforce `SQLite foreign key constraint`; below it is shown that
#       I don't have it now (I can add the orphan easily).
#       Ref [ https://www.sqlitetutorial.net/sqlite-foreign-key/ ].
# Вроде как это решается так [https://stackoverflow.com/a/67228228/774971]:
# from sqlalchemy import event
# event.listen(engine, 'connect', lambda c, _: c.execute('pragma foreign_keys=on'))

