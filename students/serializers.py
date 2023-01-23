from rest_framework import serializers
from django.conf import settings
from students.models import Course, Student
from django.core.exceptions import ValidationError


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ("id", "name", "students")

    def validate(self, data):
        if self.context['request'].method == 'POST' or self.context['request'].method == 'PATCH':
            if len(data) > 1:
                if len(data['students']) > settings.MAX_STUDENTS_PER_COURSE:
                    raise ValidationError('Too many students per course.')
        return data