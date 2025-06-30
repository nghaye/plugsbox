from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'plugsbox-api'
router = NetBoxRouter()
router.register('plugs', views.PlugViewSet)
urlpatterns = router.urls