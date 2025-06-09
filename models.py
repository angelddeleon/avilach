from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'usuarios'  # Especificamos el nombre de la tabla en la base de datos

    id_usuario = db.Column(db.Integer, primary_key=True)  # ID del usuario
    tipo_usuario = db.Column(db.String(50), nullable=False, default= "agente")  # Tipo de usuario (admin, empleado, etc.)
    estado = db.Column(db.String(20), nullable=False)  # Estado del usuario (activo, inactivo)
    correo_usuario = db.Column(db.String(120), unique=True, nullable=False)  # Correo del usuario
    nombre = db.Column(db.String(100), nullable=False)  # Nombre del usuario
    apellidos = db.Column(db.String(100), nullable=False)  # Apellidos del usuario
    area_o_sucursal = db.Column(db.String(100), nullable=False)  # Área o sucursal del usuario
    direccion = db.Column(db.String(200), nullable=False)  # Dirección del usuario
    contrasena = db.Column(db.String(200), nullable=False)  # Contraseña del usuario (hasheada)
    telefono = db.Column(db.String(15), nullable=False)  # Teléfono del usuario
    imagen_usuario = db.Column(db.String(200), nullable=True)  # Imagen del usuario (ruta de la imagen)
    rol = db.Column(db.String(50), nullable=False, default='agente')  # Rol del usuario (por defecto 'agente')

    # Nuevas columnas para redes sociales
    facebook = db.Column(db.String(200), nullable=True)  # Enlace de Facebook (opcional)
    instagram = db.Column(db.String(200), nullable=True)  # Enlace de Instagram (opcional)
    telegram = db.Column(db.String(200), nullable=True)  # Enlace de Telegram (opcional)
    twitter = db.Column(db.String(200), nullable=True)  # Enlace de Twitter (opcional)

    def __repr__(self):
        return f"<User {self.nombre} {self.apellidos} - {self.correo_usuario}>"

    # Método para establecer una contraseña hasheada
    def set_password(self, password):
        self.contrasena = generate_password_hash(password)

    # Método para verificar la contraseña
    def check_password(self, password):
        return check_password_hash(self.contrasena, password)

