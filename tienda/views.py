from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission
from django.db.models import Sum, F, DecimalField, Q
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from .models import Venta, Producto, Categoria, CarritoItem
from datetime import date, datetime, timedelta
from django.utils.dateparse import parse_date
import json
from django.db.models import Q as Qfilter

# Importar para PDF
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def check_permission(user, permission_codename):
    """
    Verifica si un usuario tiene un permiso específico
    """
    return user.has_perm(f'tienda.{permission_codename}')

def logout_view(request):
    """Vista de logout que acepta GET y POST"""
    logout(request)
    return redirect('login')

def signup(request):
    """Vista de registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('tienda:home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Autenticar e iniciar sesión automáticamente
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=raw_password)
            if user is not None:
                # Asignar permiso básico para ver ventas al usuario nuevo
                try:
                    perm = Permission.objects.get(codename='view_venta', content_type__app_label='tienda')
                    user.user_permissions.add(perm)
                except Permission.DoesNotExist:
                    # Si no existe el permiso, continuar sin fallo (se puede asignar desde admin)
                    pass
                login(request, user)
                # Forzar recarga de permisos en la sesión (evitar caches de permisos)
                try:
                    if hasattr(request.user, '_perm_cache'):
                        del request.user._perm_cache
                except Exception:
                    pass
                return redirect('tienda:home')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

@login_required
def home(request):
    """Vista principal del sistema"""
    context = {
        'usuario': request.user,
        'puede_ver_reportes': check_permission(request.user, 'view_sales_reports'),
        'puede_exportar': check_permission(request.user, 'export_sales_reports'),
    }
    return render(request, 'home.html', context)


@login_required
def catalogo(request):
    """Listado público (para usuarios autenticados) de productos - catálogo"""
    productos = Producto.objects.select_related('categoria').all()
    categorias = Categoria.objects.all()

    # Filtros simples: categoría y búsqueda por nombre
    categoria_id = request.GET.get('categoria')
    q = request.GET.get('q', '').strip()

    if categoria_id:
        productos = productos.filter(categoria__id=categoria_id)

    if q:
        productos = productos.filter(Qfilter(nombre__icontains=q) | Qfilter(categoria__nombre__icontains=q))

    return render(request, 'catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'q': q,
        'categoria_seleccionada': categoria_id,
    })

@login_required
@permission_required('tienda.view_venta', raise_exception=True)
def ventas(request):
    """Lista todas las ventas con filtros opcionales"""
    ventas = Venta.objects.select_related('producto', 'producto__categoria', 'vendedor').all()
    categorias = Categoria.objects.all()
    
    # Filtros
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')
    categoria = request.GET.get('categoria')
    producto = request.GET.get('producto')
    
    filtros_activos = {}
    
    if fecha_inicio:
        try:
            fecha_inicio_parsed = parse_date(fecha_inicio)
            ventas = ventas.filter(fecha__gte=fecha_inicio_parsed)
            filtros_activos['inicio'] = fecha_inicio
        except:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_parsed = parse_date(fecha_fin)
            ventas = ventas.filter(fecha__lte=fecha_fin_parsed)
            filtros_activos['fin'] = fecha_fin
        except:
            pass
    
    if categoria:
        ventas = ventas.filter(producto__categoria_id=categoria)
        filtros_activos['categoria'] = categoria
    
    if producto:
        ventas = ventas.filter(producto__id=producto)
        filtros_activos['producto'] = producto
    
    # Cálculos
    total_ventas = ventas.count()
    ingreso_total = sum(float(v.total()) for v in ventas) if ventas.exists() else 0
    promedio_por_venta = ingreso_total / total_ventas if total_ventas > 0 else 0
    
    productos = Producto.objects.all()
    
    return render(request, 'ventas.html', {
        'ventas': ventas,
        'categorias': categorias,
        'productos': productos,
        'total': ingreso_total,
        'cantidad_ventas': total_ventas,
        'promedio_venta': promedio_por_venta,
        'filtros': filtros_activos,
    })

@login_required
@permission_required('tienda.view_sales_reports', raise_exception=True)
def reporte_ventas(request):
    """
    Vista de reportes de ventas con filtros avanzados
    Soporta visualización web y descarga PDF
    """
    ventas = Venta.objects.select_related('producto', 'producto__categoria', 'vendedor').all()
    categorias = Categoria.objects.all()
    productos = Producto.objects.all()
    
    # Parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    producto = request.GET.get('producto', '').strip()
    formato = request.GET.get('formato', 'web').strip()  # web o pdf
    
    # Aplicar filtros
    filtros_activos = {}
    
    if fecha_inicio:
        try:
            fecha_inicio_parsed = parse_date(fecha_inicio)
            if fecha_inicio_parsed:
                ventas = ventas.filter(fecha__gte=fecha_inicio_parsed)
                filtros_activos['fecha_inicio'] = fecha_inicio
        except:
            fecha_inicio = None
    
    if fecha_fin:
        try:
            fecha_fin_parsed = parse_date(fecha_fin)
            if fecha_fin_parsed:
                ventas = ventas.filter(fecha__lte=fecha_fin_parsed)
                filtros_activos['fecha_fin'] = fecha_fin
        except:
            fecha_fin = None
    
    if categoria:
        try:
            cat_id = int(categoria)
            ventas = ventas.filter(producto__categoria_id=cat_id)
            filtros_activos['categoria'] = categoria
        except (ValueError, TypeError):
            pass
    
    if producto:
        try:
            prod_id = int(producto)
            ventas = ventas.filter(producto_id=prod_id)
            filtros_activos['producto'] = producto
        except (ValueError, TypeError):
            pass
    
    # Cálculos agregados
    total_ventas_count = ventas.count()
    ingreso_total = sum(float(v.total()) for v in ventas) if ventas.exists() else 0
    cantidad_productos = ventas.values('producto').distinct().count() if ventas.exists() else 0
    
    datos_reporte = {
        'total_ventas': total_ventas_count,
        'ingreso_total': ingreso_total,
        'cantidad_productos': cantidad_productos,
        'vendedor_top': None,
    }
    
    if ventas.exists():
        vendedor_stats = ventas.values('vendedor__username').annotate(
            cantidad=Sum('cantidad')
        ).order_by('-cantidad').first()
        if vendedor_stats:
            datos_reporte['vendedor_top'] = vendedor_stats['vendedor__username']
    
    # Agrupar por categoría
    reporte_categorias = []
    for cat in categorias:
        ventas_cat = ventas.filter(producto__categoria=cat)
        if ventas_cat.exists():
            ingreso_cat = sum(float(v.total()) for v in ventas_cat)
            reporte_categorias.append({
                'categoria': cat,
                'cantidad': ventas_cat.count(),
                'ingreso': ingreso_cat,
                'promedio': ingreso_cat / ventas_cat.count() if ventas_cat.count() > 0 else 0,
            })
    
    # Si es PDF, generar descarga
    if formato == 'pdf':
        if not check_permission(request.user, 'export_sales_reports'):
            return redirect('tienda:reporte_ventas')
        return generar_pdf_reporte(ventas, datos_reporte, reporte_categorias, filtros_activos)
    
    context = {
        'ventas': ventas,
        'categorias': categorias,
        'productos': productos,
        'datos_reporte': datos_reporte,
        'reporte_categorias': reporte_categorias,
        'filtros': filtros_activos,
        'puede_exportar': check_permission(request.user, 'export_sales_reports'),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'reportes/reporte_ventas.html', context)

def generar_pdf_reporte(ventas, datos_reporte, reporte_categorias, filtros):
    """
    Genera un PDF con el reporte de ventas
    """
    if not REPORTLAB_AVAILABLE:
        return HttpResponse(
            "ReportLab no está instalado. Instálalo con: pip install reportlab",
            status=400
        )
    
    try:
        # Crear respuesta HTTP
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        
        # Crear PDF
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2e5090'),
            spaceAfter=12,
            spaceBefore=12,
        )
        
        # Título
        titulo = Paragraph("REPORTE DE VENTAS", title_style)
        elements.append(titulo)
        
        # Información de filtros
        fecha_reporte = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        info_filtros = f"Generado: {fecha_reporte}"
        if filtros and any(filtros.values()):
            info_filtros += " | Filtros aplicados:"
            if filtros.get('fecha_inicio'):
                info_filtros += f" Desde {filtros['fecha_inicio']}"
            if filtros.get('fecha_fin'):
                info_filtros += f" Hasta {filtros['fecha_fin']}"
            if filtros.get('categoria'):
                info_filtros += f" Categoría: {filtros['categoria']}"
        
        elements.append(Paragraph(info_filtros, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Resumen general
        elements.append(Paragraph("RESUMEN GENERAL", heading_style))
        
        try:
            ingreso_total = float(datos_reporte.get('ingreso_total', 0))
            total_ventas = int(datos_reporte.get('total_ventas', 0))
            cantidad_productos = int(datos_reporte.get('cantidad_productos', 0))
            vendedor_top = datos_reporte.get('vendedor_top') or 'N/A'
        except (ValueError, TypeError):
            ingreso_total = 0
            total_ventas = 0
            cantidad_productos = 0
            vendedor_top = 'N/A'
        
        datos_resumen = [
            ['Métrica', 'Valor'],
            ['Total de Ventas', str(total_ventas)],
            ['Ingreso Total', f"${ingreso_total:.2f}"],
            ['Cantidad de Productos', str(cantidad_productos)],
            ['Vendedor Top', str(vendedor_top)],
        ]
        
        tabla_resumen = Table(datos_resumen, colWidths=[3*inch, 2*inch])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(tabla_resumen)
        elements.append(Spacer(1, 0.3*inch))
        
        # Reporte por categoría
        if reporte_categorias and len(reporte_categorias) > 0:
            elements.append(Paragraph("VENTAS POR CATEGORÍA", heading_style))
            
            datos_categorias = [
                ['Categoría', 'Cantidad', 'Ingreso Total', 'Promedio'],
            ]
            
            for item in reporte_categorias:
                try:
                    datos_categorias.append([
                        str(item['categoria'].nombre),
                        str(item['cantidad']),
                        f"${float(item['ingreso']):.2f}",
                        f"${float(item['promedio']):.2f}",
                    ])
                except (ValueError, KeyError, TypeError):
                    continue
            
            if len(datos_categorias) > 1:  # Si hay más que el encabezado
                tabla_categorias = Table(datos_categorias, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
                tabla_categorias.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(tabla_categorias)
        
        # Construir PDF
        doc.build(elements)
        return response
    
    except Exception as e:
        return HttpResponse(
            f"Error al generar PDF: {str(e)}",
            status=500
        )

@login_required
@permission_required('tienda.view_sales_reports', raise_exception=True)
def reporte_por_categoria(request):
    """Reporte detallado por categoría"""
    categorias = Categoria.objects.all()
    categoria_id = request.GET.get('categoria')
    
    reporte_datos = []
    
    for cat in categorias:
        ventas = Venta.objects.filter(producto__categoria=cat)
        if ventas.exists():
            reporte_datos.append({
                'categoria': cat,
                'total_ventas': ventas.count(),
                'ingreso': sum(float(v.total()) for v in ventas),
                'productos': Producto.objects.filter(categoria=cat).count(),
            })
    
    return render(request, 'reportes/reporte_categorias.html', {
        'reporte': reporte_datos,
        'categorias': categorias,
        'puede_exportar': check_permission(request.user, 'export_sales_reports'),
    })

@login_required
def reporte_por_producto(request):
    """Reporte detallado por producto"""
    productos = Producto.objects.all()
    
    reporte_datos = []
    
    for prod in productos:
        ventas = Venta.objects.filter(producto=prod)
        if ventas.exists():
            ingreso_total = sum(float(v.total()) for v in ventas)
            cantidad_ventas = ventas.count()
            ingreso_promedio = ingreso_total / cantidad_ventas if cantidad_ventas > 0 else 0
            reporte_datos.append({
                'producto': prod,
                'total_ventas': cantidad_ventas,
                'ingreso': ingreso_total,
                'cantidad_vendida': sum(v.cantidad for v in ventas),
                'ingreso_promedio': ingreso_promedio,
            })
    
    return render(request, 'reportes/reporte_productos.html', {
        'reporte': reporte_datos,
        'productos': productos,
        'puede_exportar': check_permission(request.user, 'export_sales_reports'),
    })

@login_required
def carrito(request):
    """Vista del carrito de compras"""
    items = CarritoItem.objects.filter(usuario=request.user).select_related('producto')
    total = sum(float(item.subtotal()) for item in items) if items.exists() else 0
    
    return render(request, 'carrito.html', {
        'items': items,
        'total': total,
    })

@login_required
@require_http_methods(['POST'])
def agregar_carrito(request):
    """Agregar un producto al carrito"""
    producto_id = request.POST.get('producto_id')
    cantidad = int(request.POST.get('cantidad', 1))
    
    try:
        producto = Producto.objects.get(id=producto_id)
        
        # Verificar stock
        if cantidad > producto.stock:
            cantidad = producto.stock
        
        # Obtener o crear item del carrito
        item, created = CarritoItem.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults={'cantidad': cantidad}
        )
        
        if not created:
            # Si el item ya existe, aumentar cantidad
            item.cantidad += cantidad
            if item.cantidad > producto.stock:
                item.cantidad = producto.stock
            item.save()
        
        return redirect('tienda:carrito')
    except Producto.DoesNotExist:
        return redirect('tienda:productos')

@login_required
@require_http_methods(['POST'])
def eliminar_carrito(request, item_id):
    """Eliminar un item del carrito"""
    item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    item.delete()
    return redirect('tienda:carrito')

@login_required
@require_http_methods(['POST'])
def actualizar_cantidad(request, item_id):
    """Actualizar cantidad de un item en el carrito"""
    cantidad = int(request.POST.get('cantidad', 1))
    item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    
    if cantidad > 0 and cantidad <= item.producto.stock:
        item.cantidad = cantidad
        item.save()
    elif cantidad <= 0:
        item.delete()
    
    return redirect('tienda:carrito')

@login_required
@require_http_methods(['POST'])
def procesar_compra(request):
    """Procesar la compra: crear ventas y limpiar carrito"""
    items = CarritoItem.objects.filter(usuario=request.user).select_related('producto')
    
    if not items.exists():
        return redirect('tienda:carrito')
    
    # Crear ventas por cada item del carrito
    for item in items:
        # Verificar stock disponible
        if item.cantidad <= item.producto.stock:
            Venta.objects.create(
                producto=item.producto,
                cantidad=item.cantidad,
                vendedor=request.user
            )
            # Reducir stock del producto
            item.producto.stock -= item.cantidad
            item.producto.save()
    
    # Limpiar carrito
    items.delete()
    
    return redirect('tienda:compra_exitosa')

@login_required
def compra_exitosa(request):
    """Página de confirmación de compra"""
    return render(request, 'compra_exitosa.html')
