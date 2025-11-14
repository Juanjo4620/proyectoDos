from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .models import Venta

def reporte_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'

    p = canvas.Canvas(response)
    p.drawString(200, 800, "Reporte de Ventas")
    y = 750
    ventas = Venta.objects.all()
    for v in ventas:
        p.drawString(100, y, f"{v.fecha} - {v.producto.nombre} - {v.cantidad} - ${v.total()}")
        y -= 20
    p.showPage()
    p.save()
    return response
