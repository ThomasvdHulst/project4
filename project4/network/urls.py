
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("posts/<int:post_id>", views.view_post, name="view_post"),
    path("people/<int:person_id>", views.view_profile, name="view_profile"),
    path("following/<int:user_id>", views.follow_profile, name="follow_profile"),
    path("following", views.following_posts, name="following_posts")
]
