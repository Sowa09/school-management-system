from unittest import TestCase

from django.contrib.auth import get_user_model, authenticate
from django.test import Client
from django.urls import reverse
from main_app.models import Student, SchoolClass, Teacher
import pytest
from django.contrib.auth.models import User
import pdb


def create_user():
    """
    Function that creates django auth user for testing
    :return: user in django application
    """
    user = User.objects.create_user(username='testuser', password='12345')
    return user


@pytest.mark.django_db
def test_add_student_to_db():
    """
    Testing student form.
    :return: asserts
    """
    student = Student.objects.create(first_name='Adam', last_name='Korzeniak', age=23)
    second_student = Student.objects.create(first_name='Adama', last_name='Korzeniak1', age=24)

    assert len(Student.objects.all()) == 2
    assert Student.objects.get(first_name='Adam', last_name='Korzeniak', age=23) == student
    assert Student.objects.get(first_name='Adama', last_name='Korzeniak1', age=24) == second_student


@pytest.mark.django_db
def test_login_view_access(client):
    """
    Test if client can log into app
    :param client:
    :return: asserts
    """

    create_user()
    response = client.post('/', {'uname': 'testuser', 'psw': '12345'})

    assert response.status_code == 302
    assert client.get('/index/').status_code == 200
    assert client.get('/student/list').status_code == 200


@pytest.mark.django_db
class SigninLogoutTest(TestCase):
    """
    Login, logout tests. Passing wrong password or username tests.
    """

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username='test', password='12345')
        self.client = Client()

    def tearDown(self) -> None:
        self.user.delete()

    def test_correct(self):
        user = authenticate(username='test', password='12345')
        self.assertTrue((user is not None) and user.is_authenticated)

    def test_wrong_username(self):
        user = authenticate(username='adam', password='12345')
        self.assertFalse(user is not None and user.is_authenticated)
        # or

    def test_wrong_password(self):
        user = authenticate(username='test', password='123456')
        self.assertFalse(user is not None and user.is_authenticated)
        # or

    def test_logout(self):
        user = authenticate(username='test', password='12345')
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(user is not user.is_authenticated)


@pytest.mark.django_db
class CreateUSerTest(TestCase):
    """
    User creation test.
    """

    def setUp(self) -> None:
        self.client = Client()

    def tearDown(self) -> None:
        self.user.delete()

    def test_create_user(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        response = self.client.post('/', {'uname': 'testuser', 'psw': '12345'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user is not None)


@pytest.mark.django_db
class CountingStudentsTeacherTest(TestCase):
    """
    Testing counting students and teachers in base view.
    """

    def setUp(self) -> None:
        self.client = Client()
        self.student1 = Student.objects.create(first_name='Adam', last_name='Sokołowski', age=23)
        self.student2 = Student.objects.create(first_name='Adam1', last_name='Momo', age=24)
        self.student3 = Student.objects.create(first_name='Adam3', last_name='Kowalski', age=73)
        self.teacher1 = Teacher.objects.create(first_name='Agnieszka', last_name='Stępień')
        self.teacher2 = Teacher.objects.create(first_name='Mariola', last_name='Kałamaga')
        self.teacher3 = Teacher.objects.create(first_name='Magda', last_name='Kuternoga')
        self.teacher4 = Teacher.objects.create(first_name='Magda1', last_name='Kuternoga1')

    def tearDown(self) -> None:
        pass

    def test_count_students(self):
        self.student_count = Student.objects.count()
        self.assertEqual(self.student_count, 3)

    def test_count_teacher(self):
        self.teacher_count = Teacher.objects.count()
        self.assertEqual(self.teacher_count, 4)

    def test_count_students_wrong(self):
        self.student_count = Student.objects.count()
        self.assertTrue(self.student_count, 2)

    def test_count_teacher_wrong(self):
        self.teacher_count = Teacher.objects.count()
        self.assertTrue(self.teacher_count, 5)


@pytest.mark.django_db
def test_add_class_to_db(client):
    """
    Function test SchoolClass form.
    :return: asserts
    """
    create_user()
    login = client.post('/', {'uname': 'testuser', 'psw': '12345'})
    new_class = SchoolClass.objects.create(name='32', year=2021)
    response = client.get('/student/add')

    assert login.status_code == 302
    assert response.status_code == 200
    assert SchoolClass.objects.count() == 1
    assert SchoolClass.objects.get(name='32', year=2021) == new_class


@pytest.mark.django_db
class ClassUpdateTest(TestCase):
    """
    Modify view test.
    """

    def setUp(self) -> None:
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='test', password='12345')

    def tearDown(self) -> None:
        pass

    def test_class_update(self):
        sch_class = SchoolClass.objects.create(pk=1, name=3, year=2020)
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(('class-modify'), kwargs={'pk': sch_class.id}),
            {'name': '6', 'year': 2022})

        self.assertEqual(response.status_code, 302)
        sch_class.refresh_from_db()
        self.assertEqual(sch_class.name, '6')
        self.assertEqual(sch_class.year, 2022)

    def test_class_no_update(self):
        sch_class = SchoolClass.objects.create(pk=1, name=3, year=2020)
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(('class-modify'), kwargs={'pk': sch_class.id}),
            {'name': '', 'year': ''})

        self.assertEqual(response.status_code, 200)
        sch_class.refresh_from_db()
        self.assertEqual(sch_class.name, '3')
        self.assertEqual(sch_class.year, 2020)


# @pytest.mark.django_db
# class TeacherFormTest(TestCase):
#     """
#     Tests for teacher form view.
#     """
#
#     def setUp(self) -> None:
#         self.client = Client()
#         self.user = get_user_model().objects.create_user(username='test', password='12345')
#
#     def tearDown(self) -> None:
#         pass
#
#     def test_teacher_add(self):
#         self.client.force_login(self.user)
#         response = self.client.post(reverse('teacher-add'),
#                                     {'first_name': 'Robert', 'last_name': 'Kowalski', 'gender': '32',
#                                      'subject': 'Chemia'})
#
#         self.assertEqual(response.status_code, 302)
