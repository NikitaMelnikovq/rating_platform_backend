from django.contrib import admin

from accounts.models import User
from institute.models import Institute
from subjects.models import Subject
from lessons.models import Lesson
from lessons.models import StudentFeedback


admin.site.register(User)
admin.site.register(Institute)
admin.site.register(Subject)
admin.site.register(Lesson)
admin.site.register(StudentFeedback)