from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("register", views.register, name="register"),
    path("create/<str:project>", views.create, name="create"),
    path("manage/<str:project>", views.manage, name="manage"),
    path("console/<str:project>/<str:instance_name>", views.console, name="console"),
    path("delete/<str:project>", views.delete, name="delete"),
    path("wait/<str:operation_id>", views.wait, name="wait"),
    path("access", views.access, name="access"),
    path("files", views.files, name="files"),
]
