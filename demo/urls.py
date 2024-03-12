from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet,PostViewSet

router = DefaultRouter()

router.register(r'categories',CategoryViewSet,basename="category")
router.register(r'post',PostViewSet,basename="post")
# router.register("likes",basename="likes")
# router.register("comments",basename="comments")

urlpatterns = router.urls
