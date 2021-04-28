from django.urls import path     
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index),
    path('register', views.register),
    path('login', views.login),
    path('dashboard', views.show_all),
    path('dashboard/add_product', views.add_product),
    path('dashboard/create', views.create_product),
    path('dashboard/product/<int:product_id>', views.product),
    path('dashboard/product/<int:id>/upload', views.image_upload_view),
    path("dashboard/<int:id>/delete", views.delete),
    path('user/<int:userobj_id>', views.user_profile),
    path('user/<int:currentuser_id>/edit', views.user_profile_edit),
    path('user/<int:currentuser_id>/update', views.user_profile_update),
    path("logout", views.logout),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)