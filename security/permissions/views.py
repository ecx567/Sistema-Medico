from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import Module, Permission, GroupModulePermission
from .forms import PermissionManagementForm


@staff_member_required
def manage_permissions(request):
    """Vista principal para la gestión de permisos"""
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        messages.error(request, _("No tienes permisos para acceder a esta página."))
        return redirect('home')
        
    selected_group_id = request.GET.get('group')
    selected_module_id = request.GET.get('module')
    
    # Obtenemos todos los grupos y módulos para los selectores
    groups = Group.objects.all()
    modules = Module.objects.filter(is_active=True)
    
    # Variables para el contexto
    permissions = []
    permissions_data = {}
    has_permissions = False
    selected_group = None
    selected_module = None
    
    # Si se seleccionó grupo y módulo, cargamos los permisos disponibles
    if selected_group_id and selected_module_id:
        selected_group = Group.objects.filter(id=selected_group_id).first()
        selected_module = Module.objects.filter(id=selected_module_id).first()
        
        if selected_group and selected_module:
            # Obtenemos los permisos para el módulo seleccionado
            permissions = Permission.objects.filter(
                module=selected_module,
                is_active=True
            )
            
            # Verificamos si hay permisos disponibles
            has_permissions = permissions.exists()
            
            # Preparamos los datos para el formulario
            for perm in permissions:
                # Buscamos si el grupo ya tiene asignado este permiso
                group_perm = GroupModulePermission.objects.filter(
                    group=selected_group,
                    permission=perm
                ).first()
                
                # Guardamos los datos del permiso
                permissions_data[perm.id] = {
                    'name': perm.name,
                    'description': perm.description,
                    'is_active': group_perm.is_active if group_perm else False
                }
    
    # Si se envió el formulario, procesamos los datos
    if request.method == 'POST':
        # Recuperamos el grupo y módulo del formulario
        group_id = request.POST.get('group')
        module_id = request.POST.get('module')
        
        if group_id and module_id:
            group = Group.objects.get(id=group_id)
            module = Module.objects.get(id=module_id)
            
            # Obtenemos los permisos del módulo
            module_permissions = Permission.objects.filter(module=module, is_active=True)
            
            # Actualizamos cada permiso según lo marcado en el formulario
            for perm in module_permissions:
                is_active = request.POST.get(f'perm_{perm.id}') == 'on'
                
                # Obtenemos o creamos la asignación de permiso para este grupo
                group_perm, created = GroupModulePermission.objects.get_or_create(
                    group=group,
                    permission=perm,
                    defaults={'is_active': is_active}
                )
                
                # Si ya existía, actualizamos su estado
                if not created:
                    group_perm.is_active = is_active
                    group_perm.save()
            
            messages.success(request, _("Permisos actualizados correctamente"))
            return redirect(f'?group={group_id}&module={module_id}')
    
    # Contexto para la plantilla
    context = {
        'groups': groups,
        'modules': modules,
        'selected_group': selected_group,
        'selected_module': selected_module,
        'permissions': permissions,
        'permissions_data': permissions_data,
        'has_permissions': has_permissions,
    }
    
    return render(request, 'permissions/manage.html', context)
