import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, render_template, redirect, url_for, request, flash, session, Blueprint, current_app
from models import db, User, Casa, Apartamento,Negociacion, Terreno, Vendidos, Alquilados, Galpon, Local, Comercio, Agenda, Notificaciones,Talleres, Noticias,EventoDelMedio
from werkzeug.security import check_password_hash
import os
from werkzeug.utils import secure_filename
from flask import jsonify, flash
from datetime import datetime
from functools import wraps

main_routes = Blueprint('main', __name__)

# Carpetas y configuración de archivos
UPLOAD_FOLDER = 'static/imagenes/inmuebles'
ARCHIVOS_FOLDER = 'static/archivos'  # NUEVA LÍNEA
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Crear carpeta si no existe
os.makedirs(ARCHIVOS_FOLDER, exist_ok=True)  # NUEVA LÍNEA

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Función reutilizable para guardar archivos
def guardar_archivo(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        ruta = os.path.join(ARCHIVOS_FOLDER, filename)
        file.save(ruta)
        return filename  # Solo el nombre del archivo
    return None



#ruta para el login 

@main_routes.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Buscar el usuario en la base de datos utilizando 'correo_usuario'
        user = User.query.filter_by(correo_usuario=email).first()

        if user and check_password_hash(user.contrasena, password):  # Usar 'contrasena' para la verificación
            session['user_id'] = user.id_usuario  # Guarda el ID del usuario en la sesión
            flash('Inicio de sesión exitoso', 'login-success')
            
            # Verificar si el usuario es administrador o agente
            if user.rol == 'administrador':
                return redirect(url_for('main.dashboard'))  # Redirige al dashboard del administrador
            elif user.rol == 'agente':
                return redirect(url_for('main.dashboard'))  # Redirige al dashboard del agente
            else:
                flash('Rol no reconocido', 'danger')
                return redirect(url_for('main.login'))  # Redirige al login si el rol es desconocido
        else:
            flash('Credenciales inválidas', 'login-danger')

    return render_template('login.html')







@main_routes.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige al login si no hay usuario en sesión
    
    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if user.tipo_usuario == 'administrador':
        # Obtener todos los eventos de la agenda
        eventos = Agenda.query.all()

        # Convertir los eventos en el formato que FullCalendar entiende
        eventos_lista = [{
            'title': evento.titulo,
            'start': evento.fecha_inicio.isoformat(),
            'end': evento.fecha_fin.isoformat() if evento.fecha_fin else evento.fecha_inicio.isoformat()
        } for evento in eventos]

        # Obtener las 10 noticias más recientes
        noticias = Noticias.query.order_by(Noticias.fecha.desc()).limit(10).all()

        # Obtener las 5 notificaciones más recientes
        notificaciones = Notificaciones.query.order_by(Notificaciones.fecha.desc()).limit(5).all()

        # Obtener los 10 últimos talleres
        talleres = Talleres.query.order_by(Talleres.fecha_hora.desc()).limit(10).all()

        eventosdelmedio= EventoDelMedio.query.order_by(EventoDelMedio.fecha_hora.desc()).limit(10).all()

        # Renderiza el dashboard con los datos de eventos, noticias, notificaciones y talleres
        return render_template('dashboard.html', user=user, eventos=eventos_lista, 
                               notificaciones=notificaciones, noticias=noticias, 
                               talleres=talleres,medios=eventosdelmedio)
    

    elif user.tipo_usuario == 'agente':
        # Obtener todos los eventos de la agenda
        eventos = Agenda.query.all()

        # Convertir los eventos en el formato que FullCalendar entiende
        eventos_lista = [{
            'title': evento.titulo,
            'start': evento.fecha_inicio.isoformat(),
            'end': evento.fecha_fin.isoformat() if evento.fecha_fin else evento.fecha_inicio.isoformat()
        } for evento in eventos]

        # Obtener las 10 noticias más recientes
        noticias = Noticias.query.order_by(Noticias.fecha.desc()).limit(10).all()

        # Obtener las 5 notificaciones más recientes
        notificaciones = Notificaciones.query.order_by(Notificaciones.fecha.desc()).limit(5).all()

        # Obtener los 10 últimos talleres
        talleres = Talleres.query.order_by(Talleres.fecha_hora.desc()).limit(10).all()

        eventosdelmedio= EventoDelMedio.query.order_by(EventoDelMedio.fecha_hora.desc()).limit(10).all()

        # Renderiza el dashboard con los datos de eventos, noticias, notificaciones y talleres
        return render_template('dashboardagente.html', user=user, eventos=eventos_lista, 
                               notificaciones=notificaciones, noticias=noticias, 
                               talleres=talleres,medios=eventosdelmedio)
    else:
        flash('Acceso no autorizado o usuario no válido', 'danger')
        return redirect(url_for('main.login'))

"""

Apartir de aqui vienen las zonas de los inmuebñes, esta zona no se debe modificar sin hacer modificacion previa a los modelos
puesto que toda esta depende de ellos se puede causar errores agregando o quitando cualquier de los datos


"""

#crear casa 

@main_routes.route('/crear-casa', methods=['GET', 'POST'])
def crear_casa():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if request.method == 'POST':
        
            data = request.form

            tipo_negocio = data.get('tipo_negocio')

            # Procesar múltiples imágenes principales
            imagenes = []
            if 'imagenes' in request.files:
                archivos = request.files.getlist('imagenes')
                for archivo in archivos:
                    if archivo and archivo.filename:
                        filename = secure_filename(archivo.filename)
                        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        archivo.save(ruta)
                        imagenes.append(filename)  # Guardar solo el nombre del archivo

            # Guardar otras imágenes
            imagen_cedula = guardar_archivo(request.files.get('imagen_cedula'))
            documento_propiedad = guardar_archivo(request.files.get('documento_propiedad'))

            # Obtener las listas de checkboxes y convertirlas a cadenas separadas por comas
            areas_internas = ','.join(request.form.getlist('areas_internas'))
            areas_comunes = ','.join(request.form.getlist('areas_comunes'))
            comodidades = ','.join(request.form.getlist('comodidades'))
            telefonia = ','.join(request.form.getlist('telefonia'))
            cablevision = ','.join(request.form.getlist('cablevision'))
            servicios_internet = ','.join(request.form.getlist('servicios_internet'))  # Convertir a cadena separada por comas

            # Conversión segura de campos numéricos
            def safe_int(val):
                return int(val) if val not in (None, '', 'None') else None
            def safe_float(val):
                return float(val) if val not in (None, '', 'None') else None

            # Creación de la nueva casa con los datos obtenidos
            nueva_casa = Casa(
                nombre=data['nombre'],
                apellido=data['apellido'],
                ci=data['ci'],
                rif=data.get('rif'),
                fecha_nacimiento=datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d') if data.get('fecha_nacimiento') else None,
                estado_civil=data.get('estado_civil'),
                email=data['email'],
                telefono=data.get('telefono'),
        
                titulo_propiedad=data['titulo_propiedad'],
                destacado='destacado' in data,
                tipo_inmueble=data.get('tipo_inmueble', 'Casa'),
                datos_inmueble=data.get('datos_inmueble'),
                referencia=data.get('referencia'),
                habitaciones=safe_int(data.get('habitaciones')),
                hab_servicio=safe_int(data.get('hab_servicio')),
                total_habitaciones=safe_int(data.get('total_habitaciones')),
                banos_completos=safe_int(data.get('banos_completos')),
                bano_servicio=safe_int(data.get('bano_servicio')),
                medio_bano=safe_int(data.get('medio_bano')),
                total_banos=safe_int(data.get('total_banos')),
                puestos_estacionamiento=safe_int(data.get('puestos_estacionamiento')),
                estacionamientos_cubiertos=safe_int(data.get('estacionamientos_cubiertos')),
                estacionamientos_descubiertos=safe_int(data.get('estacionamientos_descubiertos')),
                tiene_maletero='tiene_maletero' in data,
                cantidad_maleteros=safe_int(data.get('cantidad_maleteros')),
                metros_construccion=safe_float(data.get('metros_construccion')),
                metros_terreno=safe_float(data.get('metros_terreno')),
                anio_construccion=safe_int(data.get('anio_construccion')),
                obra=data.get('obra'),
                estilo=data.get('estilo'),
                tiene_terraza='tiene_terraza' in data,
                tipo_piso=data.get('tipo_piso'),
                niveles=safe_int(data.get('niveles')),
                pais=data.get('pais'),
                estado_departamento=data.get('estado_departamento'),
                ciudad=data.get('ciudad'),
                direccion=data.get('direccion'),
                codigo_postal=data.get('codigo_postal'),
                areas_internas=areas_internas,
                areas_comunes=areas_comunes,
                comodidades=comodidades,
                servicio_telefonia_fija= telefonia,
                servicio_cable= cablevision,
                servicio_internet= servicios_internet,
                condominio_aprox=safe_float(data.get('condominio_aprox')),
                precio=safe_float(data['precio']),
                imagen_cedula=imagen_cedula,
                documento_propiedad=documento_propiedad,
                imagen_principal=','.join(imagenes),
                tipo_negocio = tipo_negocio,
                id_usuario=user_id
            )

            db.session.add(nueva_casa)
            db.session.commit()

            flash('Casa creada exitosamente', 'success')
            return redirect(url_for('main.dashboard'))

       

    return render_template('crear-inmueble-casa.html', user=user, casa=None)

#ruta para crear apartamentos 

@main_routes.route('/crear-apartamento', methods=['GET', 'POST'])
def crear_apartamento():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if request.method == 'POST':
        data = request.form
        tipo_negocio = data.get('tipo_negocio')
        # Procesar múltiples imágenes principales
        imagenes = []
        if 'imagenes' in request.files:
            archivos = request.files.getlist('imagenes')
            for archivo in archivos:
                if archivo and archivo.filename:
                    filename = secure_filename(archivo.filename)
                    ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    archivo.save(ruta)
                    imagenes.append(filename)  # Guardar solo el nombre del archivo
        # Guardar otras imágenes
        imagen_cedula = guardar_archivo(request.files.get('imagen_cedula'))
        documento_propiedad = guardar_archivo(request.files.get('documento_propiedad'))
        # Obtener las listas de checkboxes y convertirlas a cadenas separadas por comas
        areas_internas = ','.join(request.form.getlist('areas_internas'))
        areas_comunes = ','.join(request.form.getlist('areas_comunes'))
        comodidades = ','.join(request.form.getlist('comodidades'))
        telefonia = ','.join(request.form.getlist('telefonia'))
        cablevision = ','.join(request.form.getlist('cablevision'))
        internet = ','.join(request.form.getlist('internet'))
        # Conversión segura de campos numéricos
        def safe_int(val):
            return int(val) if val not in (None, '', 'None') else None
        def safe_float(val):
            return float(val) if val not in (None, '', 'None') else None
        nuevo_apartamento = Apartamento(
            nombre=data['nombre'],
            apellido=data['apellido'],
            ci=data['ci'],
            rif=data.get('rif'),
            fecha_nacimiento=datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d') if data.get('fecha_nacimiento') else None,
            estado_civil=data.get('estado_civil'),
            email=data['email'],
            telefono=data.get('telefono'),
            titulo_propiedad=data['titulo_propiedad'],
            tipo_inmueble=data.get('tipo_inmueble', 'Apartamento'),
            datos_inmueble=data.get('datos_inmueble'),
            referencia=data.get('referencia'),
            habitaciones=safe_int(data.get('habitaciones')),
            hab_servicio=safe_int(data.get('hab_servicio')),
            total_habitaciones=safe_int(data.get('total_habitaciones')),
            banos_completos=safe_int(data.get('banos_completos')),
            bano_servicio=safe_int(data.get('bano_servicio')),
            medio_bano=safe_int(data.get('medio_bano')),
            total_banos=safe_int(data.get('total_banos')),
            puestos_estacionamiento=safe_int(data.get('puestos_estacionamiento')),
            estacionamientos_cubiertos=safe_int(data.get('estacionamientos_cubiertos')),
            estacionamientos_descubiertos=safe_int(data.get('estacionamientos_descubiertos')),
            tiene_maletero='tiene_maletero' in data,
            cantidad_maleteros=safe_int(data.get('cantidad_maleteros')),
            metros_construccion=safe_float(data.get('metros_construccion')),
            metros_terreno=safe_float(data.get('metros_terreno')),
            anio_construccion=safe_int(data.get('anio_construccion')) if data.get('anio_construccion') else None,
            obra=data.get('obra'),
            estilo=data.get('estilo'),
            tiene_terraza='tiene_terraza' in data,
            tipo_piso=data.get('tipo_piso'),
            niveles=safe_int(data.get('niveles')),
            pais=data.get('pais'),
            estado_departamento=data.get('estado_departamento'),
            ciudad=data.get('ciudad'),
            direccion=data.get('direccion'),
            codigo_postal=data.get('codigo_postal'),
            aptos_x_piso=safe_int(data.get('aptos_x_piso')),
            total_pisos=safe_int(data.get('total_pisos')),
            areas_internas=areas_internas,
            areas_comunes=areas_comunes,
            servicio_telefonia_fija=telefonia,
            servicio_cable=cablevision,
            servicio_internet=internet,
            comodidades=comodidades,
            condominio_aprox=safe_float(data.get('condominio_aprox')),
            precio=safe_float(data.get('precio')),
            comision=safe_float(data.get('comision')) if data.get('comision') else None,
            imagen_cedula=imagen_cedula,
            documento_propiedad=documento_propiedad,
            imagen_principal=','.join(imagenes),
            tipo_negocio=tipo_negocio,
            id_usuario=user_id
        )
        db.session.add(nuevo_apartamento)
        db.session.commit()
        flash('Apartamento creado exitosamente', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('crear-inmueble-apartamento.html', user=user, apartamento=None)

#ruta para crear terreno
@main_routes.route('/crear-terreno', methods=['GET', 'POST'])
def crear_terreno():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if request.method == 'POST':
        try:
            data = request.form
            print(data)  # Verifica los datos que Flask recibe

            imagenes = []
            if 'imagenes' in request.files:
                archivos = request.files.getlist('imagenes')
                for archivo in archivos:
                    if archivo and archivo.filename:
                        filename = secure_filename(archivo.filename)
                        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        archivo.save(ruta)
                        imagenes.append(filename)  # Guardar solo el nombre del archivo

            # Guardar otras imágenes
            imagen_cedula = guardar_archivo(request.files.get('imagen_cedula'))
            documento_propiedad = guardar_archivo(request.files.get('documento_propiedad'))

            # Conversión segura de campos numéricos
            def safe_int(val):
                return int(val) if val not in (None, '', 'None') else None
            def safe_float(val):
                return float(val) if val not in (None, '', 'None') else None

            # Obtener los valores de los nuevos campos
            m2_terreno = safe_float(data.get('m2_terreno'))
            m2_construccion = safe_float(data.get('m2_construccion'))
            m_frente = safe_float(data.get('m_frente'))
            m_anch = safe_float(data.get('m_anch'))
            m_largo = safe_float(data.get('m_largo'))
            cerca_perimetral = data.get('cerca_perimetral')
            bienechurias = data.get('bienechurias')
            otros = data.get('otros')
            materiales = ','.join(request.form.getlist('materiales'))
            tipo_negocio = data.get('tipo_negocio')

            # Otros campos del formulario
            precio = safe_float(data.get('precio'))
            comision = safe_float(data.get('comision'))

            # Crear el nuevo terreno
            nuevo_terreno = Terreno(
                titulo_publicacion=data['titulo_publicacion'],
               
                tipo_inmueble=data['tipo_inmueble'],
                nombre=data['nombre'],
                apellido=data['apellido'],
                ci=data['ci'],
                rif=data.get('rif'),
                fecha_nacimiento=datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d') if data.get('fecha_nacimiento') else None,
                estado_civil=data.get('estado_civil'),
                email=data['email'],
                telefono=data.get('telefono'),
                estado=data['estado'],
                municipio=data['municipio'],
                ciudad=data['ciudad'],
                urbanizacion=data['urbanizacion'],
                referencia=data.get('referencia'),
                m2_terreno=m2_terreno,
                m2_construccion=m2_construccion,
                m_frente=m_frente,
                m_anch=m_anch,
                m_largo=m_largo,
                cerca_perimetral=cerca_perimetral,
                bienechurias=bienechurias,
                otros=otros,
                materiales=materiales,  # Almacena los materiales como texto separado por comas
                precio=precio,
                comision=comision,

                imagen_cedula=imagen_cedula,
                documento_propiedad=documento_propiedad,
                imagen_principal=','.join(imagenes),
                tipo_negocio = tipo_negocio,
                id_usuario=user_id
            )

            db.session.add(nuevo_terreno)
            db.session.commit()

            flash('Terreno creado exitosamente', 'success')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el terreno: {str(e)}', 'danger')
            

    return render_template('crear-inmueble-terreno.html', user=user, terreno=None)


@main_routes.route('/crear-galpon', methods=['GET', 'POST'])
def crear_galpon():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige a login si no hay sesión activa
    
    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if request.method == 'POST':
    
            data = request.form  # Obtiene los datos del formulario

            imagenes = []
            if 'imagenes' in request.files:
                archivos = request.files.getlist('imagenes')
                for archivo in archivos:
                    if archivo and archivo.filename:
                        filename = secure_filename(archivo.filename)
                        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        archivo.save(ruta)
                        imagenes.append(filename)  # Guardar solo el nombre del archivo

            # Guardar otras imágenes
            imagen_cedula = guardar_archivo(request.files.get('imagen_cedula'))
            documento_propiedad = guardar_archivo(request.files.get('documento_propiedad'))

            # Conversión segura de campos numéricos
            def safe_int(val):
                return int(val) if val not in (None, '', 'None') else None
            def safe_float(val):
                return float(val) if val not in (None, '', 'None') else None

            # Captura de los datos del formulario con validación
            oficinas = safe_int(data.get('oficinas'))
            banos_completos = safe_int(data.get('banos_completos'))
            precio = safe_float(data.get('precio'))
            comision = safe_float(data.get('comision'))
            area_descanso = data['area_descanso'] or None
            amoblado = data['amoblado'] or None
            galpon = data['galpon'] or None
            banos_servicio = safe_int(data.get('bano_servicio'))
            puestos_estacionamiento = safe_int(data.get('puestos_estacionamiento'))
            kitchenette = data['kitchenette'] or None
            patio_trabajo = data['patio_trabajo'] or None
            m_frente = safe_float(data.get('m_frente'))
            total_banos = safe_int(data.get('total_banos'))
            descubierto = data['estacionamientos_descubiertos'] or None
            vigilancia = data['vigilancia'] or None
            m_fondo = safe_float(data.get('m_fondo'))
            estacionamiento_visitantes = data['estacionamiento_visitantes'] or None
            m_altura = safe_float(data.get('m_altura'))
            centro_comercial = data['centro_comercial'] or None
            m2_terreno = safe_float(data.get('m2_terreno'))
            anos_construccion = safe_int(data.get('anos_construccion'))
            parque_industrial = data['parque_industrial'] or None
            m2_construccion = safe_float(data.get('m2_construccion'))
            condominio_aprox = safe_float(data.get('condominio_aprox'))
            tipo_negocio = data.get('tipo_negocio')

            # Obtener las áreas internas, comodidades y servicios como listas
            areas_internas = ','.join(request.form.getlist('areas_internas'))
            comodidades = ','.join(request.form.getlist('comodidades'))
            servicio_telefonia_fija = ','.join(request.form.getlist('servicio_telefonia_fija'))
            servicio_cable = ','.join(request.form.getlist('servicio_cable'))
            servicio_internet = ','.join(request.form.getlist('servicio_internet'))

            titulo_propiedad = data['titulo_propiedad']
            destacado = 'destacado' in data
            tipo_inmueble = data['tipo_inmueble']
            datos_inmueble = data['datos_inmueble']
            referencia = data['referencia']

            if not titulo_propiedad:
                flash('El campo Título de Propiedad es obligatorio.', 'danger')
                return redirect(url_for('main.crear_galpon'))
            
            nuevo_galpon = Galpon(
                nombre=data['nombre'],
                apellido=data['apellido'],
                ci=data['ci'],
                rif=data.get('rif'),
                fecha_nacimiento=datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d') if data.get('fecha_nacimiento') else None,
                estado_civil=data.get('estado_civil'),
                email=data['email'],
                telefono=data.get('telefono'),
                titulo_propiedad=titulo_propiedad,
                destacado=destacado,
                tipo_inmueble=tipo_inmueble,
                datos_inmueble=datos_inmueble,
                referencia=referencia,
                oficinas=oficinas,
                galpon=galpon,
                banos_completos=banos_completos,
                banos_servicio=banos_servicio,
                medio_bano=safe_int(data.get('medio_bano')),
                area_descanso=area_descanso,
                puestos_estacionamiento=puestos_estacionamiento,
                cubierto=data.get('cubierto'),
                amoblado=amoblado,
                kitchenette=kitchenette,
                patio_trabajo=patio_trabajo,
                m_frente=m_frente,
                total_banos=total_banos,
                descubierto=descubierto,
                vigilancia=vigilancia,
                m_fondo=m_fondo,
                estacionamiento_visitantes=estacionamiento_visitantes,
                m_altura=m_altura,
                centro_comercial=centro_comercial,
                m2_terreno=m2_terreno,
                anos_construccion=anos_construccion,
                parque_industrial=parque_industrial,
                m2_construccion=m2_construccion,
                condominio_aprox=condominio_aprox,
                pais=data.get('pais'),
                estado_departamento=data.get('estado_departamento'),
                ciudad=data.get('ciudad'),
                direccion=data.get('direccion'),
                codigo_postal=data.get('codigo_postal'),
                imagen_cedula=imagen_cedula,
                documento_propiedad=documento_propiedad,
                imagen_principal=','.join(imagenes),
                areas_internas=areas_internas,
                comodidades=comodidades,
                servicio_telefonia_fija=servicio_telefonia_fija,
                servicio_cable=servicio_cable,
                servicio_internet=servicio_internet,
                precio=precio,
                comision=comision,
                tipo_negocio = tipo_negocio,
                id_usuario=user_id
            )

            db.session.add(nuevo_galpon)
            db.session.commit()

            flash('Galpón creado exitosamente', 'success')
            return redirect(url_for('main.dashboard'))

    return render_template('crear-inmueble-galpon.html', user=user, galpon=None)

#ruta para locales

@main_routes.route('/crear-local', methods=['GET', 'POST'])
def crear_local():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige a login si no hay sesión activa
    
    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if request.method == 'POST':
            
        try:
            data = request.form  # Obtiene los datos del formulario

            tipo_negocio = data.get('tipo_negocio')

            imagenes = []
            if 'imagenes' in request.files:
                archivos = request.files.getlist('imagenes')
                for archivo in archivos:
                    if archivo and archivo.filename:
                        filename = secure_filename(archivo.filename)
                        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        archivo.save(ruta)
                        imagenes.append(filename)  # Guardar solo el nombre del archivo

            # Guardar otras imágenes
            imagen_cedula = guardar_archivo(request.files.get('imagen_cedula'))
            documento_propiedad = guardar_archivo(request.files.get('documento_propiedad'))

            # Conversión segura de campos numéricos
            def safe_int(val):
                return int(val) if val not in (None, '', 'None') else None
            def safe_float(val):
                return float(val) if val not in (None, '', 'None') else None

            # Campos numéricos
            banos_completos = safe_int(data.get('banos_completos'))
            precio = safe_float(data.get('precio'))
            comision = safe_float(data.get('comision'))
            banos_servicio = safe_int(data.get('bano_servicio'))
            puestos_estacionamiento = safe_int(data.get('puestos_estacionamiento'))
            m_frente = safe_float(data.get('m_frente'))
            total_banos = safe_int(data.get('total_banos'))
            m_fondo = safe_float(data.get('m_fondo'))
            m_altura = safe_float(data.get('m_altura'))
            m2_terreno = safe_float(data.get('m2_terreno'))
            anos_construccion = safe_int(data.get('anos_construccion'))
            m2_construccion = safe_float(data.get('m2_construccion'))
            condominio_aprox = safe_float(data.get('condominio_aprox'))

            # Campos de texto
            area_descanso = data.get('area_descanso')
            amoblado = data.get('amoblado')
            patio_trabajo = data.get('patio_trabajo')
            descubierto = data.get('descubierto')
            vigilancia = data.get('vigilancia')
            estacionamiento_visitantes = data.get('estacionamiento_visitantes')
            parque_industrial = data.get('parque_industrial')

            # Campos de servicios
            areas_internas = ','.join(request.form.getlist('areas_internas'))
            comodidades = ','.join(request.form.getlist('comodidades'))
            servicio_telefonia_fija = ','.join(request.form.getlist('servicio_telefonia_fija'))
            servicio_cable = ','.join(request.form.getlist('servicio_cable'))
            servicio_internet = ','.join(request.form.getlist('servicio_internet'))

            # Campos obligatorios
            titulo_propiedad = data.get('titulo_propiedad')
            tipo_inmueble = data.get('tipo_inmueble')
            datos_inmueble = data.get('datos_inmueble')
            referencia = data.get('referencia')

            # Campo destacado
            destacado = 'destacado' in data

            if not titulo_propiedad:
                flash('El campo Título de Propiedad es obligatorio.', 'danger')
                return redirect(url_for('main.crear_local'))
            
            nuevo_local = Local(
                nombre=data.get('nombre'),
                apellido=data.get('apellido'),
                ci=data.get('ci'),
                rif=data.get('rif'),
                fecha_nacimiento=datetime.strptime(data.get('fecha_nacimiento'), '%Y-%m-%d') if data.get('fecha_nacimiento') else None,
                estado_civil=data.get('estado_civil'),
                email=data.get('email'),
                telefono=data.get('telefono'),
                titulo_propiedad=titulo_propiedad,
                tipo_inmueble=tipo_inmueble,
                datos_inmueble=datos_inmueble,
                referencia=referencia,
                banos_completos=banos_completos,
                banos_servicio=banos_servicio,
                medio_bano=safe_int(data.get('medio_bano')),
                area_descanso=area_descanso,
                puestos_estacionamiento=puestos_estacionamiento,
                cubierto=data.get('cubierto'),
                amoblado=amoblado,
                patio_trabajo=patio_trabajo,
                m_frente=m_frente,
                total_banos=total_banos,
                descubierto=descubierto,
                vigilancia=vigilancia,
                m_fondo=m_fondo,
                estacionamiento_visitantes=estacionamiento_visitantes,
                m_altura=m_altura,
                m2_terreno=m2_terreno,
                anos_construccion=anos_construccion,
                parque_industrial=parque_industrial,
                m2_construccion=m2_construccion,
                condominio_aprox=condominio_aprox,
                pais=data.get('pais'),
                estado_departamento=data.get('estado_departamento'),
                ciudad=data.get('ciudad'),
                direccion=data.get('direccion'),
                codigo_postal=data.get('codigo_postal'),
                imagen_cedula=imagen_cedula,
                documento_propiedad=documento_propiedad,
                imagen_principal=','.join(imagenes),
                areas_internas=areas_internas,
                comodidades=comodidades,
                servicio_telefonia_fija=servicio_telefonia_fija,
                servicio_cable=servicio_cable,
                servicio_internet=servicio_internet,
                precio=precio,
                comision=comision,
                tipo_negocio=tipo_negocio,
                destacado=destacado,
                id_usuario=user_id
            )

            db.session.add(nuevo_local)
            db.session.commit()

            flash('Local creado exitosamente', 'success')
            return redirect(url_for('main.dashboard'))
        
        except Exception as e:
            db.session.rollback()  # Si ocurre un error, revertimos la transacción
            flash(f'Error al crear el Local: {str(e)}', 'danger')
            return redirect(url_for('main.crear_local'))  # Redirige al formulario de creación

    return render_template('crear-inmueble-local.html', user=user, local=None)

#crear comercio 

@main_routes.route('/crear-comercio', methods=['GET', 'POST'])
def crear_comercio():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige a login si no hay sesión activa
    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if request.method == 'POST':
        
            data = request.form  # Obtiene los datos del formulario
            tipo_negocio = data.get('tipo_negocio')
            # Procesar múltiples imágenes principales
            imagenes = []
            if 'imagenes' in request.files:
                archivos = request.files.getlist('imagenes')
                for archivo in archivos:
                    if archivo and archivo.filename:
                        filename = secure_filename(archivo.filename)
                        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        archivo.save(ruta)
                        imagenes.append(filename)  # Guardar solo el nombre del archivo
            # Guardar otras imágenes
            imagen_cedula = guardar_archivo(request.files.get('imagen_cedula'))
            documento_propiedad = guardar_archivo(request.files.get('documento_propiedad'))
            # Conversión segura de campos numéricos
            def safe_int(val):
                return int(val) if val not in (None, '', 'None') else None
            def safe_float(val):
                return float(val) if val not in (None, '', 'None') else None
            banos_completos = safe_int(data.get('banos_completos'))
            precio = safe_float(data.get('precio'))
            comision = safe_float(data.get('comision'))
            area_descanso = data['area_descanso'] or None
            amoblado = data['amoblado'] or None
            banos_servicio = safe_int(data.get('bano_servicio'))
            puestos_estacionamiento = safe_int(data.get('puestos_estacionamiento'))
            m_frente = safe_float(data.get('m_frente'))
            total_banos = safe_int(data.get('total_banos'))
            descubierto = data['descubierto'] or None
            m_fondo = safe_float(data.get('m_fondo'))
            estacionamiento_visitantes = data['estacionamiento_visitantes'] or None
            m_altura = safe_float(data.get('m_altura'))
            m2_terreno = safe_float(data.get('m2_terreno'))
            anos_construccion = safe_int(data.get('anos_construccion'))
            m2_construccion = safe_float(data.get('m2_construccion'))
            condominio_aprox = safe_float(data.get('condominio_aprox'))
            areas_internas = ','.join(request.form.getlist('areas_internas'))
            comodidades = ','.join(request.form.getlist('comodidades'))
            telefonia = ','.join(request.form.getlist('telefonia'))
            cablevision = ','.join(request.form.getlist('cablevision'))
            internet = ','.join(request.form.getlist('internet'))
            titulo_propiedad = data['titulo_propiedad']
            tipo_inmueble = data['tipo_inmueble']
            datos_inmueble = data['datos_inmueble']
            referencia = data['referencia']
            # --- CAMBIO: Manejo de destacado ---
            destacado = 'destacado' in data or data.get('destacado', 'off') == 'on'
            # Si el campo no viene, será False
            if not titulo_propiedad:
                flash('El campo Título de Propiedad es obligatorio.', 'danger')
                return redirect(url_for('main.crear_comercio'))
            nuevo_comercio = Comercio(
                nombre=data['nombre'],
                apellido=data['apellido'],
                ci=data['ci'],
                rif=data.get('rif'),
                fecha_nacimiento=datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d') if data.get('fecha_nacimiento') else None,
                estado_civil=data.get('estado_civil'),
                email=data['email'],
                telefono=data.get('telefono'),
                titulo_propiedad=titulo_propiedad,
                tipo_inmueble=tipo_inmueble,
                datos_inmueble=datos_inmueble,
                referencia=referencia,
                banos_completos=banos_completos,
                bano_servicio=banos_servicio,
                medio_bano=safe_int(data.get('medio_bano')),
                area_descanso=area_descanso,
                puestos_estacionamiento=puestos_estacionamiento,
                cubierto=data.get('cubierto'),
                amoblado=amoblado,
                m_frente=m_frente,
                total_banos=total_banos,
                descubierto=descubierto,
                m_fondo=m_fondo,
                estacionamiento_visitantes=estacionamiento_visitantes,
                m_altura=m_altura,
                m2_terreno=m2_terreno,
                anos_construccion=anos_construccion,
                m2_construccion=m2_construccion,
                condominio_aprox=condominio_aprox,
                pais=data.get('pais'),
                estado_departamento=data.get('estado_departamento'),
                ciudad=data.get('ciudad'),
                direccion=data.get('direccion'),
                codigo_postal=data.get('codigo_postal'),
                imagen_cedula=imagen_cedula,
                documento_propiedad=documento_propiedad,
                imagen_principal=','.join(imagenes),
                areas_internas=areas_internas,
                comodidades=comodidades,
                telefonia=telefonia,
                cablevision=cablevision,
                internet=internet,
                precio=precio,
                comision=comision,
                tipo_negocio=tipo_negocio,
                id_usuario=user_id,
                destacado=destacado,
                # Agregando los campos faltantes
                oficinas=safe_int(data.get('oficinas')),
                ambientes=safe_int(data.get('ambientes')),
                razon_social=data.get('razon_social'),
                anio_apertura=safe_int(data.get('anio_apertura')),
                punto_venta=data.get('punto_venta') == 'on',
                maquinas_equipos=data.get('maquinas_equipos') == 'on',
                mobiliario=data.get('mobiliario') == 'on',
                lineas_telefonicas=data.get('lineas_telefonicas') == 'on',
                rrss_activas=data.get('rrss_activas') == 'on',
                sistema_fiscal=data.get('sistema_fiscal') == 'on',
                pag_web_activa=data.get('pag_web_activa') == 'on',
                contabilidad=data.get('contabilidad') == 'on'
            )
            db.session.add(nuevo_comercio)
            db.session.commit()
            flash('Comercio creado exitosamente', 'success')
            return redirect(url_for('main.dashboard'))  # Redirige al dashboard

    return render_template('crear-inmueble-comercio.html', user=user, comercio=None)

#ruta para lista-inmuebles

@main_routes.route('/lista-inmuebles')
def lista_inmuebles():

    

    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Ensure the user is logged in
    
    user_id = session['user_id']
    user = User.query.get(user_id) 
    
    # Obtener todas las casas
    casas = Casa.query.all()
    
    # Obtener todos los apartamentos
    apartamentos = Apartamento.query.all()
    
    # Obtener todos los terrenos
    terrenos = Terreno.query.all()
    
    # Obtener todos los galpones
    galpones = Galpon.query.all()
    
    # Obtener todos los comercios
    comercios = Comercio.query.all()

    locales= Local.query.all()

    # Combina todos los inmuebles en una lista
    inmuebles = casas + apartamentos + terrenos + galpones + comercios + locales

    # Pasa los inmuebles al template
    return render_template('lista-inmuebles.html', inmuebles=inmuebles, user=user)

#ruta para ver los inmuebles 
@main_routes.route('/ver-inmueble/<string:tipo_inmueble>/<int:inmueble_id>')
def ver_inmueble(tipo_inmueble, inmueble_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Asegurarse de que el usuario está logueado
    user_id = session['user_id']
    user = User.query.get(user_id) 
    
    # Buscar el inmueble en la tabla correspondiente según el tipo
    if tipo_inmueble == 'casa':
        inmueble = Casa.query.get(inmueble_id)
    elif tipo_inmueble == 'apartamento':
        inmueble = Apartamento.query.get(inmueble_id)
    elif tipo_inmueble == 'terreno':
        inmueble = Terreno.query.get(inmueble_id)
    elif tipo_inmueble == 'galpon':
        inmueble = Galpon.query.get(inmueble_id)
    elif tipo_inmueble == 'comercio':
        inmueble = Comercio.query.get(inmueble_id)
    elif tipo_inmueble == 'local':
        inmueble = Local.query.get(inmueble_id)
    elif tipo_inmueble == 'oficina':
        inmueble = Local.query.get(inmueble_id)
    else:
        flash("Tipo de inmueble no válido", "danger")
        return redirect(url_for('main.lista_inmuebles'))  # Redirigir si el tipo de inmueble es inválido

    # Si el inmueble no se encuentra en la base de datos, mostrar un mensaje de error
    if not inmueble:
        flash("Inmueble no encontrado", "danger")
        return redirect(url_for('main.lista_inmuebles'))  # Redirigir si no se encuentra el inmueble
    
    # Obtener el usuario que registró el inmueble
    usuario = User.query.get(inmueble.id_usuario)  # Asegúrate de que la relación esté bien definida

    # Pasar los datos del inmueble y usuario al template
    return render_template('ver-inmueble.html', inmueble=inmueble, usuario=usuario, user=user)

#ruta de mis inmuebles 

@main_routes.route('/mis-inmuebles')
def mis_inmuebles():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige al login si no hay sesión activa
    
    user_id = session['user_id']
    user = User.query.get(user_id) 
    
    
    
    # Obtener todas las casas del usuario
    casas = Casa.query.filter_by(id_usuario=user_id).all()
    
    # Obtener todos los apartamentos del usuario
    apartamentos = Apartamento.query.filter_by(id_usuario=user_id).all()
    
    # Obtener todos los terrenos del usuario
    terrenos = Terreno.query.filter_by(id_usuario=user_id).all()
    
    # Obtener todos los galpones del usuario
    galpones = Galpon.query.filter_by(id_usuario=user_id).all()
    
    # Obtener todos los comercios del usuario
    comercios = Comercio.query.filter_by(id_usuario=user_id).all()

    locales= Local.query.filter_by(id_usuario=user_id).all()

    # Combina todos los inmuebles del usuario en una lista
    inmuebles = casas + apartamentos + terrenos + galpones + comercios + locales

    # Pasa los inmuebles al template
    return render_template('mis-inmuebles.html', inmuebles=inmuebles, user=user)

#ruta para editar inmuebles 

@main_routes.route('/editar-inmueble/<tipo_inmueble>/<int:inmueble_id>', methods=['GET', 'POST'])
def editar_inmueble(tipo_inmueble, inmueble_id):
    # Obtener el inmueble basado en el tipo y ID

    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige al login si no hay sesión activa
    
    user_id = session['user_id']
    user = User.query.get(user_id) 
    
    if tipo_inmueble == 'casa':
        inmueble = Casa.query.get_or_404(inmueble_id)
    elif tipo_inmueble == 'apartamento':
        inmueble = Apartamento.query.get_or_404(inmueble_id)
    elif tipo_inmueble == 'terreno':
        inmueble = Terreno.query.get_or_404(inmueble_id)
    elif tipo_inmueble == 'galpon':
        inmueble = Galpon.query.get_or_404(inmueble_id)
    elif tipo_inmueble == 'comercio':
        inmueble = Comercio.query.get_or_404(inmueble_id)
    elif tipo_inmueble == 'local':
        inmueble = Local.query.get_or_404(inmueble_id)
    else:
        flash('Tipo de inmueble no válido.', 'danger')
        return redirect(url_for('main.lista_inmuebles'))  # Redirige si el tipo es incorrecto
    
    if request.method == 'POST':
        # Aquí puedes procesar los datos del formulario de edición
        try:
            # Obtén los datos del formulario
            inmueble.titulo_inmueble = request.form['titulo_inmueble']
            inmueble.precio = request.form['precio']
            inmueble.estado_publicacion = request.form['estado_publicacion']
            inmueble.tipo_negocio = request.form['tipo_negocio']
            # Agregar más campos que necesites actualizar
            
            # Guardar los cambios en la base de datos
            db.session.commit()
            flash('Inmueble actualizado con éxito.', 'success')
            return redirect(url_for('main.ver_inmueble', tipo_inmueble=tipo_inmueble, inmueble_id=inmueble.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el inmueble: {str(e)}', 'danger')
    
    # Renderizar el formulario de edición con los datos actuales
    return render_template('editar-inmueble.html', inmueble=inmueble, tipo_inmueble=tipo_inmueble, user=user)

#ruta para eliminar inmueble 

@main_routes.route('/eliminar-inmueble/<string:tipo_inmueble>/<int:inmueble_id>', methods=['GET', 'POST'])
def eliminar_inmueble(tipo_inmueble, inmueble_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirigir al login si no hay sesión activa
    

    try:
        # Selecciona el modelo adecuado dependiendo del tipo de inmueble
        if tipo_inmueble == 'casa':
            inmueble = Casa.query.get(inmueble_id)
        elif tipo_inmueble == 'apartamento':
            inmueble = Apartamento.query.get(inmueble_id)
        elif tipo_inmueble == 'terreno':
            inmueble = Terreno.query.get(inmueble_id)
        elif tipo_inmueble == 'galpon':
            inmueble = Galpon.query.get(inmueble_id)
        elif tipo_inmueble == 'comercio':
            inmueble = Comercio.query.get(inmueble_id)
        elif tipo_inmueble == 'local':
            inmueble = Local.query.get(inmueble_id)
        else:
            flash('Tipo de inmueble no válido.', 'danger')
            return redirect(url_for('main.lista_inmuebles'))

        # Si el inmueble existe, se elimina
        if inmueble:
            # Obtener el título correcto según el tipo de inmueble
            if tipo_inmueble == 'terreno':
                titulo = getattr(inmueble, 'titulo_publicacion', 'Inmueble')
            else:
                titulo = getattr(inmueble, 'titulo_propiedad', 'Inmueble')
            db.session.delete(inmueble)
            db.session.commit()
            flash(f'El inmueble {titulo} ha sido eliminado exitosamente.', 'success')
        else:
            flash('El inmueble no fue encontrado.', 'danger')

    except Exception as e:
        db.session.rollback()
        flash(f'Ocurrió un error al eliminar el inmueble: {str(e)}', 'danger')

    # Redirige a la lista de inmuebles después de la eliminación
    return redirect(url_for('main.lista_inmuebles'))

#ruta para ver inmuebles en venta 
@main_routes.route('/inmuebles-venta')
def inmuebles_venta():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Verifica que el usuario esté logueado
    user_id = session['user_id']
    user = User.query.get(user_id) 
    
    # Filtrar inmuebles que tienen tipo_negocio = 'Venta'
    inmuebles_venta = Casa.query.filter_by(tipo_negocio='Venta').all() + \
                       Apartamento.query.filter_by(tipo_negocio='Venta').all() + \
                       Terreno.query.filter_by(tipo_negocio='Venta').all() + \
                       Galpon.query.filter_by(tipo_negocio='Venta').all() + \
                       Local.query.filter_by(tipo_negocio='Venta').all() + \
                       Comercio.query.filter_by(tipo_negocio='Venta').all()

    # Pasar los datos al template
    return render_template('lista-inmuebles-venta.html', inmuebles=inmuebles_venta, user=user)

#ruta para ver inmuebles en alquiler 

@main_routes.route('/inmuebles-alquiler')
def inmuebles_alquiler():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Verifica que el usuario esté logueado
    
    user_id = session['user_id']
    user = User.query.get(user_id) 
    
    # Filtrar inmuebles que tienen tipo_negocio = 'Alquiler'
    inmuebles_alquiler = Casa.query.filter_by(tipo_negocio='Alquiler').all() + \
                         Apartamento.query.filter_by(tipo_negocio='Alquiler').all() + \
                         Terreno.query.filter_by(tipo_negocio='Alquiler').all() + \
                         Galpon.query.filter_by(tipo_negocio='Alquiler').all() + \
                         Local.query.filter_by(tipo_negocio='Venta').all() + \
                         Comercio.query.filter_by(tipo_negocio='Alquiler').all()

    # Pasar los datos al template
    return render_template('lista-inmuebles-alquiler.html', inmuebles=inmuebles_alquiler, user=user)






#rutas de las zonas de usuarios 
#ruta para la vista del perfil del usuario 
@main_routes.route('/usuarios')
def usuarios():
    # Verificar si el usuario está logueado
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirigir al login si no está logueado
    
    # Obtener el ID del usuario desde la sesión
    user_id = session['user_id']

    
    # Obtener el usuario actual de la base de datos
    usuario = User.query.get(user_id)
    
    if usuario:
        # Renderizar el archivo usuario.html pasando la información del usuario
        return render_template('usuario.html', usuario=usuario, user=usuario)
    else:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.login'))

@main_routes.route('/actualizar-perfil', methods=['POST'])
def actualizar_perfil():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirigir al login si no está logueado
    
    # Obtener el ID del usuario desde la sesión
    user_id = session['user_id']
    usuario = User.query.get(user_id)
    
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.login'))  # Redirigir al login si el usuario no existe

    # Actualizar los datos del usuario con los nuevos valores del formulario
    usuario.nombre = request.form['nombre']
    usuario.correo_usuario = request.form['email']
    usuario.telefono = request.form['telefono']
    usuario.direccion = request.form['direccion']
    usuario.facebook = request.form.get('facebook', '')  # Se utiliza get() por si el campo está vacío
    usuario.instagram = request.form.get('instagram', '')
    usuario.telegram = request.form.get('telegram', '')
    usuario.twitter = request.form.get('twitter', '')

    # Manejar la subida de una nueva imagen de perfil
    if 'imagen_usuario' in request.files:
        imagen_usuario = request.files['imagen_usuario']
        if imagen_usuario.filename != '':
            # Guardar la nueva imagen con un nombre seguro
            filename = secure_filename(imagen_usuario.filename)
            filepath = os.path.join('static/imagenes/usuarios', filename)
            imagen_usuario.save(filepath)
            usuario.imagen_usuario = filename  # Actualizar la imagen en la base de datos
        else:
            # Si no se sube una nueva imagen, dejamos la imagen predeterminada
            if not usuario.imagen_usuario:  # Si no hay imagen, asignamos la predeterminada
                usuario.imagen_usuario = 'perfil-vacio.png'
    else:
        # Si no se envió ningún archivo, asignamos la imagen predeterminada
        if not usuario.imagen_usuario:
            usuario.imagen_usuario = 'perfil-vacio.png'

    # Guardar los cambios en la base de datos
    db.session.commit()

    flash('Perfil actualizado correctamente', 'success')
    return redirect(url_for('main.usuarios'))  # Redirigir al perfil del usuario actualizado

#ruta para crear usuario 
@main_routes.route('/crear-usuario', methods=['GET', 'POST'])
def crear_usuario():
    # Asegúrate de que el usuario está logueado
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige si el usuario no está logueado
    
    # Obtener el usuario desde la base de datos
    user_id = session['user_id']
    usuario = User.query.get(user_id)
    
    # Verificar que el usuario logueado sea un administrador
    if usuario.rol != 'administrador':
        flash('No tienes permisos para agregar usuarios', 'danger')
        return redirect(url_for('main.dashboard'))  # Redirigir si no es administrador
    
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        correo_usuario = request.form['correo_usuario']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        contrasena = request.form['contrasena']
        area_o_sucursal = request.form['area_o_sucursal']

        
        # Crear un nuevo usuario con rol "agente"
        nuevo_usuario = User(
            nombre=nombre,
            apellidos=apellidos,
            correo_usuario=correo_usuario,
            telefono=telefono,
            direccion=direccion,
            rol='agente',  # Asignamos el rol "agente"
            tipo_usuario='agente',  # Puedes definir otros valores por defecto si lo necesitas
            estado='activo',  # El estado del nuevo usuario puede ser activo por defecto
            area_o_sucursal=area_o_sucursal  # Añadir el valor de 'area_o_sucursal'
        )
        
        # Establecer la contraseña hasheada
        nuevo_usuario.set_password(contrasena)
        
        # Agregar el nuevo usuario a la base de datos
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('Usuario creado con éxito', 'success')
        return redirect(url_for('main.dashboard'))  # Redirigir al dashboard o a la lista de usuarios

    return render_template('crear-usuario.html', user=usuario)  # Crear un template `crear_usuario.html`


#ruta para cambiar la contraseña 
@main_routes.route('/cambiar-contrasena', methods=['GET', 'POST'])
def cambiar_contrasena():
    # Asegúrate de que el usuario está logueado
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige si el usuario no está logueado
    
    # Obtener el usuario desde la base de datos
    user_id = session['user_id']
    usuario = User.query.get(user_id)
    
    # Verificar que el usuario logueado es el mismo que intenta cambiar la contraseña
    if usuario is None:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.login'))  # Redirigir si no se encuentra el usuario
    
    if request.method == 'POST':
        # Obtener los datos del formulario
        contrasena_actual = request.form['contrasena_actual']
        nueva_contrasena = request.form['nueva_contrasena']
        confirmacion_contrasena = request.form['confirmacion_contrasena']

        # Verificar que la contraseña actual es correcta
        if not check_password_hash(usuario.contrasena, contrasena_actual):
            flash('La contraseña actual es incorrecta', 'danger')
            return redirect(url_for('main.cambiar_contrasena'))  # Redirige al formulario si la contraseña actual es incorrecta

        # Verificar que las nuevas contraseñas coinciden
        if nueva_contrasena != confirmacion_contrasena:
            flash('Las nuevas contraseñas no coinciden', 'danger')
            return redirect(url_for('main.cambiar_contrasena'))  # Redirige si las contraseñas no coinciden

        # Establecer la nueva contraseña hasheada
        usuario.set_password(nueva_contrasena)

        # Guardar los cambios en la base de datos
        db.session.commit()

        flash('Contraseña cambiada con éxito', 'success')
        return redirect(url_for('main.dashboard'))  # Redirige al dashboard después de cambiar la contraseña

    return render_template('cambiar-contrasena.html', user=usuario)  # Renderiza el formulario para cambiar la contraseña


#ruta para la lista de usuarios 
@main_routes.route('/lista-usuarios')
def lista_usuarios():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Asegura que el usuario esté logueado
    user_id = session['user_id']
    # Obtener todos los usuarios desde la base de datos
    usuarios = User.query.all()
    usuario = User.query.get(user_id)

    return render_template('lista-usuarios.html', usuarios=usuarios, user=usuario)

#ruta para ver un usuario 
@main_routes.route('/ver-usuario/<int:id>', methods=['GET'])
def ver_usuario(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Asegura que el usuario esté logueado
    
    # Obtener el usuario desde la base de datos usando el ID
    usuario = User.query.get(id)
    
    # Si el usuario no existe, redirigir a la lista de usuarios
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.lista_usuarios'))  # Asegúrate de tener esta ruta definida

    # Obtener los inmuebles del usuario, agrupados por tipo de inmueble
    casas = Casa.query.filter_by(id_usuario=id).all()
    apartamentos = Apartamento.query.filter_by(id_usuario=id).all()
    terrenos = Terreno.query.filter_by(id_usuario=id).all()
    galpones = Galpon.query.filter_by(id_usuario=id).all()
    comercios = Comercio.query.filter_by(id_usuario=id).all()

    # Combinar todos los inmuebles en una lista
    inmuebles = casas + apartamentos + terrenos + galpones + comercios

    # Pasar los datos del usuario y los inmuebles al template
    return render_template('ver-usuario.html', usuario=usuario, inmuebles=inmuebles, user=usuario)


#ruta para editar el usuario 
@main_routes.route('/editar-usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Asegura que el usuario esté logueado
    
    # Obtener el usuario logueado
    user_id = session['user_id']
    usuario_logueado = User.query.get(user_id)

    # Verificar que el usuario logueado sea un administrador
    if usuario_logueado.rol != 'administrador':
        flash('No tienes permisos para editar usuarios', 'danger')
        return redirect(url_for('main.lista_usuarios'))  # Redirige si no es administrador

    # Obtener el usuario a editar
    usuario = User.query.get(id)
    
    # Si el usuario no existe, redirigir a la lista de usuarios
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.lista_usuarios'))
    
    if request.method == 'POST':
        # Actualizar los datos del usuario
        usuario.nombre = request.form['nombre']
        usuario.apellidos = request.form['apellidos']
        usuario.correo_usuario = request.form['email']
        usuario.telefono = request.form['telefono']
        usuario.direccion = request.form['direccion']

        # Cambiar contraseña si el campo está presente y no vacío
        nueva_contrasena = request.form.get('nueva_contrasena')
        if nueva_contrasena:
            usuario.set_password(nueva_contrasena)
            flash('Contraseña actualizada con éxito.', 'success')

        # Manejar la subida de una nueva imagen de perfil
        if 'imagen_usuario' in request.files:
            imagen_usuario = request.files['imagen_usuario']
            if imagen_usuario.filename != '':
                # Guardar la nueva imagen con un nombre seguro
                filename = secure_filename(imagen_usuario.filename)
                filepath = os.path.join('static/imagenes/usuarios', filename)
                imagen_usuario.save(filepath)
                usuario.imagen_usuario = filename  # Actualizar la imagen en la base de datos
            else:
                # Si no se sube una nueva imagen, dejamos la imagen predeterminada
                if not usuario.imagen_usuario:  # Si no hay imagen, asignamos la predeterminada
                    usuario.imagen_usuario = 'perfil-vacio.png'
        else:
            # Si no se envió ningún archivo, asignamos la imagen predeterminada
            if not usuario.imagen_usuario:
                usuario.imagen_usuario = 'perfil-vacio.png'
        
        # Guardar los cambios en la base de datos
        db.session.commit()
        flash('Usuario actualizado con éxito', 'success')
        return redirect(url_for('main.lista_usuarios'))

    return render_template('editar-usuario.html', usuario=usuario, user=usuario_logueado)

#ruta para eliminar el usuario y todos sus inmuebles 
@main_routes.route('/eliminar-usuario/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Asegura que el usuario esté logueado
    
    # Obtener el usuario logueado
    user_id = session['user_id']
    usuario_logueado = User.query.get(user_id)

    # Verificar que el usuario logueado sea un administrador
    if usuario_logueado.rol != 'administrador':
        flash('No tienes permisos para eliminar usuarios', 'danger')
        return redirect(url_for('main.lista_usuarios'))  # Redirige si no es administrador
    
    # Obtener el usuario a eliminar
    usuario = User.query.get(id)
    
    # Si el usuario no existe, redirigir a la lista de usuarios
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.lista_usuarios'))
    
    # Eliminar todos los inmuebles asociados a este usuario
    casas = Casa.query.filter_by(id_usuario=id).all()
    apartamentos = Apartamento.query.filter_by(id_usuario=id).all()
    terrenos = Terreno.query.filter_by(id_usuario=id).all()
    galpones = Galpon.query.filter_by(id_usuario=id).all()
    comercios = Comercio.query.filter_by(id_usuario=id).all()

    # Eliminar los inmuebles de las distintas tablas
    for inmueble in casas + apartamentos + terrenos + galpones + comercios:
        db.session.delete(inmueble)  # Elimina cada inmueble relacionado con el usuario
    
    # Eliminar el usuario
    db.session.delete(usuario)
    db.session.commit()

    flash('Usuario y sus inmuebles eliminados con éxito', 'success')
    return redirect(url_for('main.lista_usuarios'))












#ruta de la agenda 

@main_routes.route('/ver_eventos')
def ver_eventos():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige al login si no hay usuario en sesión
    
    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if user:  # Verificamos si el usuario existe
        # Obtener todos los eventos de la agenda
        eventos = Agenda.query.all()

        # Pasar la lista de eventos al template
        return render_template('ver_eventos.html', user=user, eventos=eventos)
    else:
        flash('Acceso no autorizado o usuario no válido', 'danger')
        return redirect(url_for('main.login')) 
    
#ruta de la creacion de eventos 

@main_routes.route('/crear-evento', methods=['GET', 'POST'])
def crear_evento():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige al login si no hay usuario en sesión
    
    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if user and user.rol == 'administrador':
        if request.method == 'POST':
            # Obtener los datos del formulario
            titulo = request.form['titulo']
            fecha_inicio = request.form['fecha_inicio']
            fecha_fin = request.form['fecha_fin']

            try:
                # Convertir las fechas a formato datetime
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%dT%H:%M')
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%dT%H:%M')

                # Crear el nuevo evento
                nuevo_evento = Agenda(titulo=titulo, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
                db.session.add(nuevo_evento)
                db.session.commit()

                flash('Evento creado con éxito', 'success')
                return redirect(url_for('main.dashboard'))  # Redirige al dashboard después de guardar el evento

            except Exception as e:
                flash(f'Error al crear el evento: {str(e)}', 'danger')
        return render_template('crear-evento.html', user=user)  # Muestra el formulario de creación de eventos
    else:
        flash('Acceso no autorizado o usuario no válido', 'danger')
        return redirect(url_for('main.login'))



#ruta para las notificaciones 

@main_routes.route('/crear_notificacion', methods=['GET', 'POST'])
def crear_notificacion():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige al login si no hay usuario en sesión
    
    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if user and user.rol == 'administrador':
        if request.method == 'POST':
            titulo = request.form['titulo']
            # Crear una nueva notificación
            nueva_notificacion = Notificaciones(titulo=titulo)
            db.session.add(nueva_notificacion)
            db.session.commit()
            flash('Notificación creada con éxito', 'success')
            return redirect(url_for('main.dashboard'))  # Redirige a la página de notificaciones

        return render_template('crear_notificacion.html', user=user)  # Muestra el formulario de creación de notificación
    else:
        flash('Acceso no autorizado o usuario no válido', 'danger')
        return redirect(url_for('main.login'))  # Redirige al login si no es un administrador
    

#ruta para crear noticias

@main_routes.route('/crear_noticia', methods=['GET', 'POST'])
def crear_noticia():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige al login si no hay usuario en sesión
    
    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if user and user.rol == 'administrador':  # Solo los administradores pueden crear noticias
        if request.method == 'POST':
            # Obtener los datos del formulario
            titulo = request.form['titulo']
            link = request.form['link']

            # Crear una nueva noticia
            nueva_noticia = Noticias(titulo=titulo, link=link)
            db.session.add(nueva_noticia)
            db.session.commit()
            flash('Noticia creada con éxito', 'success')
            return redirect(url_for('main.dashboard'))  # Redirige al dashboard después de crear la noticia

        return render_template('crear_noticia.html', user=user)  # Muestra el formulario de creación de noticia
    else:
        flash('Acceso no autorizado o usuario no válido', 'danger')
        return redirect(url_for('main.login'))  # Redirige al login si no es un administrador
    

@main_routes.route('/crear_evento_medio', methods=['GET', 'POST'])
def crear_evento_medio():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige al login si no hay usuario en sesión
    
    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if user and user.rol == 'administrador':  # Solo los administradores pueden crear eventos
        if request.method == 'POST':
            # Obtener los datos del formulario
            titulo = request.form['titulo']
            ubicacion = request.form['ubicacion']
            fecha_hora = request.form['fecha_hora']

            # Convertir la fecha y hora a un objeto datetime
            try:
                fecha_hora = datetime.strptime(fecha_hora, '%Y-%m-%dT%H:%M')  # Formato 'YYYY-MM-DDTHH:MM'
            except ValueError:
                flash('Formato de fecha y hora no válido.', 'danger')
                return render_template('crear-evento-medio.html', user=user)

            # Crear un nuevo evento
            nuevo_evento = EventoDelMedio(titulo=titulo, ubicacion=ubicacion, fecha_hora=fecha_hora)
            db.session.add(nuevo_evento)
            db.session.commit()
            flash('Evento creado con éxito', 'success')
            return redirect(url_for('main.dashboard'))  # Redirige al dashboard después de crear el evento

        return render_template('crear-evento-medio.html', user=user)  # Muestra el formulario de creación de evento
    else:
        flash('Acceso no autorizado o usuario no válido', 'danger')
        return redirect(url_for('main.login'))  # Redirige a

#ruta para crear vendidos 

@main_routes.route('/crearvendidos/<string:tipo_inmueble>/<int:id>', methods=['GET', 'POST'])
def crear_vendidos(tipo_inmueble, id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Verifica si el usuario está logueado
    
    user_id = session['user_id']  # Obtener el usuario logueado
    user = User.query.get(user_id) 

    # Obtener la propiedad por el tipo de inmueble y ID
    if tipo_inmueble == "casa":
        inmueble = Casa.query.get(id)
    elif tipo_inmueble == "apartamento":
        inmueble = Apartamento.query.get(id)
    elif tipo_inmueble == "terreno":
        inmueble = Terreno.query.get(id)
    elif tipo_inmueble == "galpon":
        inmueble = Galpon.query.get(id)
    elif tipo_inmueble == "comercio":
        inmueble = Comercio.query.get(id)
    else:
        flash('Tipo de inmueble no reconocido.', 'danger')
        return redirect(url_for('main.dashboard'))  # Redirige si el tipo es incorrecto
    
    # Verificar si el tipo de negocio es 'Venta' o 'Venta y Alquiler'
    if inmueble.tipo_negocio not in ['Venta', 'Venta y Alquiler']:
        flash('No puede vender esta propiedad. El tipo de negocio no es adecuado.', 'danger')
        return redirect(url_for('main.dashboard'))  # Redirige si el tipo de negocio no es adecuado
    
    if request.method == 'POST':
        # Obtener los datos del formulario
        comprador = request.form['comprador']
        correo_comprador = request.form['correo_comprador']
        realtor_vendedor = request.form['realtor_vendedor']
        valor_comision = float(request.form['valor_comision']) if request.form['valor_comision'] else None
        fecha_venta = datetime.strptime(request.form['fecha_venta'], '%Y-%m-%d') if request.form['fecha_venta'] else datetime.utcnow()

        # Obtener el precio de la propiedad
        precio_propiedad = float(request.form['precio_propiedad']) if request.form['precio_propiedad'] else None

        # Crear un nuevo registro en la tabla 'vendidos'
        nuevo_vendido = Vendidos(
            id_del_inmueble=id,
            tipo_inmueble=tipo_inmueble,
            comprador=comprador,
            correo_comprador=correo_comprador,
            realtor_vendedor=realtor_vendedor,
            valor_comision=valor_comision,
            fecha_venta=fecha_venta,
            precio_propiedad=precio_propiedad  # Agregar el precio de la propiedad
        )
        inmueble.estado_publicacion = 'vendido'
        # Guardar el nuevo registro en la base de datos
        db.session.add(nuevo_vendido)
        db.session.commit()

        flash('Inmueble vendido registrado exitosamente', 'success')
        return redirect(url_for('main.dashboard'))  # Redirige al dashboard después de registrar

    return render_template('crear-vendidos.html', tipo_inmueble=tipo_inmueble, id=id, user=user)

#ruta para crear alquilados 
@main_routes.route('/crearalquilados/<string:tipo_inmueble>/<int:id>', methods=['GET', 'POST'])
def crear_alquilados(tipo_inmueble, id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Verifica si el usuario está logueado
    
    user_id = session['user_id']  # Obtener el usuario logueado
    user = User.query.get(user_id) 

    # Obtener la propiedad por el tipo de inmueble y ID
    if tipo_inmueble == "casa":
        inmueble = Casa.query.get(id)
    elif tipo_inmueble == "apartamento":
        inmueble = Apartamento.query.get(id)
    elif tipo_inmueble == "terreno":
        inmueble = Terreno.query.get(id)
    elif tipo_inmueble == "galpon":
        inmueble = Galpon.query.get(id)
    elif tipo_inmueble == "comercio":
        inmueble = Comercio.query.get(id)
    else:
        flash('Tipo de inmueble no reconocido.', 'danger')
        return redirect(url_for('main.dashboard'))  # Redirige si el tipo es incorrecto
    
    # Verificar si el tipo de negocio es 'Alquiler' o 'Venta y Alquiler'
    if inmueble.tipo_negocio not in ['Alquiler', 'Venta y Alquiler']:
        flash('No puede alquilar esta propiedad. El tipo de negocio no es adecuado.', 'danger')
        return redirect(url_for('main.dashboard'))  # Redirige si el tipo de negocio no es adecuado
    
    if request.method == 'POST':
        # Obtener los datos del formulario
        arrendatario = request.form['arrendatario']
        correo_arrendatario = request.form['correo_arrendatario']
        realtor_vendedor = request.form['realtor_vendedor']
        valor_comision = float(request.form['valor_comision']) if request.form['valor_comision'] else None
        
        # Obtener el precio de la propiedad
        precio_alquiler = float(request.form['precio_alquiler']) if request.form['precio_alquiler'] else None
        # Crear un nuevo registro en la tabla 'alquilados'
        nuevo_alquilado = Alquilados(
            id_del_inmueble=id,
            tipo_inmueble=tipo_inmueble,
            arrendatario=arrendatario,
            correo_arrendatario=correo_arrendatario,
            realtor_vendedor=realtor_vendedor,
            valor_comision=valor_comision,
            precio_alquiler=precio_alquiler
        )

        # Cambiar el estado de publicación del inmueble a "alquilado"
        inmueble.estado_publicacion = 'alquilado'
        # Guardar el nuevo registro en la base de datos
        db.session.add(nuevo_alquilado)
        db.session.commit()

        flash('Inmueble alquilado registrado exitosamente', 'success')
        return redirect(url_for('main.dashboard'))  # Redirige al dashboard después de registrar

    return render_template('crear-alquilados.html', tipo_inmueble=tipo_inmueble, user=user, id=id)

@main_routes.route('/vendidos', methods=['GET'])
def vendidos():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Verifica si el usuario está logueado

    user_id = session['user_id']  # Obtener el usuario logueado
    user = User.query.get(user_id)
    # Recuperamos los inmuebles vendidos
    inmuebles_vendidos = db.session.query(Vendidos).all()

    inmuebles_detalle = []

    # Ahora obtenemos el detalle de cada inmueble según su tipo
    for inmueble in inmuebles_vendidos:
        tipo_inmueble = inmueble.tipo_inmueble
        inmueble_id = inmueble.id_del_inmueble

        # Consulta dependiendo del tipo de inmueble (id se refiere a la columna id en cada tabla)
        if tipo_inmueble == "casa":
            inmueble_detalle = Casa.query.get(inmueble_id)
        elif tipo_inmueble == "apartamento":
            inmueble_detalle = Apartamento.query.get(inmueble_id)
        elif tipo_inmueble == "galpon":
            inmueble_detalle = Galpon.query.get(inmueble_id)
        elif tipo_inmueble == "terreno":
            inmueble_detalle = Terreno.query.get(inmueble_id)
        elif tipo_inmueble == "local":
            inmueble_detalle = Local.query.get(inmueble_id)
        elif tipo_inmueble == "comercio":
            inmueble_detalle = Comercio.query.get(inmueble_id)
        else:
            inmueble_detalle = None

        # Si encontramos el inmueble, lo agregamos a la lista
        if inmueble_detalle:
            inmuebles_detalle.append(inmueble_detalle)

        

    # Pasamos la lista de inmuebles detallados a la plantilla
    return render_template('vendidos.html', inmuebles=inmuebles_detalle,user=user)

#ruta para ver alquilados 
@main_routes.route('/alquilados', methods=['GET'])
def alquilados():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Verifica si el usuario está logueado

    user_id = session['user_id']  # Obtener el usuario logueado
    user = User.query.get(user_id)
    # Recuperamos los inmuebles alquilados
    inmuebles_alquilados = db.session.query(Alquilados).all()

    inmuebles_detalle = []

    # Ahora obtenemos el detalle de cada inmueble según su tipo
    for inmueble in inmuebles_alquilados:
        tipo_inmueble = inmueble.tipo_inmueble
        inmueble_id = inmueble.id_del_inmueble

        # Consulta dependiendo del tipo de inmueble (id se refiere a la columna id en cada tabla)
        if tipo_inmueble == "casa":
            inmueble_detalle = Casa.query.get(inmueble_id)
        elif tipo_inmueble == "apartamento":
            inmueble_detalle = Apartamento.query.get(inmueble_id)
        elif tipo_inmueble == "galpon":
            inmueble_detalle = Galpon.query.get(inmueble_id)
        elif tipo_inmueble == "terreno":
            inmueble_detalle = Terreno.query.get(inmueble_id)
        elif tipo_inmueble == "local":
            inmueble_detalle = Local.query.get(inmueble_id)
        elif tipo_inmueble == "comercio":
            inmueble_detalle = Comercio.query.get(inmueble_id)
        
        
        else:
            inmueble_detalle = None

        # Si encontramos el inmueble, lo agregamos a la lista
        if inmueble_detalle:
            inmuebles_detalle.append(inmueble_detalle)

    # Pasamos la lista de inmuebles detallados a la plantilla
    return render_template('alquilados.html', inmuebles=inmuebles_detalle, user=user)

#ruta para las negociaciones

@main_routes.route('/crearnegociacion/<string:tipo_inmueble>/<int:id>', methods=['GET', 'POST'])
def crear_negociacion(tipo_inmueble, id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Verifica si el usuario está logueado

    user_id = session['user_id']  # Obtener el usuario logueado
    user = User.query.get(user_id)

    if tipo_inmueble == "casa":
        inmueble = Casa.query.get(id)
    elif tipo_inmueble == "apartamento":
        inmueble = Apartamento.query.get(id)
    elif tipo_inmueble == "terreno":
        inmueble = Terreno.query.get(id)
    elif tipo_inmueble == "galpon":
        inmueble = Galpon.query.get(id)
    elif tipo_inmueble == "comercio":
        inmueble = Comercio.query.get(id)
    else:
        flash('Tipo de inmueble no reconocido.', 'danger')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        cliente = request.form['cliente']
        realtor = request.form['realtor']
        monto = float(request.form['monto']) if request.form['monto'] else 0.0
        descripcion = request.form['descripcion']

        nueva_negociacion = Negociacion(
            id_inmueble=id,
            tipo_inmueble=tipo_inmueble,
            monto=monto,
            cliente=cliente,
            realtor=realtor,
            descripcion=descripcion
        )

        inmueble.estado_publicacion = 'negociacion'

        db.session.add(nueva_negociacion)
        db.session.commit()

        flash('Negociación registrada exitosamente.', 'success')
        return redirect(url_for('main.dashboard'))

    # 👉 Aquí agregamos tipo_inmueble e id
    return render_template('crear_negociacion.html', inmueble=inmueble, tipo_inmueble=tipo_inmueble,user=user, id=id)

#ruta para ver al negociaciones 
@main_routes.route('/negociaciones', methods=['GET'])
def negociacion():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Verifica si el usuario está logueado
    
    user_id = session['user_id']  # Obtener el usuario logueado
    user = User.query.get(user_id)

    # Recuperamos los inmuebles alquilados
    inmuebles_alquilados = db.session.query(Negociacion).all()

    inmuebles_detalle = []

    # Ahora obtenemos el detalle de cada inmueble según su tipo
    for inmueble in inmuebles_alquilados:
        tipo_inmueble = inmueble.tipo_inmueble
        inmueble_id = inmueble.id_inmueble

        # Consulta dependiendo del tipo de inmueble (id se refiere a la columna id en cada tabla)
        if tipo_inmueble == "casa":
            inmueble_detalle = Casa.query.get(inmueble_id)
        elif tipo_inmueble == "apartamento":
            inmueble_detalle = Apartamento.query.get(inmueble_id)
        elif tipo_inmueble == "galpon":
            inmueble_detalle = Galpon.query.get(inmueble_id)
        elif tipo_inmueble == "terreno":
            inmueble_detalle = Terreno.query.get(inmueble_id)
        elif tipo_inmueble == "local":
            inmueble_detalle = Local.query.get(inmueble_id)
        elif tipo_inmueble == "comercio":
            inmueble_detalle = Comercio.query.get(inmueble_id)
        
        
        else:
            inmueble_detalle = None

        # Si encontramos el inmueble, lo agregamos a la lista
        if inmueble_detalle:
            inmuebles_detalle.append(inmueble_detalle)

    # Pasamos la lista de inmuebles detallados a la plantilla
    return render_template('negociacion.html', inmuebles=inmuebles_detalle, user=user)






#crear talleres

@main_routes.route('/crear_taller', methods=['GET', 'POST'])
def crear_taller():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Redirige al login si no hay usuario en sesión
    
    user_id = session['user_id']
    user = User.query.get(user_id)  # Obtener el usuario desde la base de datos

    if user and user.rol == 'administrador':  # Solo los administradores pueden crear talleres
        if request.method == 'POST':
            # Obtener los datos del formulario
            titulo = request.form['titulo']
            ubicacion = request.form['ubicacion']
            fecha_hora = request.form['fecha_hora']

            # Convertir la fecha y hora a un objeto datetime
            try:
                fecha_hora = datetime.strptime(fecha_hora, '%Y-%m-%dT%H:%M')  # Formato 'YYYY-MM-DDTHH:MM'
            except ValueError:
                flash('Formato de fecha y hora no válido.', 'danger')
                return render_template('crear-taller.html', user=user)

            # Crear un nuevo taller
            nuevo_taller = Talleres(titulo=titulo, ubicacion=ubicacion, fecha_hora=fecha_hora)
            db.session.add(nuevo_taller)
            db.session.commit()
            flash('Taller creado con éxito', 'success')
            return redirect(url_for('main.dashboard'))  # Redirige al dashboard después de crear el taller

        return render_template('crear-taller.html', user=user)  # Muestra el formulario de creación de taller
    else:
        flash('Acceso no autorizado o usuario no válido', 'danger')
        return redirect(url_for('main.login'))  # Redirige a login si el usuario no es admin


@main_routes.route('/activar/<string:tipo_inmueble>/<int:id>', methods=['GET'])
def activar_inmueble(tipo_inmueble, id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))  # Verifica si el usuario está logueado

    # Obtener el modelo correcto según el tipo de inmueble
    if tipo_inmueble == "casa":
        inmueble = Casa.query.get(id)
    elif tipo_inmueble == "apartamento":
        inmueble = Apartamento.query.get(id)
    elif tipo_inmueble == "terreno":
        inmueble = Terreno.query.get(id)
    elif tipo_inmueble == "galpon":
        inmueble = Galpon.query.get(id)
    elif tipo_inmueble == "comercio":
        inmueble = Comercio.query.get(id)
    else:
        flash('Tipo de inmueble no reconocido.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Cambiar el estado a "Activo"
    inmueble.estado_publicacion = 'Activo'
    
    try:
        db.session.commit()
        flash('Inmueble activado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al activar el inmueble', 'danger')
        
    
    return redirect(url_for('main.dashboard'))


#ruta para cerrar sesion 
@main_routes.route('/logout')
def logout():
    # Verificar si hay un usuario logueado antes de cerrar sesión
    if 'user_id' in session:
        flash('Has cerrado sesión correctamente.', 'info')
    
    # Limpiar toda la información de la sesión
    session.clear()
    
    # Redirigir a la página principal o de login
    return redirect(url_for('main.login'))

# --- EDITAR CASA ---
@main_routes.route('/editar-casa/<int:id>', methods=['GET', 'POST'])
def editar_casa(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    user = User.query.get(user_id)
    casa = Casa.query.get_or_404(id)
    if request.method == 'POST':
        data = request.form

        # Procesar imágenes eliminadas y actuales
        imagenes_eliminar = request.form.getlist('imagenes_eliminar[]')
        imagenes_actuales = request.form.getlist('imagenes_actuales[]')

        # Procesar nuevas imágenes subidas
        nuevas_imagenes = []
        if 'imagenes' in request.files:
            archivos = request.files.getlist('imagenes')
            for archivo in archivos:
                if archivo and archivo.filename:
                    filename = secure_filename(archivo.filename)
                    ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    archivo.save(ruta)
                    nuevas_imagenes.append(filename)

        # Eliminar físicamente las imágenes marcadas para eliminar
        for img_nombre in imagenes_eliminar:
            img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], img_nombre)
            if os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except Exception as e:
                    print(f"No se pudo eliminar {img_path}: {e}")

        # Actualizar la lista de imágenes en la base de datos
        imagenes_finales = imagenes_actuales + nuevas_imagenes
        casa.imagen_principal = ','.join(imagenes_finales)

        # Procesar imagen_cedula y documento_propiedad
        imagen_cedula_file = request.files.get('imagen_cedula')
        if imagen_cedula_file and imagen_cedula_file.filename:
            casa.imagen_cedula = guardar_archivo(imagen_cedula_file)
        # Si no se sube nada, se mantiene el valor anterior

        documento_propiedad_file = request.files.get('documento_propiedad')
        if documento_propiedad_file and documento_propiedad_file.filename:
            casa.documento_propiedad = guardar_archivo(documento_propiedad_file)
        # Si no se sube nada, se mantiene el valor anterior

        def safe_int(val):
            return int(val) if val not in (None, '', 'None') else None
        def safe_float(val):
            return float(val) if val not in (None, '', 'None') else None
        casa.nombre = data['nombre']
        casa.apellido = data['apellido']
        casa.ci = data['ci']
        casa.rif = data.get('rif')
        casa.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d') if data.get('fecha_nacimiento') else None
        casa.estado_civil = data.get('estado_civil')
        casa.email = data['email']
        casa.telefono = data.get('telefono')
        casa.titulo_propiedad = data['titulo_propiedad']
        casa.destacado = 'destacado' in data
        casa.tipo_inmueble = data.get('tipo_inmueble', 'Casa')
        casa.datos_inmueble = data.get('datos_inmueble')
        casa.referencia = data.get('referencia')
        casa.habitaciones = safe_int(data.get('habitaciones'))
        casa.hab_servicio = safe_int(data.get('hab_servicio'))
        casa.total_habitaciones = safe_int(data.get('total_habitaciones'))
        casa.banos_completos = safe_int(data.get('banos_completos'))
        casa.bano_servicio = safe_int(data.get('bano_servicio'))
        casa.medio_bano = safe_int(data.get('medio_bano'))
        casa.total_banos = safe_int(data.get('total_banos'))
        casa.puestos_estacionamiento = safe_int(data.get('puestos_estacionamiento'))
        casa.estacionamientos_cubiertos = safe_int(data.get('estacionamientos_cubiertos'))
        casa.estacionamientos_descubiertos = safe_int(data.get('estacionamientos_descubiertos'))
        casa.tiene_maletero = 'tiene_maletero' in data
        casa.cantidad_maleteros = safe_int(data.get('cantidad_maleteros'))
        casa.metros_construccion = safe_float(data.get('metros_construccion'))
        casa.metros_terreno = safe_float(data.get('metros_terreno'))
        casa.anio_construccion = safe_int(data.get('anio_construccion'))
        casa.obra = data.get('obra')
        casa.estilo = data.get('estilo')
        casa.tiene_terraza = 'tiene_terraza' in data
        casa.tipo_piso = data.get('tipo_piso')
        casa.niveles = safe_int(data.get('niveles'))
        casa.pais = data.get('pais')
        casa.estado_departamento = data.get('estado_departamento')
        casa.ciudad = data.get('ciudad')
        casa.direccion = data.get('direccion')
        casa.codigo_postal = data.get('codigo_postal')
        casa.areas_internas = ','.join(request.form.getlist('areas_internas'))
        casa.areas_comunes = ','.join(request.form.getlist('areas_comunes'))
        casa.comodidades = ','.join(request.form.getlist('comodidades'))
        casa.servicio_telefonia_fija = ','.join(request.form.getlist('telefonia'))
        casa.servicio_cable = ','.join(request.form.getlist('cablevision'))
        casa.servicio_internet = ','.join(request.form.getlist('servicios_internet'))
        casa.condominio_aprox = safe_float(data.get('condominio_aprox'))
        casa.precio = safe_float(data['precio'])
        casa.tipo_negocio = data.get('tipo_negocio')
        db.session.commit()
        flash('Casa actualizada con éxito.', 'success')
        return redirect(url_for('main.lista_inmuebles'))
    return render_template('editar-casa.html', casa=casa, user=user)

# --- EDITAR APARTAMENTO ---
@main_routes.route('/editar-apartamento/<int:id>', methods=['GET', 'POST'])
def editar_apartamento(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    user = User.query.get(user_id)
    apartamento = Apartamento.query.get_or_404(id)
    if request.method == 'POST':
        data = request.form
        imagenes_eliminar = request.form.getlist('imagenes_eliminar[]')
        imagenes_actuales = request.form.getlist('imagenes_actuales[]')
        nuevas_imagenes = []
        if 'imagenes' in request.files:
            archivos = request.files.getlist('imagenes')
            for archivo in archivos:
                if archivo and archivo.filename:
                    filename = secure_filename(archivo.filename)
                    ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    archivo.save(ruta)
                    nuevas_imagenes.append(filename)
        for img_nombre in imagenes_eliminar:
            img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], img_nombre)
            if os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except Exception as e:
                    print(f"No se pudo eliminar {img_path}: {e}")
        imagenes_finales = imagenes_actuales + nuevas_imagenes
        apartamento.imagen_principal = ','.join(imagenes_finales)
        # Procesar imagen_cedula y documento_propiedad
        imagen_cedula_file = request.files.get('imagen_cedula')
        if imagen_cedula_file and imagen_cedula_file.filename:
            apartamento.imagen_cedula = guardar_archivo(imagen_cedula_file)
        documento_propiedad_file = request.files.get('documento_propiedad')
        if documento_propiedad_file and documento_propiedad_file.filename:
            apartamento.documento_propiedad = guardar_archivo(documento_propiedad_file)
        def safe_int(val):
            return int(val) if val not in (None, '', 'None') else None
        def safe_float(val):
            return float(val) if val not in (None, '', 'None') else None
        apartamento.nombre = data['nombre']
        apartamento.apellido = data['apellido']
        apartamento.ci = data['ci']
        apartamento.rif = data.get('rif')
        apartamento.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d') if data.get('fecha_nacimiento') else None
        apartamento.estado_civil = data.get('estado_civil')
        apartamento.email = data['email']
        apartamento.telefono = data.get('telefono')
        apartamento.titulo_propiedad = data['titulo_propiedad']
        apartamento.tipo_inmueble = data.get('tipo_inmueble', 'Apartamento')
        apartamento.datos_inmueble = data.get('datos_inmueble')
        apartamento.referencia = data.get('referencia')
        apartamento.habitaciones = safe_int(data.get('habitaciones'))
        apartamento.hab_servicio = safe_int(data.get('hab_servicio'))
        apartamento.total_habitaciones = safe_int(data.get('total_habitaciones'))
        apartamento.banos_completos = safe_int(data.get('banos_completos'))
        apartamento.bano_servicio = safe_int(data.get('bano_servicio'))
        apartamento.medio_bano = safe_int(data.get('medio_bano'))
        apartamento.total_banos = safe_int(data.get('total_banos'))
        apartamento.puestos_estacionamiento = safe_int(data.get('puestos_estacionamiento'))
        apartamento.estacionamientos_cubiertos = safe_int(data.get('estacionamientos_cubiertos'))
        apartamento.estacionamientos_descubiertos = safe_int(data.get('estacionamientos_descubiertos'))
        apartamento.tiene_maletero = 'tiene_maletero' in data
        apartamento.cantidad_maleteros = safe_int(data.get('cantidad_maleteros'))
        apartamento.metros_construccion = safe_float(data.get('metros_construccion'))
        apartamento.metros_terreno = safe_float(data.get('metros_terreno'))
        apartamento.anio_construccion = safe_int(data.get('anio_construccion'))
        apartamento.obra = data.get('obra')
        apartamento.estilo = data.get('estilo')
        apartamento.tiene_terraza = 'tiene_terraza' in data
        apartamento.tipo_piso = data.get('tipo_piso')
        apartamento.niveles = safe_int(data.get('niveles'))
        apartamento.pais = data.get('pais')
        apartamento.estado_departamento = data.get('estado_departamento')
        apartamento.ciudad = data.get('ciudad')
        apartamento.direccion = data.get('direccion')
        apartamento.codigo_postal = data.get('codigo_postal')
        apartamento.areas_internas = ','.join(request.form.getlist('areas_internas'))
        apartamento.areas_comunes = ','.join(request.form.getlist('areas_comunes'))
        apartamento.comodidades = ','.join(request.form.getlist('comodidades'))
        apartamento.servicio_telefonia_fija = ','.join(request.form.getlist('telefonia'))
        apartamento.servicio_cable = ','.join(request.form.getlist('cablevision'))
        apartamento.servicio_internet = ','.join(request.form.getlist('internet'))
        apartamento.condominio_aprox = safe_float(data.get('condominio_aprox'))
        apartamento.precio = safe_float(data['precio'])
        apartamento.tipo_negocio = data.get('tipo_negocio')
        db.session.commit()
        flash('Apartamento actualizado con éxito.', 'success')
        return redirect(url_for('main.lista_inmuebles'))
    return render_template('editar-apartamento.html', apartamento=apartamento, user=user)

# --- EDITAR TERRENO ---
@main_routes.route('/editar-terreno/<int:id>', methods=['GET', 'POST'])
def editar_terreno(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    user = User.query.get(user_id)
    terreno = Terreno.query.get_or_404(id)
    if request.method == 'POST':
        data = request.form
        # Procesar imágenes eliminadas y actuales
        imagenes_eliminar = request.form.getlist('imagenes_eliminar[]')
        imagenes_actuales = request.form.getlist('imagenes_actuales[]')
        # Procesar nuevas imágenes subidas
        nuevas_imagenes = []
        if 'imagenes' in request.files:
            archivos = request.files.getlist('imagenes')
            for archivo in archivos:
                if archivo and archivo.filename:
                    filename = secure_filename(archivo.filename)
                    ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    archivo.save(ruta)
                    nuevas_imagenes.append(filename)
        # Eliminar físicamente las imágenes marcadas para eliminar
        for img_nombre in imagenes_eliminar:
            if img_nombre:
                ruta_img = os.path.join(current_app.config['UPLOAD_FOLDER'], img_nombre)
                if os.path.exists(ruta_img):
                    os.remove(ruta_img)
        # Construir la lista final de imágenes
        imagenes_finales = imagenes_actuales + nuevas_imagenes
        terreno.imagen_principal = ','.join(imagenes_finales)
        def safe_int(val):
            return int(val) if val not in (None, '', 'None') else None
        def safe_float(val):
            return float(val) if val not in (None, '', 'None') else None
        terreno.titulo_publicacion = data['titulo_publicacion']
        terreno.tipo_inmueble = data['tipo_inmueble']
        terreno.nombre = data['nombre']
        terreno.apellido = data['apellido']
        terreno.ci = data['ci']
        terreno.rif = data.get('rif')
        terreno.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d') if data.get('fecha_nacimiento') else None
        terreno.estado_civil = data.get('estado_civil')
        terreno.email = data['email']
        terreno.telefono = data.get('telefono')
        terreno.estado = data['estado']
        terreno.municipio = data['municipio']
        terreno.ciudad = data['ciudad']
        terreno.urbanizacion = data['urbanizacion']
        terreno.referencia = data.get('referencia')
        terreno.m2_terreno = safe_float(data.get('m2_terreno'))
        terreno.m2_construccion = safe_float(data.get('m2_construccion'))
        terreno.m_frente = safe_float(data.get('m_frente'))
        terreno.m_anch = safe_float(data.get('m_anch'))
        terreno.m_largo = safe_float(data.get('m_largo'))
        terreno.cerca_perimetral = data.get('cerca_perimetral')
        terreno.bienechurias = data.get('bienechurias')
        terreno.otros = data.get('otros')
        terreno.materiales = ','.join(request.form.getlist('materiales'))
        terreno.precio = safe_float(data.get('precio'))
        terreno.comision = safe_float(data.get('comision'))
        db.session.commit()
        flash('Terreno actualizado con éxito.', 'success')
        return redirect(url_for('main.lista_inmuebles'))
    return render_template('editar-terreno.html', terreno=terreno, user=user)

# --- EDITAR GALPON ---
@main_routes.route('/editar-galpon/<int:id>', methods=['GET', 'POST'])
def editar_galpon(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    user = User.query.get(user_id)
    galpon = Galpon.query.get_or_404(id)
    if request.method == 'POST':
        data = request.form
        imagenes_eliminar = request.form.getlist('imagenes_eliminar[]')
        imagenes_actuales = request.form.getlist('imagenes_actuales[]')
        nuevas_imagenes = []
        if 'imagenes' in request.files:
            archivos = request.files.getlist('imagenes')
            for archivo in archivos:
                if archivo and archivo.filename:
                    filename = secure_filename(archivo.filename)
                    ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    archivo.save(ruta)
                    nuevas_imagenes.append(filename)
        for img_nombre in imagenes_eliminar:
            img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], img_nombre)
            if os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except Exception as e:
                    print(f"No se pudo eliminar {img_path}: {e}")
        imagenes_finales = imagenes_actuales + nuevas_imagenes
        galpon.imagen_principal = ','.join(imagenes_finales)
        # Procesar imagen_cedula y documento_propiedad
        imagen_cedula_file = request.files.get('imagen_cedula')
        if imagen_cedula_file and imagen_cedula_file.filename:
            galpon.imagen_cedula = guardar_archivo(imagen_cedula_file)
        documento_propiedad_file = request.files.get('documento_propiedad')
        if documento_propiedad_file and documento_propiedad_file.filename:
            galpon.documento_propiedad = guardar_archivo(documento_propiedad_file)
        def safe_int(val):
            return int(val) if val not in (None, '', 'None') else None
        def safe_float(val):
            return float(val) if val not in (None, '', 'None') else None
        galpon.nombre = data['nombre']
        galpon.apellido = data['apellido']
        galpon.ci = data['ci']
        galpon.rif = data.get('rif')
        galpon.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d') if data.get('fecha_nacimiento') else None
        galpon.estado_civil = data.get('estado_civil')
        galpon.email = data['email']
        galpon.telefono = data.get('telefono')
        galpon.titulo_propiedad = data['titulo_propiedad']
        galpon.destacado = 'destacado' in data
        galpon.tipo_inmueble = data['tipo_inmueble']
        galpon.datos_inmueble = data['datos_inmueble']
        galpon.referencia = data['referencia']
        galpon.oficinas = safe_int(data.get('oficinas'))
        galpon.galpon = data.get('galpon')
        galpon.banos_completos = safe_int(data.get('banos_completos'))
        galpon.banos_servicio = safe_int(data.get('bano_servicio'))
        galpon.medio_bano = safe_int(data.get('medio_bano'))
        galpon.area_descanso = data['area_descanso'] or None
        galpon.puestos_estacionamiento = safe_int(data.get('puestos_estacionamiento'))
        galpon.cubierto = data.get('cubierto')
        galpon.amoblado = data['amoblado'] or None
        galpon.kitchenette = data['kitchenette'] or None
        galpon.patio_trabajo = data['patio_trabajo'] or None
        galpon.m_frente = safe_float(data.get('m_frente'))
        galpon.total_banos = safe_int(data.get('total_banos'))
        galpon.descubierto = data['estacionamientos_descubiertos'] or None
        galpon.vigilancia = data['vigilancia'] or None
        galpon.m_fondo = safe_float(data.get('m_fondo'))
        galpon.estacionamiento_visitantes = data['estacionamiento_visitantes'] or None
        galpon.m_altura = safe_float(data.get('m_altura'))
        galpon.centro_comercial = data['centro_comercial'] or None
        galpon.m2_terreno = safe_float(data.get('m2_terreno'))
        galpon.anos_construccion = safe_int(data.get('anos_construccion'))
        galpon.parque_industrial = data['parque_industrial'] or None
        galpon.m2_construccion = safe_float(data.get('m2_construccion'))
        galpon.condominio_aprox = safe_float(data.get('condominio_aprox'))
        galpon.pais = data.get('pais')
        galpon.estado_departamento = data.get('estado_departamento')
        galpon.ciudad = data.get('ciudad')
        galpon.direccion = data.get('direccion')
        galpon.codigo_postal = data.get('codigo_postal')
        galpon.areas_internas = ','.join(request.form.getlist('areas_internas'))
        galpon.comodidades = ','.join(request.form.getlist('comodidades'))
        galpon.servicio_telefonia_fija = ','.join(request.form.getlist('telefonia'))
        galpon.servicio_cable = ','.join(request.form.getlist('cablevision'))
        galpon.servicio_internet = ','.join(request.form.getlist('internet'))
        galpon.precio = safe_float(data.get('precio'))
        galpon.comision = safe_float(data.get('comision'))
        galpon.tipo_negocio = data.get('tipo_negocio')
        db.session.commit()
        flash('Galpón actualizado con éxito.', 'success')
        return redirect(url_for('main.lista_inmuebles'))
    return render_template('editar-galpon.html', galpon=galpon, user=user)

# --- EDITAR LOCAL ---
@main_routes.route('/editar-local/<int:id>', methods=['GET', 'POST'])
def editar_local(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    user = User.query.get(user_id)
    local = Local.query.get_or_404(id)
    if request.method == 'POST':
        data = request.form
        imagenes_eliminar = request.form.getlist('imagenes_eliminar[]')
        imagenes_actuales = request.form.getlist('imagenes_actuales[]')
        nuevas_imagenes = []
        if 'imagenes' in request.files:
            archivos = request.files.getlist('imagenes')
            for archivo in archivos:
                if archivo and archivo.filename:
                    filename = secure_filename(archivo.filename)
                    ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    archivo.save(ruta)
                    nuevas_imagenes.append(filename)
        for img_nombre in imagenes_eliminar:
            img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], img_nombre)
            if os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except Exception as e:
                    print(f"No se pudo eliminar {img_path}: {e}")
        imagenes_finales = imagenes_actuales + nuevas_imagenes
        local.imagen_principal = ','.join(imagenes_finales)
        # Procesar imagen_cedula y documento_propiedad
        imagen_cedula_file = request.files.get('imagen_cedula')
        if imagen_cedula_file and imagen_cedula_file.filename:
            local.imagen_cedula = guardar_archivo(imagen_cedula_file)
        documento_propiedad_file = request.files.get('documento_propiedad')
        if documento_propiedad_file and documento_propiedad_file.filename:
            local.documento_propiedad = guardar_archivo(documento_propiedad_file)
        def safe_int(val):
            return int(val) if val not in (None, '', 'None') else None
        def safe_float(val):
            return float(val) if val not in (None, '', 'None') else None
        
        # Datos básicos
        local.nombre = data['nombre']
        local.apellido = data['apellido']
        local.ci = data['ci']
        local.rif = data.get('rif')
        local.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d') if data.get('fecha_nacimiento') else None
        local.estado_civil = data.get('estado_civil')
        local.email = data['email']
        local.telefono = data.get('telefono')
        
        # Datos del inmueble
        local.titulo_propiedad = data['titulo_propiedad']
        local.tipo_inmueble = data['tipo_inmueble']
        local.datos_inmueble = data['datos_inmueble']
        local.referencia = data['referencia']
        
        # Ubicación
        local.pais = data.get('pais')
        local.estado_departamento = data.get('estado_departamento')
        local.ciudad = data.get('ciudad')
        local.direccion = data.get('direccion')
        local.codigo_postal = data.get('codigo_postal')
        
        # Características específicas
        local.banos_completos = safe_int(data.get('banos_completos'))
        local.bano_servicio = safe_int(data.get('bano_servicio'))
        local.medio_bano = safe_int(data.get('medio_bano'))
        local.total_banos = safe_int(data.get('total_banos'))
        local.area_descanso = data.get('area_descanso')
        local.puestos_estacionamiento = safe_int(data.get('puestos_estacionamiento'))
        local.cubierto = data.get('cubierto')
        local.descubierto = data.get('descubierto')
        local.estacionamiento_visitantes = data.get('estacionamiento_visitantes')
        local.amoblado = data.get('amoblado')
        local.patio_trabajo = data.get('patio_trabajo')
        
        # Medidas
        local.m_frente = safe_float(data.get('m_frente'))
        local.m_fondo = safe_float(data.get('m_fondo'))
        local.m_altura = safe_float(data.get('m_altura'))
        local.m2_terreno = safe_float(data.get('m2_terreno'))
        local.m2_construccion = safe_float(data.get('m2_construccion'))
        local.anos_construccion = safe_int(data.get('anos_construccion'))
        local.condominio_aprox = safe_float(data.get('condominio_aprox'))
        
        # Servicios
        local.areas_internas = ','.join(request.form.getlist('areas_internas'))
        local.comodidades = ','.join(request.form.getlist('comodidades'))
        local.telefonia = ','.join(request.form.getlist('telefonia'))
        local.cablevision = ','.join(request.form.getlist('cablevision'))
        local.internet = ','.join(request.form.getlist('internet'))
        
        # Precio y tipo de negocio
        local.precio = safe_float(data.get('precio'))
        local.comision = safe_float(data.get('comision'))
        local.tipo_negocio = data.get('tipo_negocio')
        
        # Destacado
        local.destacado = 'destacado' in data
        
        db.session.commit()
        flash('Local actualizado con éxito.', 'success')
        return redirect(url_for('main.lista_inmuebles'))
    return render_template('crear-inmueble-local.html', local=local, user=user)

# --- EDITAR COMERCIO ---
@main_routes.route('/editar-comercio/<int:id>', methods=['GET', 'POST'])
def editar_comercio(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    user = User.query.get(user_id)
    comercio = Comercio.query.get_or_404(id)
    if request.method == 'POST':
        data = request.form
        imagenes_eliminar = request.form.getlist('imagenes_eliminar[]')
        imagenes_actuales = request.form.getlist('imagenes_actuales[]')
        nuevas_imagenes = []
        if 'imagenes' in request.files:
            archivos = request.files.getlist('imagenes')
            for archivo in archivos:
                if archivo and archivo.filename:
                    filename = secure_filename(archivo.filename)
                    ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    archivo.save(ruta)
                    nuevas_imagenes.append(filename)
        for img_nombre in imagenes_eliminar:
            img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], img_nombre)
            if os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except Exception as e:
                    print(f"No se pudo eliminar {img_path}: {e}")
        imagenes_finales = imagenes_actuales + nuevas_imagenes
        comercio.imagen_principal = ','.join(imagenes_finales)
        # Procesar imagen_cedula y documento_propiedad
        imagen_cedula_file = request.files.get('imagen_cedula')
        if imagen_cedula_file and imagen_cedula_file.filename:
            comercio.imagen_cedula = guardar_archivo(imagen_cedula_file)
        documento_propiedad_file = request.files.get('documento_propiedad')
        if documento_propiedad_file and documento_propiedad_file.filename:
            comercio.documento_propiedad = guardar_archivo(documento_propiedad_file)
        def safe_int(val):
            return int(val) if val not in (None, '', 'None') else None
        def safe_float(val):
            return float(val) if val not in (None, '', 'None') else None
        
        # Datos básicos
        comercio.nombre = data['nombre']
        comercio.apellido = data['apellido']
        comercio.ci = data['ci']
        comercio.rif = data.get('rif')
        comercio.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d') if data.get('fecha_nacimiento') else None
        comercio.estado_civil = data.get('estado_civil')
        comercio.email = data['email']
        comercio.telefono = data.get('telefono')
        
        # Datos del inmueble
        comercio.titulo_propiedad = data['titulo_propiedad']
        comercio.tipo_inmueble = data['tipo_inmueble']
        comercio.datos_inmueble = data['datos_inmueble']
        comercio.referencia = data['referencia']
        
        # Ubicación
        comercio.pais = data.get('pais')
        comercio.estado_departamento = data.get('estado_departamento')
        comercio.ciudad = data.get('ciudad')
        comercio.direccion = data.get('direccion')
        comercio.codigo_postal = data.get('codigo_postal')
        
        # Características específicas
        comercio.oficinas = safe_int(data.get('oficinas'))
        comercio.ambientes = safe_int(data.get('ambientes'))
        comercio.banos_completos = safe_int(data.get('banos_completos'))
        comercio.bano_servicio = safe_int(data.get('bano_servicio'))
        comercio.medio_bano = safe_int(data.get('medio_bano'))
        comercio.total_banos = safe_int(data.get('total_banos'))
        comercio.area_descanso = data.get('area_descanso')
        comercio.puestos_estacionamiento = safe_int(data.get('puestos_estacionamiento'))
        comercio.cubierto = data.get('cubierto')
        comercio.descubierto = data.get('descubierto')
        comercio.estacionamiento_visitantes = data.get('estacionamiento_visitantes')
        comercio.amoblado = data.get('amoblado')
        
        # Medidas
        comercio.m_frente = safe_float(data.get('m_frente'))
        comercio.m_fondo = safe_float(data.get('m_fondo'))
        comercio.m_altura = safe_float(data.get('m_altura'))
        comercio.m2_terreno = safe_float(data.get('m2_terreno'))
        comercio.m2_construccion = safe_float(data.get('m2_construccion'))
        comercio.anos_construccion = safe_int(data.get('anos_construccion'))
        comercio.condominio_aprox = safe_float(data.get('condominio_aprox'))
        
        # Datos comerciales
        comercio.razon_social = data.get('razon_social')
        comercio.anio_apertura = safe_int(data.get('anio_apertura'))
        comercio.punto_venta = 'punto_venta' in data
        comercio.maquinas_equipos = 'maquinas_equipos' in data
        comercio.mobiliario = 'mobiliario' in data
        comercio.lineas_telefonicas = 'lineas_telefonicas' in data
        comercio.rrss_activas = 'rrss_activas' in data
        comercio.sistema_fiscal = 'sistema_fiscal' in data
        comercio.pag_web_activa = 'pag_web_activa' in data
        comercio.contabilidad = 'contabilidad' in data
        
        # Servicios
        comercio.areas_internas = ','.join(request.form.getlist('areas_internas'))
        comercio.comodidades = ','.join(request.form.getlist('comodidades'))
        comercio.telefonia = ','.join(request.form.getlist('telefonia'))
        comercio.cablevision = ','.join(request.form.getlist('cablevision'))
        comercio.internet = ','.join(request.form.getlist('internet'))
        
        # Precio y tipo de negocio
        comercio.precio = safe_float(data.get('precio'))
        comercio.comision = safe_float(data.get('comision'))
        comercio.tipo_negocio = data.get('tipo_negocio')
        
        # Destacado
        comercio.destacado = 'destacado' in data
        
        db.session.commit()
        flash('Comercio actualizado con éxito.', 'success')
        return redirect(url_for('main.lista_inmuebles'))
    return render_template('crear-inmueble-comercio.html', comercio=comercio, user=user)

@main_routes.route('/resetear-contrasena/<int:id>', methods=['POST'])
def resetear_contrasena(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    usuario_logueado = User.query.get(user_id)
    if usuario_logueado.rol != 'administrador':
        flash('No tienes permisos para resetear contraseñas', 'danger')
        return redirect(url_for('main.lista_usuarios'))
    usuario = User.query.get(id)
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('main.lista_usuarios'))
    nueva_contrasena = '12345678'
    usuario.set_password(nueva_contrasena)
    db.session.commit()
    flash('Contraseña reseteada a 12345678', 'success')
    return redirect(url_for('main.lista_usuarios'))
