from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import (Usuarios, Categorias, Gastos, Documentos, Reembolsos, Detalle_Reembolso)


from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
import json
from datetime import datetime, timedelta
from calendar import month_name
import locale

def inicio(request):
    """
    Vista principal que renderiza el dashboard con 10 KPIs diferentes
    """
    try:
        # Configurar locale para español (opcional)
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        except:
            pass  # Si no está disponible, continuar
        
        kpis = {}
        
        # KPI 1: Total de usuarios registrados
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Usuarios;")
            kpis['total_usuarios'] = cursor.fetchone()[0]
        
        # KPI 2: Gasto total registrado
        with connection.cursor() as cursor:
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM Gastos;")
            kpis['gasto_total'] = cursor.fetchone()[0] or 0
        
        # KPI 3: Total de reembolsos solicitados
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Reembolsos;")
            kpis['total_reembolsos'] = cursor.fetchone()[0]
        
        # KPI 4: Gastos sin documentos adjuntos
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM Gastos g
                LEFT JOIN Documentos d ON g.id_gasto = d.id_gasto
                WHERE d.id_documento IS NULL;
            """)
            kpis['gastos_sin_documentos'] = cursor.fetchone()[0]
        
        # KPI 5: Usuarios por departamento (Pie Chart)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT departamento, COUNT(*) as cantidad 
                FROM Usuarios 
                WHERE departamento IS NOT NULL 
                GROUP BY departamento 
                ORDER BY cantidad DESC;
            """)
            results = cursor.fetchall()
            
            if results:
                kpis['usuarios_departamento'] = {
                    'labels': json.dumps([row[0] for row in results]),
                    'data': json.dumps([row[1] for row in results])
                }
            else:
                kpis['usuarios_departamento'] = {
                    'labels': json.dumps(['Sin datos']),
                    'data': json.dumps([0])
                }
        
        # KPI 6: Top 5 usuarios con mayor gasto (Bar Chart)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.nombre, COALESCE(SUM(g.monto), 0) AS total
                FROM Usuarios u
                LEFT JOIN Gastos g ON u.id_usuario = g.id_usuario
                GROUP BY u.id_usuario, u.nombre
                ORDER BY total DESC
                LIMIT 5;
            """)
            results = cursor.fetchall()
            
            if results:
                kpis['top_usuarios'] = {
                    'labels': json.dumps([row[0] for row in results]),
                    'data': json.dumps([float(row[1]) for row in results])
                }
            else:
                kpis['top_usuarios'] = {
                    'labels': json.dumps(['Sin datos']),
                    'data': json.dumps([0])
                }
        
        # KPI 7: Documentos por tipo (Doughnut Chart)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tipo, COUNT(*) as cantidad 
                FROM Documentos 
                WHERE tipo IS NOT NULL 
                GROUP BY tipo 
                ORDER BY cantidad DESC;
            """)
            results = cursor.fetchall()
            
            if results:
                kpis['documentos_tipo'] = {
                    'labels': json.dumps([row[0] for row in results]),
                    'data': json.dumps([row[1] for row in results])
                }
            else:
                kpis['documentos_tipo'] = {
                    'labels': json.dumps(['PDF', 'JPG', 'PNG', 'XLSX']),
                    'data': json.dumps([15, 25, 20, 10])  # Datos de ejemplo
                }
        
        # KPI 8: Gastos por mes (Line Chart)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    TO_CHAR(fecha_gasto, 'YYYY-MM') as mes,
                    COALESCE(SUM(monto), 0) as total
                FROM Gastos 
                WHERE fecha_gasto >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY TO_CHAR(fecha_gasto, 'YYYY-MM')
                ORDER BY mes;
            """)
            results = cursor.fetchall()
            
            if results:
                # Convertir formato de fecha
                labels = []
                for row in results:
                    try:
                        fecha = datetime.strptime(row[0], '%Y-%m')
                        labels.append(fecha.strftime('%b %Y'))
                    except:
                        labels.append(row[0])
                
                kpis['gastos_mensuales'] = {
                    'labels': json.dumps(labels),
                    'data': json.dumps([float(row[1]) for row in results])
                }
            else:
                # Datos de ejemplo para los últimos 6 meses
                today = datetime.now()
                months = []
                data = []
                for i in range(6):
                    month_date = today - timedelta(days=30*i)
                    months.append(month_date.strftime('%b %Y'))
                    data.append(1000 + (i * 500))  # Datos de ejemplo
                
                kpis['gastos_mensuales'] = {
                    'labels': json.dumps(list(reversed(months))),
                    'data': json.dumps(list(reversed(data)))
                }
        
        # KPI 9: Monto total aprobado por usuario (Horizontal Bar Chart)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.nombre, COALESCE(SUM(d.monto_aprobado), 0) AS total_aprobado
                FROM Usuarios u
                LEFT JOIN Reembolsos r ON u.id_usuario = r.id_usuario
                LEFT JOIN Detalle_Reembolso d ON r.id_reembolso = d.id_reembolso
                GROUP BY u.id_usuario, u.nombre
                HAVING COALESCE(SUM(d.monto_aprobado), 0) > 0
                ORDER BY total_aprobado DESC
                LIMIT 8;
            """)
            results = cursor.fetchall()
            
            if results:
                kpis['monto_aprobado'] = {
                    'labels': json.dumps([row[0] for row in results]),
                    'data': json.dumps([float(row[1]) for row in results])
                }
            else:
                kpis['monto_aprobado'] = {
                    'labels': json.dumps(['Usuario 1', 'Usuario 2', 'Usuario 3']),
                    'data': json.dumps([1500, 1200, 800])  # Datos de ejemplo
                }
        
        # KPI 10: Gastos vs Reembolsos por categoría (Radar Chart)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.nombre,
                    COALESCE(SUM(g.monto), 0) as total_gastos,
                    COALESCE(SUM(dr.monto_aprobado), 0) as total_reembolsos
                FROM Categorias c
                LEFT JOIN Gastos g ON c.id_categoria = g.id_categoria
                LEFT JOIN Detalle_Reembolso dr ON g.id_gasto = dr.id_gasto
                GROUP BY c.id_categoria, c.nombre
                ORDER BY total_gastos DESC
                LIMIT 6;
            """)
            results = cursor.fetchall()
            
            if results:
                kpis['gastos_reembolsos'] = {
                    'labels': json.dumps([row[0] for row in results]),
                    'gastos': json.dumps([float(row[1]) for row in results]),
                    'reembolsos': json.dumps([float(row[2]) for row in results])
                }
            else:
                kpis['gastos_reembolsos'] = {
                    'labels': json.dumps(['Transporte', 'Alimentación', 'Oficina', 'Viajes', 'Otros']),
                    'gastos': json.dumps([2500, 1800, 1200, 3000, 800]),
                    'reembolsos': json.dumps([2000, 1500, 1000, 2800, 600])
                }
        
        # KPI 11: Estado de reembolsos (Polar Area Chart)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT estado, COUNT(*) as cantidad
                FROM Reembolsos
                WHERE estado IS NOT NULL
                GROUP BY estado
                ORDER BY cantidad DESC;
            """)
            results = cursor.fetchall()
            
            if results:
                kpis['estado_reembolsos'] = {
                    'labels': json.dumps([row[0] for row in results]),
                    'data': json.dumps([row[1] for row in results])
                }
            else:
                kpis['estado_reembolsos'] = {
                    'labels': json.dumps(['Aprobado', 'Pendiente', 'Rechazado', 'En Revisión']),
                    'data': json.dumps([45, 23, 8, 12])  # Datos de ejemplo
                }
        
        # KPI 12: Promedio de gastos por categoría (Bar Chart)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.nombre, COALESCE(AVG(g.monto), 0) as promedio
                FROM Categorias c
                LEFT JOIN Gastos g ON c.id_categoria = g.id_categoria
                GROUP BY c.id_categoria, c.nombre
                HAVING COUNT(g.id_gasto) > 0
                ORDER BY promedio DESC;
            """)
            results = cursor.fetchall()
            
            if results:
                kpis['promedio_categorias'] = {
                    'labels': json.dumps([row[0] for row in results]),
                    'data': json.dumps([float(row[1]) for row in results])
                }
            else:
                kpis['promedio_categorias'] = {
                    'labels': json.dumps(['Transporte', 'Alimentación', 'Oficina', 'Viajes']),
                    'data': json.dumps([150, 85, 120, 350])  # Datos de ejemplo
                }
        
        # KPI 13: Tendencia de registro de usuarios (Area Chart)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    TO_CHAR(fecha_registro, 'YYYY-MM') as mes,
                    COUNT(*) as cantidad
                FROM Usuarios 
                WHERE fecha_registro >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY TO_CHAR(fecha_registro, 'YYYY-MM')
                ORDER BY mes;
            """)
            results = cursor.fetchall()
            
            if results:
                # Convertir formato de fecha
                labels = []
                for row in results:
                    try:
                        fecha = datetime.strptime(row[0], '%Y-%m')
                        labels.append(fecha.strftime('%b %Y'))
                    except:
                        labels.append(row[0])
                
                kpis['tendencia_usuarios'] = {
                    'labels': json.dumps(labels),
                    'data': json.dumps([row[1] for row in results])
                }
            else:
                # Datos de ejemplo para los últimos 6 meses
                today = datetime.now()
                months = []
                data = []
                for i in range(6):
                    month_date = today - timedelta(days=30*i)
                    months.append(month_date.strftime('%b %Y'))
                    data.append(2 + i)  # Datos de ejemplo
                
                kpis['tendencia_usuarios'] = {
                    'labels': json.dumps(list(reversed(months))),
                    'data': json.dumps(list(reversed(data)))
                }
        
        # KPI 14: Distribución de gastos (Bubble Chart)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    u.nombre,
                    COUNT(g.id_gasto) as num_gastos,
                    COALESCE(AVG(g.monto), 0) as promedio_gasto,
                    COALESCE(SUM(g.monto), 0) as total_gasto
                FROM Usuarios u
                LEFT JOIN Gastos g ON u.id_usuario = g.id_usuario
                GROUP BY u.id_usuario, u.nombre
                HAVING COUNT(g.id_gasto) > 0
                ORDER BY total_gasto DESC
                LIMIT 10;
            """)
            results = cursor.fetchall()
            
            if results:
                bubble_data = []
                for i, row in enumerate(results):
                    bubble_data.append({
                        'x': row[1],  # número de gastos
                        'y': float(row[2]),  # promedio de gasto
                        'r': min(max(float(row[3])/100, 5), 25)  # radio basado en total (min 5, max 25)
                    })
                
                kpis['distribucion_gastos'] = json.dumps(bubble_data)
            else:
                # Datos de ejemplo
                kpis['distribucion_gastos'] = json.dumps([
                    {'x': 15, 'y': 250, 'r': 20},
                    {'x': 8, 'y': 180, 'r': 15},
                    {'x': 12, 'y': 320, 'r': 18},
                    {'x': 6, 'y': 150, 'r': 10},
                    {'x': 20, 'y': 280, 'r': 25}
                ])
    
    except Exception as e:
        # En caso de error, proporcionar datos de ejemplo
        print(f"Error en KPIs: {e}")
        
        kpis = {
            'total_usuarios': 50,
            'gasto_total': 15750.50,
            'total_reembolsos': 23,
            'gastos_sin_documentos': 8,
            'usuarios_departamento': {
                'labels': json.dumps(['Ventas', 'Marketing', 'IT', 'RRHH', 'Finanzas']),
                'data': json.dumps([15, 12, 8, 7, 8])
            },
            'top_usuarios': {
                'labels': json.dumps(['Juan Pérez', 'María García', 'Carlos López', 'Ana Martín', 'Luis Rodríguez']),
                'data': json.dumps([2500, 2200, 1800, 1650, 1400])
            },
            'documentos_tipo': {
                'labels': json.dumps(['PDF', 'JPG', 'PNG', 'XLSX']),
                'data': json.dumps([35, 28, 22, 15])
            },
            'gastos_mensuales': {
                'labels': json.dumps(['Ene 2024', 'Feb 2024', 'Mar 2024', 'Abr 2024', 'May 2024', 'Jun 2024']),
                'data': json.dumps([1200, 1500, 1800, 2200, 1900, 2100])
            },
            'monto_aprobado': {
                'labels': json.dumps(['Juan Pérez', 'María García', 'Carlos López', 'Ana Martín']),
                'data': json.dumps([2200, 1800, 1500, 1200])
            },
            'gastos_reembolsos': {
                'labels': json.dumps(['Transporte', 'Alimentación', 'Oficina', 'Viajes', 'Otros']),
                'gastos': json.dumps([2500, 1800, 1200, 3000, 800]),
                'reembolsos': json.dumps([2000, 1500, 1000, 2800, 600])
            },
            'estado_reembolsos': {
                'labels': json.dumps(['Aprobado', 'Pendiente', 'Rechazado', 'En Revisión']),
                'data': json.dumps([45, 23, 8, 12])
            },
            'promedio_categorias': {
                'labels': json.dumps(['Viajes', 'Transporte', 'Oficina', 'Alimentación', 'Otros']),
                'data': json.dumps([350, 150, 120, 85, 95])
            },
            'tendencia_usuarios': {
                'labels': json.dumps(['Ene 2024', 'Feb 2024', 'Mar 2024', 'Abr 2024', 'May 2024', 'Jun 2024']),
                'data': json.dumps([3, 5, 4, 8, 6, 7])
            },
            'distribucion_gastos': json.dumps([
                {'x': 15, 'y': 250, 'r': 20},
                {'x': 8, 'y': 180, 'r': 15},
                {'x': 12, 'y': 320, 'r': 18},
                {'x': 6, 'y': 150, 'r': 10},
                {'x': 20, 'y': 280, 'r': 25},
                {'x': 10, 'y': 200, 'r': 12}
            ])
        }
    
    context = {
        'kpis': kpis
    }
    
    return render(request, 'inicio.html', context)


# --- Usuarios --- #
def usuarios_list(request):
    usuarios = Usuarios.objects.all().order_by('-fecha_creacion')
    return render(request, 'usuarios_list.html', {'usuarios': usuarios})


def usuario_create(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        departamento = request.POST.get('departamento')
        fecha_registro = request.POST.get('fecha_registro')

        usuario = Usuarios.objects.create(
            nombre=nombre,
            correo=correo,
            departamento=departamento,
            fecha_registro=fecha_registro,
            fecha_creacion=timezone.now(),
            fecha_actualizacion=timezone.now()
        )
        messages.success(request, 'Usuario creado correctamente.')
        return redirect('usuarios_list')
    return render(request, 'usuario_form.html', {'accion': 'Crear'})


def usuario_edit(request, usuario_id):
    usuario = get_object_or_404(Usuarios, id_usuario=usuario_id)
    if request.method == "POST":
        usuario.nombre = request.POST.get('nombre')
        usuario.correo = request.POST.get('correo')
        usuario.departamento = request.POST.get('departamento')
        usuario.fecha_registro = request.POST.get('fecha_registro')
        usuario.fecha_actualizacion = timezone.now()
        usuario.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('usuarios_list')
    return render(request, 'usuario_form.html', {'usuario': usuario, 'accion': 'Editar'})


def usuario_delete(request, usuario_id):
    usuario = get_object_or_404(Usuarios, id_usuario=usuario_id)
    usuario.delete()
    messages.success(request, 'Usuario eliminado correctamente.')
    return redirect('usuarios_list')


# --- Categorias --- #
def categorias_list(request):
    categorias = Categorias.objects.all().order_by('-fecha_creacion')
    return render(request, 'categorias_list.html', {'categorias': categorias})


def categoria_create(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        estado = request.POST.get('estado')
        ahora = timezone.now()
        categoria = Categorias(
            nombre=nombre,
            descripcion=descripcion,
            estado=estado,
            fecha_creacion=ahora,
            fecha_actualizacion=ahora
        )
        categoria.save(force_insert=True)
        messages.success(request, 'Categoría creada correctamente.')
        return redirect('categorias_list')
    return render(request, 'categoria_form.html', {'accion': 'Crear'})


def categoria_edit(request, id_categoria):
    categoria = get_object_or_404(Categorias, id_categoria=id_categoria)
    if request.method == 'POST':
        categoria.nombre = request.POST.get('nombre')
        categoria.descripcion = request.POST.get('descripcion')
        categoria.estado = request.POST.get('estado')
        categoria.fecha_actualizacion = timezone.now()
        categoria.save(force_update=True)
        messages.success(request, 'Categoría actualizada correctamente.')
        return redirect('categorias_list')
    return render(request, 'categoria_form.html', {'categoria': categoria, 'accion': 'Editar'})


def categoria_delete(request, id_categoria):
    categoria = get_object_or_404(Categorias, id_categoria=id_categoria)
    categoria.delete()
    messages.success(request, 'Categoría eliminada correctamente.')
    return redirect('categorias_list')


# --- Gastos --- #
def gastos_list(request):
    gastos = Gastos.objects.select_related('id_usuario', 'id_categoria').all().order_by('-fecha_creacion')
    return render(request, 'gastos_list.html', {'gastos': gastos})


def gasto_create(request):
    usuarios = Usuarios.objects.all()
    categorias = Categorias.objects.all()

    if request.method == 'POST':
        id_usuario = request.POST.get('id_usuario')
        id_categoria = request.POST.get('id_categoria')
        monto = request.POST.get('monto')
        fecha_gasto = request.POST.get('fecha_gasto')
        descripcion = request.POST.get('descripcion')
        ahora = timezone.now()

        gasto = Gastos(
            id_usuario=Usuarios.objects.get(pk=id_usuario),
            id_categoria=Categorias.objects.get(pk=id_categoria),
            monto=monto,
            fecha_gasto=fecha_gasto,
            descripcion=descripcion,
            fecha_creacion=ahora,
            fecha_actualizacion=ahora,
        )
        gasto.save(force_insert=True)
        messages.success(request, 'Gasto creado correctamente.')
        return redirect('gastos_list')

    return render(request, 'gasto_form.html', {
        'usuarios': usuarios,
        'categorias': categorias,
        'accion': 'Crear'
    })


def gasto_edit(request, id_gasto):
    gasto = get_object_or_404(Gastos, id_gasto=id_gasto)
    usuarios = Usuarios.objects.all()
    categorias = Categorias.objects.all()

    if request.method == 'POST':
        gasto.id_usuario = Usuarios.objects.get(pk=request.POST.get('id_usuario'))
        gasto.id_categoria = Categorias.objects.get(pk=request.POST.get('id_categoria'))
        gasto.monto = request.POST.get('monto')
        gasto.fecha_gasto = request.POST.get('fecha_gasto')
        gasto.descripcion = request.POST.get('descripcion')
        gasto.fecha_actualizacion = timezone.now()
        gasto.save(force_update=True)
        messages.success(request, 'Gasto actualizado correctamente.')
        return redirect('gastos_list')

    return render(request, 'gasto_form.html', {
        'gasto': gasto,
        'usuarios': usuarios,
        'categorias': categorias,
        'accion': 'Editar'
    })


def gasto_delete(request, id_gasto):
    gasto = get_object_or_404(Gastos, id_gasto=id_gasto)
    gasto.delete()
    messages.success(request, 'Gasto eliminado correctamente.')
    return redirect('gastos_list')


# --- Documentos --- #
def documentos_list(request):
    documentos = Documentos.objects.select_related('id_gasto').all().order_by('-fecha_creacion')
    return render(request, 'documentos_list.html', {'documentos': documentos})


def documento_create(request):
    gastos = Gastos.objects.all()
    if request.method == 'POST':
        id_gasto = request.POST.get('id_gasto')
        nombre_archivo = request.POST.get('nombre_archivo')
        tipo = request.POST.get('tipo')
        ruta_archivo = request.POST.get('ruta_archivo')
        ahora = timezone.now()

        documento = Documentos(
            id_gasto=Gastos.objects.get(pk=id_gasto),
            nombre_archivo=nombre_archivo,
            tipo=tipo,
            ruta_archivo=ruta_archivo,
            fecha_creacion=ahora,
            fecha_actualizacion=ahora
        )
        documento.save(force_insert=True)
        messages.success(request, 'Documento creado correctamente.')
        return redirect('documentos_list')

    return render(request, 'documento_form.html', {
        'gastos': gastos,
        'accion': 'Crear'
    })


def documento_edit(request, id_documento):
    documento = get_object_or_404(Documentos, id_documento=id_documento)
    gastos = Gastos.objects.all()

    if request.method == 'POST':
        documento.id_gasto = Gastos.objects.get(pk=request.POST.get('id_gasto'))
        documento.nombre_archivo = request.POST.get('nombre_archivo')
        documento.tipo = request.POST.get('tipo')
        documento.ruta_archivo = request.POST.get('ruta_archivo')
        documento.fecha_actualizacion = timezone.now()
        documento.save(force_update=True)
        messages.success(request, 'Documento actualizado correctamente.')
        return redirect('documentos_list')

    return render(request, 'documento_form.html', {
        'documento': documento,
        'gastos': gastos,
        'accion': 'Editar'
    })


def documento_delete(request, id_documento):
    documento = get_object_or_404(Documentos, id_documento=id_documento)
    documento.delete()
    messages.success(request, 'Documento eliminado correctamente.')
    return redirect('documentos_list')


# --- Reembolsos --- #
def reembolsos_list(request):
    reembolsos = Reembolsos.objects.select_related('id_usuario').all().order_by('-fecha_creacion')
    return render(request, 'reembolsos_list.html', {'reembolsos': reembolsos})


def reembolso_create(request):
    usuarios = Usuarios.objects.all()
    if request.method == 'POST':
        id_usuario = request.POST.get('id_usuario')
        total = request.POST.get('total')
        estado = request.POST.get('estado')
        fecha_solicitud = request.POST.get('fecha_solicitud')
        ahora = timezone.now()

        reembolso = Reembolsos(
            id_usuario=Usuarios.objects.get(pk=id_usuario),
            total=total,
            estado=estado,
            fecha_solicitud=fecha_solicitud,
            fecha_creacion=ahora,
            fecha_actualizacion=ahora
        )
        reembolso.save(force_insert=True)
        messages.success(request, 'Reembolso creado correctamente.')
        return redirect('reembolsos_list')

    return render(request, 'reembolso_form.html', {'usuarios': usuarios, 'accion': 'Crear'})


def reembolso_edit(request, id_reembolso):
    reembolso = get_object_or_404(Reembolsos, id_reembolso=id_reembolso)
    usuarios = Usuarios.objects.all()
    if request.method == 'POST':
        reembolso.id_usuario = Usuarios.objects.get(pk=request.POST.get('id_usuario'))
        reembolso.total = request.POST.get('total')
        reembolso.estado = request.POST.get('estado')
        reembolso.fecha_solicitud = request.POST.get('fecha_solicitud')
        reembolso.fecha_actualizacion = timezone.now()
        reembolso.save(force_update=True)
        messages.success(request, 'Reembolso actualizado correctamente.')
        return redirect('reembolsos_list')

    return render(request, 'reembolso_form.html', {'reembolso': reembolso, 'usuarios': usuarios, 'accion': 'Editar'})


def reembolso_delete(request, id_reembolso):
    reembolso = get_object_or_404(Reembolsos, id_reembolso=id_reembolso)
    reembolso.delete()
    messages.success(request, 'Reembolso eliminado correctamente.')
    return redirect('reembolsos_list')


# --- Detalle_Reembolso --- #
def detalle_reembolso_list(request):
    detalles = Detalle_Reembolso.objects.select_related('id_reembolso', 'id_gasto').all().order_by('-fecha_creacion')
    return render(request, 'detalle_reembolso_list.html', {'detalles': detalles})


def detalle_reembolso_create(request):
    reembolsos = Reembolsos.objects.all()
    gastos = Gastos.objects.all()

    if request.method == 'POST':
        id_reembolso = request.POST.get('id_reembolso')
        id_gasto = request.POST.get('id_gasto')
        monto_aprobado = request.POST.get('monto_aprobado')
        comentario = request.POST.get('comentario')
        ahora = timezone.now()

        detalle = Detalle_Reembolso(
            id_reembolso=Reembolsos.objects.get(pk=id_reembolso),
            id_gasto=Gastos.objects.get(pk=id_gasto),
            monto_aprobado=monto_aprobado,
            comentario=comentario,
            fecha_creacion=ahora,
            fecha_actualizacion=ahora
        )
        detalle.save(force_insert=True)
        messages.success(request, 'Detalle de reembolso creado correctamente.')
        return redirect('detalle_reembolso_list')

    return render(request, 'detalle_reembolso_form.html', {
        'reembolsos': reembolsos,
        'gastos': gastos,
        'accion': 'Crear'
    })


def detalle_reembolso_edit(request, id_detalle):
    detalle = get_object_or_404(Detalle_Reembolso, id_detalle=id_detalle)
    reembolsos = Reembolsos.objects.all()
    gastos = Gastos.objects.all()

    if request.method == 'POST':
        detalle.id_reembolso = Reembolsos.objects.get(pk=request.POST.get('id_reembolso'))
        detalle.id_gasto = Gastos.objects.get(pk=request.POST.get('id_gasto'))
        detalle.monto_aprobado = request.POST.get('monto_aprobado')
        detalle.comentario = request.POST.get('comentario')
        detalle.fecha_actualizacion = timezone.now()
        detalle.save(force_update=True)
        messages.success(request, 'Detalle de reembolso actualizado correctamente.')
        return redirect('detalle_reembolso_list')

    return render(request, 'detalle_reembolso_form.html', {
        'detalle': detalle,
        'reembolsos': reembolsos,
        'gastos': gastos,
        'accion': 'Editar'
    })


def detalle_reembolso_delete(request, id_detalle):
    detalle = get_object_or_404(Detalle_Reembolso, id_detalle=id_detalle)
    detalle.delete()
    messages.success(request, 'Detalle de reembolso eliminado correctamente.')
    return redirect('detalle_reembolso_list')
