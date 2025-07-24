from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/crear/', views.usuario_create, name='usuario_create'),
    path('usuarios/editar/<int:usuario_id>/', views.usuario_edit, name='usuario_edit'),
    path('usuarios/eliminar/<int:usuario_id>/', views.usuario_delete, name='usuario_delete'),

   
    path('categorias/', views.categorias_list, name='categorias_list'),
    path('categorias/crear/', views.categoria_create, name='categoria_create'),
    path('categorias/editar/<int:id_categoria>/', views.categoria_edit, name='categoria_edit'),
    path('categorias/eliminar/<int:id_categoria>/', views.categoria_delete, name='categoria_delete'),


    path('gastos/', views.gastos_list, name='gastos_list'),
    path('gastos/crear/', views.gasto_create, name='gasto_create'),
    path('gastos/editar/<int:id_gasto>/', views.gasto_edit, name='gasto_edit'),
    path('gastos/eliminar/<int:id_gasto>/', views.gasto_delete, name='gasto_delete'),


    path('documentos/', views.documentos_list, name='documentos_list'),
    path('documentos/crear/', views.documento_create, name='documento_create'),
    path('documentos/editar/<int:id_documento>/', views.documento_edit, name='documento_edit'),
    path('documentos/eliminar/<int:id_documento>/', views.documento_delete, name='documento_delete'),


    path('reembolsos/', views.reembolsos_list, name='reembolsos_list'),
    path('reembolsos/crear/', views.reembolso_create, name='reembolso_create'),
    path('reembolsos/editar/<int:id_reembolso>/', views.reembolso_edit, name='reembolso_edit'),
    path('reembolsos/eliminar/<int:id_reembolso>/', views.reembolso_delete, name='reembolso_delete'),


    path('detalle_reembolso/', views.detalle_reembolso_list, name='detalle_reembolso_list'),
    path('detalle_reembolso/crear/', views.detalle_reembolso_create, name='detalle_reembolso_create'),
    path('detalle_reembolso/editar/<int:id_detalle>/', views.detalle_reembolso_edit, name='detalle_reembolso_edit'),
    path('detalle_reembolso/eliminar/<int:id_detalle>/', views.detalle_reembolso_delete, name='detalle_reembolso_delete'),
]


