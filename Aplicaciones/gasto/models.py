from django.db import models

class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)  # clave primaria explícita
    nombre = models.CharField(max_length=100)
    correo = models.CharField(max_length=100)
    departamento = models.CharField(max_length=50)
    fecha_registro = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'usuarios'  # nombre de tabla en minusculas
        managed = False
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.nombre


class Categorias(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255)
    estado = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'categorias'  # Coloca en minúsculas tal cual la tabla en la DB
        managed = False
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


from django.db import models

class Gastos(models.Model):
    id_gasto = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey('Usuarios', db_column='id_usuario', on_delete=models.CASCADE)
    id_categoria = models.ForeignKey('Categorias', db_column='id_categoria', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_gasto = models.DateField()
    descripcion = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'gastos'  # en minúsculas por convención DB
        managed = False
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'

    def __str__(self):
        return f'{self.descripcion} - {self.monto}'


from django.db import models

class Documentos(models.Model):
    id_documento = models.AutoField(primary_key=True)
    id_gasto = models.ForeignKey('Gastos', db_column='id_gasto', on_delete=models.CASCADE)
    nombre_archivo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20)
    ruta_archivo = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'documentos'
        managed = False
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return self.nombre_archivo


from django.db import models

class Reembolsos(models.Model):
    id_reembolso = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey('Usuarios', db_column='id_usuario', on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20)
    fecha_solicitud = models.DateField()
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'reembolsos'
        managed = False
        verbose_name = 'Reembolso'
        verbose_name_plural = 'Reembolsos'

    def __str__(self):
        return f'Reembolso {self.id_reembolso} - {self.estado}'


from django.db import models

class Detalle_Reembolso(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_reembolso = models.ForeignKey('Reembolsos', db_column='id_reembolso', on_delete=models.CASCADE)
    id_gasto = models.ForeignKey('Gastos', db_column='id_gasto', on_delete=models.CASCADE)
    monto_aprobado = models.DecimalField(max_digits=10, decimal_places=2)
    comentario = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'detalle_reembolso'
        managed = False
        verbose_name = 'Detalle de Reembolso'
        verbose_name_plural = 'Detalles de Reembolso'

    def __str__(self):
        return f'Detalle {self.id_detalle} - Reembolso {self.id_reembolso.id_reembolso}'
