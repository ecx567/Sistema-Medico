from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _


class Module(models.Model):
    """Modelo para representar los módulos del sistema"""
    name = models.CharField(_("Nombre"), max_length=100, unique=True)
    code = models.CharField(_("Código"), max_length=50, unique=True)
    description = models.TextField(_("Descripción"), blank=True)
    order = models.PositiveIntegerField(_("Orden"), default=0)
    is_active = models.BooleanField(_("Activo"), default=True)
    
    class Meta:
        verbose_name = _("Módulo")
        verbose_name_plural = _("Módulos")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Permission(models.Model):
    """Modelo para permisos específicos dentro de cada módulo"""
    module = models.ForeignKey(
        Module, 
        on_delete=models.CASCADE, 
        related_name='permissions',
        verbose_name=_("Módulo")
    )
    name = models.CharField(_("Nombre"), max_length=255)
    codename = models.CharField(_("Código"), max_length=100)
    description = models.TextField(_("Descripción"), blank=True)
    is_active = models.BooleanField(_("Activo"), default=True)
    
    class Meta:
        verbose_name = _("Permiso")
        verbose_name_plural = _("Permisos")
        unique_together = ['module', 'codename']
        ordering = ['module', 'name']
    
    def __str__(self):
        return f"{self.module.name} - {self.name}"


class GroupModulePermission(models.Model):
    """Asignación de permisos a grupos por módulo"""
    group = models.ForeignKey(
        Group, 
        on_delete=models.CASCADE,
        related_name='module_permissions',
        verbose_name=_("Grupo")
    )
    permission = models.ForeignKey(
        Permission, 
        on_delete=models.CASCADE,
        related_name='group_assignments',
        verbose_name=_("Permiso")
    )
    is_active = models.BooleanField(_("Activo"), default=True)
    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Última actualización"), auto_now=True)
    
    class Meta:
        verbose_name = _("Asignación de Permiso")
        verbose_name_plural = _("Asignaciones de Permisos")
        unique_together = ['group', 'permission']
    
    def __str__(self):
        status = "Activo" if self.is_active else "Inactivo"
        return f"{self.group.name} - {self.permission} ({status})"
