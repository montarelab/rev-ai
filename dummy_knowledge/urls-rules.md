# Working with `django.urls.path`

To define URLs in Django, you use the `path()` function from the `django.urls` module. It’s commonly used in the `urls.py` file of an app to map URLs to views.

### Basic Usage

```python
from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_view, name='hello'),
    path('blog/<int:post_id>/', views.blog_detail, name='blog_detail'),
]