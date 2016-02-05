from django.conf.urls import include, url
from . import views

app_name = 'bank'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^rachunki/$', views.rachunki, name='rachunki'),
    url(r'^rachunek/(?P<numer>[0-9]+){1}/$', views.rachunek, name='rachunek'),
    url(r'^historia/(?P<numer>[0-9]+){1}/$', views.historia, name='historia'),
    url(r'^zamknij/(?P<numer>[0-9]+){1}/$', views.zamknij, name='zamknij'),
    url(r'^otworz/$', views.otworz, name='otworz'),
    url(r'^kolejny_dzien/$', views.kolejny_dzien, name='kolejny_dzien'),
    url(r'^rodzaj/(?P<id>[0-9]+){1}/$', views.rodzaj, name='rodzaj'),
    url(r'^oferta/$', views.oferta, name='oferta'),
    url(r'^rejestracja/$', views.rejestracja, name='rejestracja'),
]
