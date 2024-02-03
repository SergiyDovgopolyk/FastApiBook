import unittest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Contact, User
from src.repository.address_book import (
    create_contact,
    get_contacts,
    get_contact,
    update_contact,
    delete_contact
)
from src.schemas.contact import ContactSchema


class TestAddressBook(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(
            id=1,
            username="test_user",
            avatar="test_avatar",
            refresh_token="test_refresh_token",
            is_verified=True
        )
        self.session = AsyncMock(spec=AsyncSession)

    def tearDown(self):
        self.user = None
        self.session = None

    async def test_create_contact(self):
        body = ContactSchema(
            name="Test",
            surname="User",
            email="aaaaa@aaa.com",
            number="1234567890",
            birthday="1990-01-01",
            description="test"
        )
        result = await create_contact(body, self.session, self.user)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.number, body.number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.description, body.description)
        self.assertEqual(result.user, self.user)
        self.session.add.assert_called_once_with(result)
        self.session.commit.assert_called_once()

    async def test_get_contacts(self):
        birthdays = False
        contacts = [
            Contact(id=1, name="Test1", surname="User1", email="aaaaa1@aaa.com", number="12345678",
                    birthday="1990-01-01", description="test1", user=self.user),
            Contact(id=2, name="Test2", surname="User2", email="aaaaa2@aaa.com", number="12345678",
                    birthday="1990-01-01", description="test2", user=self.user),
            Contact(id=3, name="Test3", surname="User3", email="aaaaa3@aaa.com", number="12345678",
                    birthday="1990-01-01", description="test3", user=self.user),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(None, None, None, birthdays, 10, 0, self.session, self.user)
        self.assertEqual(result, contacts)

        # Test search by name
        result = await get_contacts("Test1", None, None, birthdays, 10, 0, self.session, self.user)
        expected_result = [contacts[0]]
        self.assertEqual([result[0]], expected_result)

        # Test search by surname
        result = await get_contacts(None, "User2", None, birthdays, 10, 0, self.session, self.user)
        expected_result = [contacts[1]]
        self.assertEqual([result[1]], expected_result)

        # Test search by email
        result = await get_contacts(None, None, "aaaaa3@aaa.com", birthdays, 10, 0, self.session, self.user)
        expected_result = [contacts[2]]
        self.assertEqual([result[2]], expected_result)

        # Test upcoming birthdays
        birthdays = True
        result = await get_contacts(None, None, None, birthdays, 10, 0, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        body = ContactSchema(
            name="Test1",
            surname="User1",
            email="aaaaa111@aaa.com",
            number="1234567890111",
            birthday="2990-01-01",
            description="test11111"
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = body
        self.session.execute.return_value = mocked_contact
        result = await get_contact(1, self.session, self.user)
        self.assertEqual(result, body)

    async def test_update_contact(self):
        body = ContactSchema(
            name="Test1",
            surname="User1",
            email="aaaaa111@aaa.com",
            number="1234567890111",
            birthday="2990-01-01",
            description="test11111"
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1, name="Test", surname="User", email="aaaaa@aaa.com",
            number="1234567890", birthday="1990-01-01", description="test", user=self.user
        )
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.session.execute.return_value = mocked_contact
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.number, body.number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.description, body.description)
        self.assertEqual(result.user, self.user)

    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1, name="Test", surname="User", email="aaaaa@aaa.com",
            number="1234567890", birthday="1990-01-01", description="test", user=self.user
        )
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.user, self.user)