class Casa(db.Model):
    __tablename__ = 'casas'

    id = db.Column(db.Integer, primary_key=True)

    # Datos personales del solicitante
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    ci = db.Column(db.String(20), nullable=False)
    rif = db.Column(db.String(20), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    estado_civil = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)

    # Datos del inmueble
   
    titulo_propiedad = db.Column(db.String(200), nullable=False)
    estado_publicacion = db.Column(db.String(50), nullable=False, default= 'Activo')
    destacado = db.Column(db.Boolean, default=False)
    tipo_inmueble = db.Column(db.String(50), nullable=False, default='Casa')
    datos_inmueble = db.Column(db.Text, nullable=True)
    referencia = db.Column(db.Text, nullable=True)

    # Habitaciones y baños
    habitaciones = db.Column(db.Integer, nullable=True)
    hab_servicio = db.Column(db.Integer, nullable=True)
    total_habitaciones = db.Column(db.Integer, nullable=True)
    banos_completos = db.Column(db.Integer, nullable=True)
    bano_servicio = db.Column(db.Integer, nullable=True)
    medio_bano = db.Column(db.Integer, nullable=True)
    total_banos = db.Column(db.Integer, nullable=True)

    # Estacionamiento
    puestos_estacionamiento = db.Column(db.Integer, nullable=True)
    estacionamientos_cubiertos = db.Column(db.Integer, nullable=True)
    estacionamientos_descubiertos = db.Column(db.Integer, nullable=True)

    # Maletero
    tiene_maletero = db.Column(db.Boolean, default=False)
    cantidad_maleteros = db.Column(db.Integer, nullable=True)

    # Dimensiones y estructura
    metros_construccion = db.Column(db.Float, nullable=True)
    metros_terreno = db.Column(db.Float, nullable=True)
    anio_construccion = db.Column(db.Integer, nullable=True)
    obra = db.Column(db.String(100), nullable=True)
    estilo = db.Column(db.String(100), nullable=True)
    tiene_terraza = db.Column(db.Boolean, default=False)
    tipo_piso = db.Column(db.String(100), nullable=True)
    niveles = db.Column(db.Integer, nullable=True)

    # Ubicación del inmueble
    pais = db.Column(db.String(100), nullable=True)
    estado_departamento = db.Column(db.String(100), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    codigo_postal = db.Column(db.String(20), nullable=True)

    # Propietario
    nombre_propietario = db.Column(db.String(100), nullable=True)
    telefono_propietario = db.Column(db.String(20), nullable=True)

    # Áreas y servicios
    areas_internas = db.Column(db.Text, nullable=True)
    areas_comunes = db.Column(db.Text, nullable=True)
    servicio_telefonia_fija = db.Column(db.Text, nullable=True)
    servicio_cable = db.Column(db.Text, nullable=True)
    servicio_internet = db.Column(db.Text, nullable=True)

    # Nueva columna comodidades
    comodidades = db.Column(db.Text, nullable=True)

    # Precio y comisión
    condominio_aprox = db.Column(db.Float, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float, nullable=True, default=False)

    # Documentación
    imagen_cedula = db.Column(db.String(300), nullable=True)  # Imagen de la cédula
    documento_propiedad = db.Column(db.String(300), nullable=True)  # PDF documento de propiedad

    # Imagen principal
    imagen_principal = db.Column(db.String(300), nullable=True)

    tipo_negocio = db.Column(db.String(50), nullable=False)

    # Nueva columna para relacionar con el agente (id_usuario)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    # Relación con la tabla de usuarios (agente)
    agente = db.relationship('User', backref='casas', lazy=True)

#modelo de los apartamentos 


class Apartamento(db.Model):
    __tablename__ = 'apartamento'

    id = db.Column(db.Integer, primary_key=True)

    # Datos del propietario
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    ci = db.Column(db.String(20), nullable=False)
    rif = db.Column(db.String(20), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    estado_civil = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)

    # Datos del inmueble
    titulo_propiedad = db.Column(db.String(200), nullable=False)
   
    estado_publicacion = db.Column(db.String(50), nullable=False, default= 'Activo')
    destacado = db.Column(db.Boolean, default=False)
    tipo_inmueble = db.Column(db.String(50), nullable=False, default='Apartamento')
    datos_inmueble = db.Column(db.Text, nullable=True)
    referencia = db.Column(db.Text, nullable=True)

    # Habitaciones y baños
    habitaciones = db.Column(db.Integer, nullable=True)
    hab_servicio = db.Column(db.Integer, nullable=True)
    total_habitaciones = db.Column(db.Integer, nullable=True)
    banos_completos = db.Column(db.Integer, nullable=True)
    bano_servicio = db.Column(db.Integer, nullable=True)
    medio_bano = db.Column(db.Integer, nullable=True)
    total_banos = db.Column(db.Integer, nullable=True)

    # Estacionamiento
    puestos_estacionamiento = db.Column(db.Integer, nullable=True)
    estacionamientos_cubiertos = db.Column(db.Integer, nullable=True)
    estacionamientos_descubiertos = db.Column(db.Integer, nullable=True)

    # Maletero
    tiene_maletero = db.Column(db.Boolean, default=False)
    cantidad_maleteros = db.Column(db.Integer, nullable=True)

    # Dimensiones y estructura
    metros_construccion = db.Column(db.Float, nullable=True)
    metros_terreno = db.Column(db.Float, nullable=True)
    anio_construccion = db.Column(db.Integer, nullable=True)
    obra = db.Column(db.String(100), nullable=True)
    estilo = db.Column(db.String(100), nullable=True)
    tiene_terraza = db.Column(db.Boolean, default=False)
    tipo_piso = db.Column(db.String(100), nullable=True)
    niveles = db.Column(db.Integer, nullable=True)

    # Ubicación del inmueble
    pais = db.Column(db.String(100), nullable=True)
    estado_departamento = db.Column(db.String(100), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    codigo_postal = db.Column(db.String(20), nullable=True)
    aptos_x_piso = db.Column(db.Integer, nullable=True)
    total_pisos = db.Column(db.Integer, nullable=True)

    # Áreas y servicios
    areas_internas = db.Column(db.Text, nullable=True)
    areas_comunes = db.Column(db.Text, nullable=True)
    servicio_telefonia_fija = db.Column(db.Text, nullable=True)
    servicio_cable = db.Column(db.Text, nullable=True)
    servicio_internet = db.Column(db.Text, nullable=True)

    # Comodidades
    comodidades = db.Column(db.Text, nullable=True)

    # Precio y comisión
    condominio_aprox = db.Column(db.Float, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float, nullable=True)

    # Documentación
    imagen_cedula = db.Column(db.String(300), nullable=True)
    documento_propiedad = db.Column(db.String(300), nullable=True)

    # Imagen principal
    imagen_principal = db.Column(db.String(300), nullable=True)

    tipo_negocio = db.Column(db.String(50), nullable=False)

     # Nueva columna para relacionar con el agente (id_usuario)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    # Relación con la tabla de usuarios (agente)
    agente = db.relationship('User', backref='apartamento', lazy=True)

# modelo del terreno 
class Terreno(db.Model):
    __tablename__ = 'terrenos'

    id = db.Column(db.Integer, primary_key=True)

    # Título del inmueble
    titulo_publicacion = db.Column(db.String(200), nullable=False)  # Título de la publicación
    estado_publicacion = db.Column(db.String(20), nullable=False, default="Activo")  # Estado de publicación
    tipo_inmueble = db.Column(db.String(50), nullable=False, default="Terreno")  # Tipo de inmueble

    # Datos del propietario
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    ci = db.Column(db.String(20), nullable=False)
    rif = db.Column(db.String(20), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    estado_civil = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)

    # Datos del inmueble (Terreno)
    estado = db.Column(db.String(100), nullable=False)
    municipio = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    urbanizacion = db.Column(db.String(100), nullable=True)
    referencia = db.Column(db.String(200), nullable=True)

    # Detalles del terreno
    m2_terreno = db.Column(db.Float, nullable=False)
    m2_construccion = db.Column(db.Float, nullable=True)
    m_frente = db.Column(db.Float, nullable=True)
    m_anch = db.Column(db.Float, nullable=True)
    m_largo = db.Column(db.Float, nullable=True)

    # Características (checkboxes como texto separado por comas)
    vias_acceso = db.Column(db.String(200), nullable=True)
    formas_terreno = db.Column(db.String(200), nullable=True)
    conj_cerrado = db.Column(db.Boolean, default=False)
    calle_publica = db.Column(db.Boolean, default=False)
    cerco_electrico = db.Column(db.Boolean, default=False)
    vigilancia = db.Column(db.Boolean, default=False)
    pozo_agua = db.Column(db.Boolean, default=False)
    plantas_arboles_frutales = db.Column(db.Boolean, default=False)

    # Zonificación (checkboxes como texto separado por comas)
    zonificacion = db.Column(db.String(200), nullable=True)

    servicios_basicos = db.Column(db.String(200), nullable=True)  # O db.Text si es más largo

    # Servicios básicos (checkboxes como texto separado por comas)
    aguas_blancas = db.Column(db.Boolean, default=False)
    electricidad = db.Column(db.Boolean, default=False)
    aguas_negras = db.Column(db.Boolean, default=False)
    alta_tension = db.Column(db.Boolean, default=False)
    baja_tension = db.Column(db.Boolean, default=False)

    # Descripción y Observaciones
    descripcion = db.Column(db.Text, nullable=True)
    observaciones = db.Column(db.Text, nullable=True)

    # Documentos
    imagen_cedula = db.Column(db.String(300), nullable=True)
    documento_propiedad = db.Column(db.String(300), nullable=True)

    # Imagen principal
    imagen_principal = db.Column(db.String(300), nullable=True)

    # Precio y comisión
    precio = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float, nullable=True)

    # Nuevos campos que has solicitado
    m2_terreno = db.Column(db.Float, nullable=False)
    m2_construccion = db.Column(db.Float, nullable=True)
    m_frente = db.Column(db.Float, nullable=True)
    m_anch = db.Column(db.Float, nullable=True)
    m_largo = db.Column(db.Float, nullable=True)
    cerca_perimetral = db.Column(db.String(100), nullable=True)
    bienechurias = db.Column(db.String(100), nullable=True)
    otros = db.Column(db.String(100), nullable=True)
    materiales = db.Column(db.String(200), nullable=True) 

    tipo_negocio = db.Column(db.String(50), nullable=False)

    # Nueva columna para relacionar con el agente (id_usuario)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    # Relación con la tabla de usuarios (agente)
    agente = db.relationship('User', backref='terrenos', lazy=True)

    def __repr__(self):
        return f"<Terreno {self.titulo_publicacion} - {self.tipo_inmueble}>"
    
    #modelo para galpones 

class Galpon(db.Model):
    __tablename__ = 'galpones'

    id = db.Column(db.Integer, primary_key=True)

    # Datos del propietario
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    ci = db.Column(db.String(20), nullable=False)
    rif = db.Column(db.String(20), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    estado_civil = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)

    # Datos del galpón
    titulo_propiedad = db.Column(db.String(200), nullable=False)
    estado_publicacion = db.Column(db.String(20), nullable=False, default="Activo") 
    destacado = db.Column(db.Boolean, default=False)
    tipo_inmueble = db.Column(db.String(50), nullable=False, default='Galpón')
    datos_inmueble = db.Column(db.Text, nullable=True)
    referencia = db.Column(db.Text, nullable=True)

    # Características específicas del galpón
    oficinas = db.Column(db.Integer, nullable=True)
    galpon = db.Column(db.String(50), nullable=True)
    banos_completos = db.Column(db.Integer, nullable=True)
    banos_servicio = db.Column(db.Integer, nullable=True)
    medio_bano = db.Column(db.Integer, nullable=True)
    area_descanso = db.Column(db.String(50), nullable=True)
    puestos_estacionamiento = db.Column(db.Integer, nullable=True)
    cubierto = db.Column(db.String(50), nullable=True)
    amoblado = db.Column(db.String(50), nullable=True)
    kitchenette = db.Column(db.String(50), nullable=True)
    patio_trabajo = db.Column(db.String(50), nullable=True)
    m_frente = db.Column(db.Float, nullable=True)
    total_banos = db.Column(db.Integer, nullable=True)
    descubierto = db.Column(db.String(50), nullable=True)
    vigilancia = db.Column(db.String(50), nullable=True)
    m_fondo = db.Column(db.Float, nullable=True)
    galpon_compartido = db.Column(db.String(50), nullable=True)
    estacionamiento_visitantes = db.Column(db.String(50), nullable=True)
    m_altura = db.Column(db.Float, nullable=True)
    centro_comercial = db.Column(db.String(50), nullable=True)
    m2_terreno = db.Column(db.Float, nullable=True)
    anos_construccion = db.Column(db.Integer, nullable=True)
    parque_industrial = db.Column(db.String(50), nullable=True)
    m2_construccion = db.Column(db.Float, nullable=True)
    condominio_aprox = db.Column(db.Float, nullable=True)
    pie_de_calle = db.Column(db.String(50), nullable=True, default="No" )

    # Ubicación del galpón
    pais = db.Column(db.String(100), nullable=True)
    estado_departamento = db.Column(db.String(100), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    codigo_postal = db.Column(db.String(20), nullable=True)

    # Documentación
    imagen_cedula = db.Column(db.String(300), nullable=True)  # Imagen de la cédula
    documento_propiedad = db.Column(db.String(300), nullable=True)  # Documento propiedad

    # Imagen principal
    imagen_principal = db.Column(db.String(300), nullable=True)

    # Áreas internas (checkboxes)
    areas_internas = db.Column(db.String(500), nullable=True)

    # Comodidades (checkboxes)
    comodidades = db.Column(db.String(500), nullable=True)

    # Servicio de telefonía fija (checkboxes)
    servicio_telefonia_fija = db.Column(db.String(500), nullable=True)

    # Servicio de cable (checkboxes)
    servicio_cable = db.Column(db.String(500), nullable=True)

    # Servicio de internet (checkboxes)
    servicio_internet = db.Column(db.String(500), nullable=True)

    # Nuevos campos de precio y comisión
    precio = db.Column(db.Float, nullable=False)  # El precio del galpón
    comision = db.Column(db.Float, nullable=True)  # La comisión asociada al galpón

     # Dirección del Comercio
    pais = db.Column(db.String(100), nullable=True)
    estado_departamento = db.Column(db.String(100), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    codigo_postal = db.Column(db.String(20), nullable=True)

    tipo_negocio = db.Column(db.String(50), nullable=False)

# Nueva columna para relacionar con el agente (id_usuario)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    # Relación con la tabla de usuarios (agente)
    agente = db.relationship('User', backref='galpones', lazy=True)



    def __repr__(self):
        return f"<Galpon {self.titulo_propiedad}>"

#modelo para local 

class Local(db.Model):
    __tablename__ = 'locales'

    id = db.Column(db.Integer, primary_key=True)

    # Datos del propietario
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    ci = db.Column(db.String(20), nullable=False)
    rif = db.Column(db.String(20), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    estado_civil = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)

    # Datos del galpón
    titulo_propiedad = db.Column(db.String(200), nullable=False)
    estado_publicacion = db.Column(db.String(20), nullable=False, default="Activo") 
    destacado = db.Column(db.Boolean, default=False)
    tipo_inmueble = db.Column(db.String(50), nullable=False, default='Galpón')
    datos_inmueble = db.Column(db.Text, nullable=True)
    referencia = db.Column(db.Text, nullable=True)

    # Características específicas del galpón
    banos_completos = db.Column(db.Integer, nullable=True)
    banos_servicio = db.Column(db.Integer, nullable=True)
    medio_bano = db.Column(db.Integer, nullable=True)
    area_descanso = db.Column(db.String(50), nullable=True)
    puestos_estacionamiento = db.Column(db.Integer, nullable=True)
    cubierto = db.Column(db.String(50), nullable=True)
    amoblado = db.Column(db.String(50), nullable=True)
    patio_trabajo = db.Column(db.String(50), nullable=True)
    m_frente = db.Column(db.Float, nullable=True)
    total_banos = db.Column(db.Integer, nullable=True)
    descubierto = db.Column(db.String(50), nullable=True)
    vigilancia = db.Column(db.String(50), nullable=True)
    m_fondo = db.Column(db.Float, nullable=True)
    estacionamiento_visitantes = db.Column(db.String(50), nullable=True)
    m_altura = db.Column(db.Float, nullable=True)
    m2_terreno = db.Column(db.Float, nullable=True)
    anos_construccion = db.Column(db.Integer, nullable=True)
    parque_industrial = db.Column(db.String(50), nullable=True)
    m2_construccion = db.Column(db.Float, nullable=True)
    condominio_aprox = db.Column(db.Float, nullable=True)
    pie_de_calle = db.Column(db.String(50), nullable=True, default="No" )

    # Ubicación del galpón
    pais = db.Column(db.String(100), nullable=True)
    estado_departamento = db.Column(db.String(100), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    codigo_postal = db.Column(db.String(20), nullable=True)

    # Documentación
    imagen_cedula = db.Column(db.String(300), nullable=True)  # Imagen de la cédula
    documento_propiedad = db.Column(db.String(300), nullable=True)  # Documento propiedad

    # Imagen principal
    imagen_principal = db.Column(db.String(300), nullable=True)

    # Áreas internas (checkboxes)
    areas_internas = db.Column(db.String(500), nullable=True)

    # Comodidades (checkboxes)
    comodidades = db.Column(db.String(500), nullable=True)

    # Servicio de telefonía fija (checkboxes)
    servicio_telefonia_fija = db.Column(db.String(500), nullable=True)

    # Servicio de cable (checkboxes)
    servicio_cable = db.Column(db.String(500), nullable=True)

    # Servicio de internet (checkboxes)
    servicio_internet = db.Column(db.String(500), nullable=True)

    # Nuevos campos de precio y comisión
    precio = db.Column(db.Float, nullable=False)  # El precio del galpón
    comision = db.Column(db.Float, nullable=True)  # La comisión asociada al galpón

     # Dirección del Comercio
    pais = db.Column(db.String(100), nullable=True)
    estado_departamento = db.Column(db.String(100), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    codigo_postal = db.Column(db.String(20), nullable=True)

    tipo_negocio = db.Column(db.String(50), nullable=False)

    # Nueva columna para relacionar con el agente (id_usuario)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    # Relación con la tabla de usuarios (agente)
    agente = db.relationship('User', backref='locales', lazy=True)

    def __repr__(self):
        return f"<Local {self.titulo_propiedad}>"
    
#ruta para comercio 
class Comercio(db.Model):

    __tablename__ = 'comercios'
    id = db.Column(db.Integer, primary_key=True)
    titulo_propiedad = db.Column(db.String(100), nullable=False)
    estado_publicacion = db.Column(db.String(20), nullable=False, default="Activo") 
    destacado = db.Column(db.Boolean, nullable=False)
    tipo_inmueble = db.Column(db.String(50), nullable=False)
    datos_inmueble = db.Column(db.Text)
    referencia = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float)

    # Datos del Comercio
    oficinas = db.Column(db.Integer)
    ambientes = db.Column(db.Integer)
    banos_completos = db.Column(db.Integer)
    medio_bano = db.Column(db.Integer)
    bano_servicio = db.Column(db.Integer)
    total_banos = db.Column(db.Integer)
    galpon = db.Column(db.String(50))
    area_descanso = db.Column(db.String(50))
    puestos_estacionamiento = db.Column(db.Integer)
    cubierto = db.Column(db.String(50))
    descubierto = db.Column(db.String(50))
    estacionamiento_visitantes = db.Column(db.String(50))
    amoblado = db.Column(db.String(50))
    m_frente = db.Column(db.Float)
    m_fondo = db.Column(db.Float)
    m_altura = db.Column(db.Float)
    m2_terreno = db.Column(db.Float)
    anos_construccion = db.Column(db.Integer)
    m2_construccion = db.Column(db.Float)
    condominio_aprox = db.Column(db.Float)
    razon_social = db.Column(db.String(100))
    objeto = db.Column(db.String(50))
    anio_apertura = db.Column(db.Integer)
    punto_venta = db.Column(db.Boolean)
    maquinas_equipos = db.Column(db.Boolean)
    mobiliario = db.Column(db.Boolean)
    lineas_telefonicas = db.Column(db.Boolean)
    rrss_activas = db.Column(db.Boolean)
    sistema_fiscal = db.Column(db.Boolean)
    pag_web_activa = db.Column(db.Boolean)
    contabilidad = db.Column(db.Boolean)

    # Áreas internas, comodidades, telefonía fija, cable, internet
    areas_internas = db.Column(db.String(500))
    comodidades = db.Column(db.String(500))
    telefonia = db.Column(db.String(500))
    cablevision = db.Column(db.String(500))
    internet = db.Column(db.String(500))

     # Documentación
    imagen_cedula = db.Column(db.String(300), nullable=True)  # Imagen de la cédula
    documento_propiedad = db.Column(db.String(300), nullable=True)  # Documento propiedad

    # Imagen principal
    imagen_principal = db.Column(db.String(300), nullable=True)

     # Datos del propietario
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    ci = db.Column(db.String(20), nullable=False)
    rif = db.Column(db.String(20), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    estado_civil = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)

     # Dirección del Comercio
    pais = db.Column(db.String(100), nullable=True)
    estado_departamento = db.Column(db.String(100), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    codigo_postal = db.Column(db.String(20), nullable=True)

    tipo_negocio = db.Column(db.String(50), nullable=False)

     # Nueva columna para relacionar con el agente (id_usuario)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    # Relación con la tabla de usuarios (agente)
    agente = db.relationship('User', backref='comercios', lazy=True)



    def __repr__(self):
        return f'<Comercio {self.titulo_propiedad}>'
    

#modelo de la agenda

class Agenda(db.Model):
    __tablename__ = 'agenda'

    # Campos de la tabla
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)

    def __init__(self, titulo, fecha_inicio, fecha_fin):
        self.titulo = titulo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin

    def __repr__(self):
        return f'<Agenda {self.titulo}, {self.fecha_inicio} - {self.fecha_fin}>'
    
#modelo de las notificaciones

class Notificaciones(db.Model):
    __tablename__ = 'notificaciones'

    # Campos de la tabla
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, titulo, fecha=None):
        self.titulo = titulo
        if fecha is not None:
            self.fecha = fecha
        else:
            self.fecha = datetime.utcnow()

    def __repr__(self):
        return f'<Notificacion {self.titulo}, {self.fecha}>'
    
#noticias 
class Noticias(db.Model):
    __tablename__ = 'noticias'

    # Definimos las columnas de la tabla
    id = db.Column(db.Integer, primary_key=True)  # Columna de ID, clave primaria
    titulo = db.Column(db.String(255), nullable=False)  # Título de la noticia
    link = db.Column(db.String(255), nullable=False)  # Enlace de la noticia
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Fecha de la noticia, por defecto la fecha actual

    def __repr__(self):
        return f'<Noticia {self.titulo}, {self.fecha}>'
    
class EventoDelMedio(db.Model):
    __tablename__ = 'eventos_del_medio'

    # Campos de la tabla
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    ubicacion = db.Column(db.String(255), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<EventoDelMedio {self.titulo}, {self.fecha_hora}>'
    
#modelo de los  

class Talleres(db.Model):
    __tablename__ = 'talleres'

    # Definimos las columnas de la tabla
    id = db.Column(db.Integer, primary_key=True)  # Columna ID, clave primaria
    titulo = db.Column(db.String(255), nullable=False)  # Título del taller
    ubicacion = db.Column(db.String(255), nullable=False)  # Ubicación del taller
    fecha_hora = db.Column(db.DateTime, nullable=False)

#modelos de los vendidos 
class Vendidos(db.Model):
    __tablename__ = 'vendidos'

    id = db.Column(db.Integer, primary_key=True)

    # Datos del inmueble vendido
    id_del_inmueble = db.Column(db.Integer, nullable=False)
    tipo_inmueble = db.Column(db.String(50), nullable=False)

    # Datos del comprador
    comprador = db.Column(db.String(255), nullable=False)
    correo_comprador = db.Column(db.String(255), nullable=False)

    # Datos del vendedor (Realtor)
    realtor_vendedor = db.Column(db.String(255), nullable=False)

    # Valor de la comisión
    valor_comision = db.Column(db.Float, nullable=False)

    # Precio de la propiedad
    precio_propiedad = db.Column(db.Float, nullable=False)

    # Fecha de la venta
    fecha_venta = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Vendido {self.id_del_inmueble} - {self.comprador}>"

#modelo de los alquilados 

class Alquilados(db.Model):
    __tablename__ = 'alquilados'

    id = db.Column(db.Integer, primary_key=True)

    # Datos del inmueble alquilado
    id_del_inmueble = db.Column(db.Integer, nullable=False)
    tipo_inmueble = db.Column(db.String(50), nullable=False)

    # Datos del arrendatario
    arrendatario = db.Column(db.String(255), nullable=False)
    correo_arrendatario = db.Column(db.String(255), nullable=False)

    # Datos del vendedor (Realtor)
    realtor_vendedor = db.Column(db.String(255), nullable=False)

    #precio del alquiler
    precio_alquiler = db.Column(db.Float, nullable=False)

    # Valor de la comisión
    valor_comision = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Alquilado {self.id_del_inmueble} - {self.arrendatario}>"

# modelo para las negociaciones 
class Negociacion(db.Model):
    __tablename__ = 'negociacion'

    id = db.Column(db.Integer, primary_key=True)  # ID de la negociación
    id_inmueble = db.Column(db.Integer, nullable=False)  # ID del inmueble negociado
    tipo_inmueble = db.Column(db.String(50), nullable=False)  # Tipo de inmueble (Casa, Apartamento, etc.)
    monto = db.Column(db.Float, nullable=False)  # Monto de la negociación
    cliente = db.Column(db.String(255), nullable=False)  # Cliente que realiza la negociación
    realtor = db.Column(db.String(255), nullable=False)  # Agente inmobiliario
    descripcion = db.Column(db.Text, nullable=True)  # Descripción o detalles adicionales

    def __repr__(self):
        return f"<Negociacion {self.id_inmueble} - {self.cliente} - {self.monto}>"