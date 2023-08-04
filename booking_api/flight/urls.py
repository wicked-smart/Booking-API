from django.urls import re_path, path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    re_path('^test-index/(?P<foo>[0-9]{5})/$', views.test_index, name="test-index"),
    path('blog/<slug:slug>', views.blog, name="blog")
]

urlpatterns += static(settings.STATIC_URL, document=settings.STATIC_ROOT)