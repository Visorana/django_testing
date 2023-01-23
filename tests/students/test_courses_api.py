import pytest
from django.forms import model_to_dict
from rest_framework.test import APIClient
from model_bakery import baker
from django.conf import settings
from students.models import Course, Student


@pytest.fixture()
def client():
    return APIClient()


@pytest.fixture()
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


@pytest.fixture()
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


@pytest.mark.django_db
def test_get_course(client, course_factory):
    course = course_factory(_quantity=1)
    response = client.get('/api/v1/courses/')
    data = response.json()
    assert response.status_code == 200
    assert model_to_dict(course[0]) == data[-1]


@pytest.mark.django_db
def test_get_list_courses(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get('/api/v1/courses/')
    data = response.json()
    assert response.status_code == 200
    for i, m in enumerate(data):
        assert m == model_to_dict(courses[i])


@pytest.mark.django_db
def test_filter_courses_id(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get(f'/api/v1/courses/?id={model_to_dict(courses[0])["id"]}')
    data = response.json()
    assert response.status_code == 200
    assert data[0] == model_to_dict(courses[0])


@pytest.mark.django_db
def test_filter_courses_name(client, course_factory):
    course = course_factory(_quantity=1)
    response = client.get(f'/api/v1/courses/?name={model_to_dict(course[0])["name"]}')
    data = response.json()
    assert response.status_code == 200
    assert data[0] == model_to_dict(course[0])


@pytest.mark.django_db
def test_create_course(client):
    response = client.post('/api/v1/courses/', data={'name': 'Python'})
    assert response.status_code == 201


@pytest.mark.django_db
def test_patch_course(client, course_factory):
    course = course_factory(_quantity=1)
    response = client.patch(f'/api/v1/courses/{model_to_dict(course[0])["id"]}/', data={'name': 'Python'})
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_course(client, course_factory):
    course = course_factory(_quantity=1)
    response = client.delete(f'/api/v1/courses/{model_to_dict(course[0])["id"]}/')
    assert response.status_code == 204


@pytest.mark.django_db
@pytest.mark.parametrize('number_of_students, return_code', [
    (settings.MAX_STUDENTS_PER_COURSE - 1, 201),
    (settings.MAX_STUDENTS_PER_COURSE, 201),
    (settings.MAX_STUDENTS_PER_COURSE + 1, 400)
])
def test_max_students(number_of_students, return_code, client, student_factory):
    students = student_factory(_quantity=number_of_students)
    students_id = [student.id for student in students]
    response = client.post('/api/v1/courses/', data={'name': 'Python', 'students': students_id})
    assert response.status_code == return_code
