from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission as AuthPermission
from django.utils import timezone
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from security.permissions.models import Module, Permission, GroupModulePermission
from colorama import init, Fore, Style

# Inicializar colorama para colores en consola
init()

User = get_user_model()

class Command(BaseCommand):
    help = 'Inicializa módulos y permisos para el sistema de permisos personalizados y muestra la configuración actual'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la recreación de los módulos y permisos (cuidado: eliminará los existentes)',
        )
        parser.add_argument(
            '--only-show',
            action='store_true',
            help='Solo mostrar los permisos existentes sin crear nuevos',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        only_show = options.get('only_show', False)
        
        if only_show:
            self.show_existing_permissions()
            return
            
        if force:
            self.stdout.write(self.style.WARNING('⚠️  Eliminando todos los permisos y módulos existentes...'))
            GroupModulePermission.objects.all().delete()
            Permission.objects.all().delete()
            Module.objects.all().delete()
        
        try:
            with transaction.atomic():
                if not only_show:
                    self.stdout.write(self.style.NOTICE('🔄 Inicializando permisos del sistema...'))
                    self.create_groups_and_permissions()
                    self.stdout.write(self.style.SUCCESS('✅ Inicialización completada exitosamente'))
                
                # Mostrar los permisos actuales
                self.show_existing_permissions()
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error durante la inicialización: {str(e)}'))
            raise e

    def create_groups_and_permissions(self):
        # Crear o recuperar los grupos principales
        admin_group, _ = Group.objects.get_or_create(name='Administradores')
        doctors_group, _ = Group.objects.get_or_create(name='Médicos')
        patients_group, _ = Group.objects.get_or_create(name='Pacientes')
        
        self.stdout.write(self.style.SUCCESS('✅ Grupos principales creados/verificados'))
        
        # Definir los módulos
        modules_data = [
            {
                'name': 'Dashboard',
                'code': 'dashboard',
                'description': 'Panel de control y visualización de datos',
                'order': 1
            },
            {
                'name': 'Pacientes',
                'code': 'patients',
                'description': 'Gestión de pacientes y sus datos médicos',
                'order': 2
            },
            {
                'name': 'Médicos',
                'code': 'doctors',
                'description': 'Gestión de médicos, especialidades y horarios',
                'order': 3
            },
            {
                'name': 'Citas',
                'code': 'appointments',
                'description': 'Gestión de citas y reservas',
                'order': 4
            },
            {
                'name': 'Recetas',
                'code': 'prescriptions',
                'description': 'Gestión de recetas médicas',
                'order': 5
            },
            {
                'name': 'Historial Médico',
                'code': 'medical_records',
                'description': 'Gestión de historiales médicos',
                'order': 6
            },
            {
                'name': 'Reportes',
                'code': 'reports',
                'description': 'Generación y visualización de informes',
                'order': 7
            },
            {
                'name': 'Reseñas',
                'code': 'reviews',
                'description': 'Gestión de reseñas y calificaciones',
                'order': 8
            },
            {
                'name': 'Facturación',
                'code': 'billing',
                'description': 'Gestión de pagos y facturación',
                'order': 9
            },
            {
                'name': 'Configuración',
                'code': 'settings',
                'description': 'Configuraciones generales del sistema',
                'order': 10
            },
        ]
        
        # Crear los módulos
        modules = {}
        for module_data in modules_data:
            module, created = Module.objects.update_or_create(
                code=module_data['code'],
                defaults={
                    'name': module_data['name'],
                    'description': module_data['description'],
                    'order': module_data['order']
                }
            )
            modules[module_data['code']] = module
            
            if created:
                self.stdout.write(f'  ✅ Creado módulo: {module.name}')
            else:
                self.stdout.write(f'  🔄 Actualizado módulo: {module.name}')
        
        # Definir permisos para cada módulo
        permissions_data = {
            'dashboard': [
                {
                    'name': 'Ver panel de control',
                    'codename': 'view_dashboard',
                    'description': 'Permite ver el panel de control con estadísticas generales',
                    'groups': ['Administradores', 'Médicos']
                },
                {
                    'name': 'Ver estadísticas avanzadas',
                    'codename': 'view_advanced_stats',
                    'description': 'Permite ver estadísticas y métricas avanzadas',
                    'groups': ['Administradores']
                },
            ],
            'patients': [
                {
                    'name': 'Ver listado de pacientes',
                    'codename': 'view_patients',
                    'description': 'Permite ver el listado de pacientes',
                    'groups': ['Administradores', 'Médicos']
                },
                {
                    'name': 'Agregar pacientes',
                    'codename': 'add_patient',
                    'description': 'Permite agregar nuevos pacientes al sistema',
                    'groups': ['Administradores']
                },
                {
                    'name': 'Editar pacientes',
                    'codename': 'edit_patient',
                    'description': 'Permite editar información de pacientes existentes',
                    'groups': ['Administradores', 'Pacientes']
                },
                {
                    'name': 'Eliminar pacientes',
                    'codename': 'delete_patient',
                    'description': 'Permite eliminar pacientes del sistema',
                    'groups': ['Administradores']
                },
                {
                    'name': 'Ver historial médico',
                    'codename': 'view_medical_history',
                    'description': 'Permite ver el historial médico de los pacientes',
                    'groups': ['Administradores', 'Médicos', 'Pacientes']
                },
                {
                    'name': 'Editar historial médico',
                    'codename': 'edit_medical_history',
                    'description': 'Permite editar el historial médico de los pacientes',
                    'groups': ['Administradores', 'Médicos']
                },
            ],
            'doctors': [
                {
                    'name': 'Ver listado de médicos',
                    'codename': 'view_doctors',
                    'description': 'Permite ver el listado de médicos',
                    'groups': ['Administradores', 'Médicos', 'Pacientes']
                },
                {
                    'name': 'Agregar médicos',
                    'codename': 'add_doctor',
                    'description': 'Permite agregar nuevos médicos al sistema',
                    'groups': ['Administradores']
                },
                {
                    'name': 'Editar médicos',
                    'codename': 'edit_doctor',
                    'description': 'Permite editar información de médicos existentes',
                    'groups': ['Administradores', 'Médicos']
                },
                {
                    'name': 'Eliminar médicos',
                    'codename': 'delete_doctor',
                    'description': 'Permite eliminar médicos del sistema',
                    'groups': ['Administradores']
                },
                {
                    'name': 'Gestionar horarios',
                    'codename': 'manage_schedules',
                    'description': 'Permite gestionar los horarios de disponibilidad de los médicos',
                    'groups': ['Administradores', 'Médicos']
                },
                {
                    'name': 'Gestionar tarifas',
                    'codename': 'manage_fees',
                    'description': 'Permite gestionar las tarifas de consulta de los médicos',
                    'groups': ['Administradores', 'Médicos']
                },
            ],
            'appointments': [
                {
                    'name': 'Ver citas',
                    'codename': 'view_appointments',
                    'description': 'Permite ver las citas médicas',
                    'groups': ['Administradores', 'Médicos', 'Pacientes']
                },
                {
                    'name': 'Crear citas',
                    'codename': 'create_appointment',
                    'description': 'Permite crear nuevas citas',
                    'groups': ['Administradores', 'Médicos', 'Pacientes']
                },
                {
                    'name': 'Editar citas',
                    'codename': 'edit_appointment',
                    'description': 'Permite editar citas existentes',
                    'groups': ['Administradores', 'Médicos']
                },
                {
                    'name': 'Cancelar citas',
                    'codename': 'cancel_appointment',
                    'description': 'Permite cancelar citas',
                    'groups': ['Administradores', 'Médicos', 'Pacientes']
                },
                {
                    'name': 'Confirmar citas',
                    'codename': 'confirm_appointment',
                    'description': 'Permite confirmar citas pendientes',
                    'groups': ['Administradores', 'Médicos']
                },
                {
                    'name': 'Marcar como completada',
                    'codename': 'complete_appointment',
                    'description': 'Permite marcar citas como completadas',
                    'groups': ['Administradores', 'Médicos']
                },
            ],
            'prescriptions': [
                {
                    'name': 'Ver recetas',
                    'codename': 'view_prescriptions',
                    'description': 'Permite ver las recetas médicas',
                    'groups': ['Administradores', 'Médicos', 'Pacientes']
                },
                {
                    'name': 'Crear recetas',
                    'codename': 'create_prescription',
                    'description': 'Permite crear nuevas recetas',
                    'groups': ['Administradores', 'Médicos']
                },
                {
                    'name': 'Editar recetas',
                    'codename': 'edit_prescription',
                    'description': 'Permite editar recetas existentes',
                    'groups': ['Administradores', 'Médicos']
                },
                {
                    'name': 'Eliminar recetas',
                    'codename': 'delete_prescription',
                    'description': 'Permite eliminar recetas',
                    'groups': ['Administradores']
                },
            ],
            'medical_records': [
                {
                    'name': 'Ver historiales',
                    'codename': 'view_records',
                    'description': 'Permite ver los historiales médicos',
                    'groups': ['Administradores', 'Médicos', 'Pacientes']
                },
                {
                    'name': 'Crear historiales',
                    'codename': 'create_record',
                    'description': 'Permite crear nuevos historiales médicos',
                    'groups': ['Administradores', 'Médicos']
                },
                {
                    'name': 'Editar historiales',
                    'codename': 'edit_record',
                    'description': 'Permite editar historiales existentes',
                    'groups': ['Administradores', 'Médicos']
                },
                {
                    'name': 'Añadir diagnóstico',
                    'codename': 'add_diagnosis',
                    'description': 'Permite añadir diagnósticos a los historiales',
                    'groups': ['Administradores', 'Médicos']
                },
            ],
            'reports': [
                {
                    'name': 'Ver informes básicos',
                    'codename': 'view_basic_reports',
                    'description': 'Permite ver informes básicos del sistema',
                    'groups': ['Administradores', 'Médicos']
                },
                {
                    'name': 'Ver informes avanzados',
                    'codename': 'view_advanced_reports',
                    'description': 'Permite ver informes avanzados y detallados',
                    'groups': ['Administradores']
                },
                {
                    'name': 'Exportar informes',
                    'codename': 'export_reports',
                    'description': 'Permite exportar informes en diferentes formatos',
                    'groups': ['Administradores']
                },
            ],
            'reviews': [
                {
                    'name': 'Ver reseñas',
                    'codename': 'view_reviews',
                    'description': 'Permite ver las reseñas y calificaciones',
                    'groups': ['Administradores', 'Médicos', 'Pacientes']
                },
                {
                    'name': 'Crear reseñas',
                    'codename': 'create_review',
                    'description': 'Permite crear nuevas reseñas',
                    'groups': ['Pacientes']
                },
                {
                    'name': 'Moderar reseñas',
                    'codename': 'moderate_reviews',
                    'description': 'Permite aprobar o rechazar reseñas',
                    'groups': ['Administradores']
                },
                {
                    'name': 'Responder reseñas',
                    'codename': 'respond_reviews',
                    'description': 'Permite responder a las reseñas',
                    'groups': ['Administradores', 'Médicos']
                },
            ],
            'billing': [
                {
                    'name': 'Ver facturación',
                    'codename': 'view_billing',
                    'description': 'Permite ver información de facturación',
                    'groups': ['Administradores', 'Médicos', 'Pacientes']
                },
                {
                    'name': 'Crear facturas',
                    'codename': 'create_invoice',
                    'description': 'Permite crear nuevas facturas',
                    'groups': ['Administradores', 'Médicos']
                },
                {
                    'name': 'Registrar pagos',
                    'codename': 'register_payment',
                    'description': 'Permite registrar pagos en el sistema',
                    'groups': ['Administradores']
                },
                {
                    'name': 'Ver reportes financieros',
                    'codename': 'view_financial_reports',
                    'description': 'Permite ver reportes financieros detallados',
                    'groups': ['Administradores']
                },
            ],
            'settings': [
                {
                    'name': 'Ver configuración',
                    'codename': 'view_settings',
                    'description': 'Permite ver la configuración del sistema',
                    'groups': ['Administradores']
                },
                {
                    'name': 'Editar configuración',
                    'codename': 'edit_settings',
                    'description': 'Permite modificar la configuración del sistema',
                    'groups': ['Administradores']
                },
                {
                    'name': 'Gestionar permisos',
                    'codename': 'manage_permissions',
                    'description': 'Permite gestionar los permisos de usuarios y grupos',
                    'groups': ['Administradores']
                },
            ],
        }
        
        # Crear los permisos y asignarlos a grupos
        created_count = 0
        updated_count = 0
        
        for module_code, perms in permissions_data.items():
            module = modules.get(module_code)
            if not module:
                continue
                
            for perm_data in perms:
                # Crear o actualizar el permiso
                perm, created = Permission.objects.update_or_create(
                    module=module,
                    codename=perm_data['codename'],
                    defaults={
                        'name': perm_data['name'],
                        'description': perm_data['description'],
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'    ✅ Creado permiso: {perm}')
                else:
                    updated_count += 1
                
                # Asignar permiso a los grupos especificados
                for group_name in perm_data.get('groups', []):
                    group = Group.objects.get(name=group_name)
                    group_perm, _ = GroupModulePermission.objects.get_or_create(
                        group=group,
                        permission=perm,
                        defaults={'is_active': True}
                    )
                    
        self.stdout.write(self.style.SUCCESS(
            f'✅ Se crearon {created_count} permisos nuevos y se actualizaron {updated_count} permisos existentes.'
        ))
    
    def show_existing_permissions(self):
        """Muestra los permisos actuales configurados en el sistema"""
        self.stdout.write('\n' + '='*80)
        self.stdout.write(Fore.CYAN + Style.BRIGHT + '📋 CONFIGURACIÓN ACTUAL DE PERMISOS' + Style.RESET_ALL)
        self.stdout.write('='*80 + '\n')
        
        # Obtener todos los grupos y mostrar sus permisos
        groups = Group.objects.all()
        
        if not groups.exists():
            self.stdout.write(Fore.YELLOW + '⚠️ No hay grupos en el sistema' + Style.RESET_ALL)
            return
        
        for group in groups:
            self.stdout.write(Fore.GREEN + Style.BRIGHT + f'👥 Grupo: {group.name}' + Style.RESET_ALL)
            self.stdout.write('-'*80)
            
            # Obtener todos los permisos para este grupo
            group_perms = GroupModulePermission.objects.filter(
                group=group, 
                is_active=True
            ).select_related('permission', 'permission__module')
            
            if not group_perms.exists():
                self.stdout.write(Fore.YELLOW + '  No tiene permisos asignados' + Style.RESET_ALL)
                self.stdout.write('')
                continue
            
            # Agrupar por módulo para mejor visualización
            by_module = {}
            for gp in group_perms:
                module_name = gp.permission.module.name
                if module_name not in by_module:
                    by_module[module_name] = []
                by_module[module_name].append(gp.permission)
                
            # Mostrar permisos por módulo
            for module_name, permissions in sorted(by_module.items()):
                self.stdout.write(Fore.BLUE + f'  📁 Módulo: {module_name}' + Style.RESET_ALL)
                for perm in permissions:
                    self.stdout.write(f'    ✓ {perm.name}: {perm.description}')
                self.stdout.write('')
                
            self.stdout.write('')
        
        self.stdout.write('='*80)
