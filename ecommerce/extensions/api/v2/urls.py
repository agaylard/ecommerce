from django.conf.urls import url, include
from rest_framework_extensions.routers import ExtendedSimpleRouter

from ecommerce.core.constants import COURSE_ID_PATTERN
from ecommerce.extensions.api.v2.views import (baskets as basket_views, payments as payment_views,
                                               orders as order_views, refunds as refund_views,
                                               products as product_views, courses as course_views,
                                               publication as publication_views, partners as partner_views,
                                               catalog as catalog_views,
                                               stockrecords as stockrecords_views,
                                               coupons as coupons_views)

ORDER_NUMBER_PATTERN = r'(?P<number>[-\w]+)'
BASKET_ID_PATTERN = r'(?P<basket_id>[\w]+)'

BASKET_URLS = [
    url(r'^$', basket_views.BasketCreateView.as_view(), name='create'),
    url(
        r'^{basket_id}/order/$'.format(basket_id=BASKET_ID_PATTERN),
        basket_views.OrderByBasketRetrieveView.as_view(),
        name='retrieve_order'
    ),
]

COUPON_URLS = [
    url(r'^$', coupons_views.CouponOrderCreateView.as_view({'get': 'list'}), name='create'),
]

PAYMENT_URLS = [
    url(r'^processors/$', payment_views.PaymentProcessorListView.as_view(),
        name='list_processors'),
]

REFUND_URLS = [
    url(r'^$', refund_views.RefundCreateView.as_view(), name='create'),
    url(r'^(?P<pk>[\d]+)/process/$', refund_views.RefundProcessView.as_view(), name='process'),
]

ATOMIC_PUBLICATION_URLS = [
    url(r'^$', publication_views.AtomicPublicationView.as_view(), name='create'),
    url(
        r'^{course_id}$'.format(course_id=COURSE_ID_PATTERN),
        publication_views.AtomicPublicationView.as_view(),
        name='update'
    ),
]

urlpatterns = [
    url(r'^baskets/', include(BASKET_URLS, namespace='baskets')),
    url(r'^coupons/', include(COUPON_URLS, namespace='coupons')),
    url(r'^payment/', include(PAYMENT_URLS, namespace='payment')),
    url(r'^refunds/', include(REFUND_URLS, namespace='refunds')),
    url(r'^publication/', include(ATOMIC_PUBLICATION_URLS, namespace='publication')),
    url(r'^coupons/', include(COUPON_URLS, namespace='coupons'))
]

router = ExtendedSimpleRouter()
router.register(r'courses', course_views.CourseViewSet) \
    .register(r'products', product_views.ProductViewSet,
              base_name='course-product', parents_query_lookups=['course_id'])
router.register(r'partners', partner_views.PartnerViewSet) \
    .register(r'products', product_views.ProductViewSet,
              base_name='partner-product', parents_query_lookups=['stockrecords__partner_id'])
router.register(r'partners', partner_views.PartnerViewSet) \
    .register(r'catalogs', catalog_views.CatalogViewSet,
              base_name='partner-catalogs', parents_query_lookups=['partner_id'])
router.register(r'products', product_views.ProductViewSet)
router.register(r'stockrecords', stockrecords_views.StockRecordViewSet, base_name='stockrecords')

router.register(r'catalogs', catalog_views.CatalogViewSet) \
    .register(r'products', product_views.ProductViewSet, base_name='catalog-product',
              parents_query_lookups=['stockrecords__catalogs'])


router.register(r'orders', order_views.OrderViewSet)

router.register(r'coupons', coupons_views.CouponOrderCreateView, base_name="coupons")

urlpatterns += router.urls
