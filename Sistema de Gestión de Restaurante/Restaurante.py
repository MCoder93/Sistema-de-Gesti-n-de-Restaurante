# 🐺 Programación en Python

"""
Sistema de Administración de Restaurante
Autor: Marcos Soto / MCode-DevOps93
Descripción: Sistema completo para gestionar platillos y órdenes de un restaurante
con persistencia de datos en archivos .txt
"""


from datetime import datetime
import os

# ==================== CONFIGURACIÓN GLOBAL ====================
# Definición de las carpetas donde se almacenarán los archivos
CARPETA_PLATILLOS = 'restaurant/platillos/'           # Carpeta para guardar los platillos
CARPETA_ORDENES = 'restaurant/ordenes/'               # Carpeta para guardar las órdenes
CARPETA_ORDENES_GUARDADAS = 'Ordenes Guardadas/'      # Carpeta para guardar reportes de órdenes
CARPETA_CIERRE_CAJA = 'Cierre de caja/'               # Carpeta para guardar cierre de caja
EXTENSION = '.txt'                                     # Extensión de los archivos


# ==================== CLASE PLATILLO ====================
class Platillo:
    """
    Clase que representa un platillo del menú del restaurant
    """
    def __init__(self, id_platillo, nombre, precio, categoria):
        self.id_platillo = id_platillo
        self.nombre = nombre
        self.precio = precio
        self.categoria = categoria
        self.disponible = True

    def __str__(self):
        """Método para mostrar el platillo en formato legible"""
        estado = "✅ Disponible" if self.disponible else "❌ No disponible"
        return f"[{self.id_platillo}] {self.nombre} - ${self.precio:,.0f} ({self.categoria}) {estado}"


# ==================== CLASE ORDEN ====================
class Orden:
    """
    Clase que representa una orden del restaurant
    """
    def __init__(self, numero_orden, cliente):
        self.numero_orden = numero_orden
        self.cliente = cliente
        self.platillos = []
        self.fecha = datetime.now()
        self.total = 0

    def agregar_platillo(self, platillo, cantidad=1):
        """Agrega un platillo a la orden con su cantidad y calcula el subtotal"""
        self.platillos.append({
            'platillo': platillo,
            'cantidad': cantidad,
            'subtotal': platillo.precio * cantidad
        })
        self.total += platillo.precio * cantidad

    def __str__(self):
        """Método para mostrar la orden en formato legible"""
        fecha_str = self.fecha.strftime("%d/%m/%Y %H:%M")
        return f"Orden #{self.numero_orden} - {self.cliente} - ${self.total:,.0f} ({fecha_str})"


# ==================== CLASE CIERRE DE CAJA ====================
class CierreCaja:
    """
    Clase que representa un cierre de caja diario
    """
    def __init__(self, ordenes):
        self.fecha_cierre = datetime.now()
        self.ordenes = ordenes
        self.total_ordenes = len(ordenes)
        self.total_ingresos = sum(orden.total for orden in ordenes)
        self.promedio_orden = self.total_ingresos / self.total_ordenes if self.total_ordenes > 0 else 0
        self.platillos_vendidos = self._calcular_platillos_vendidos()
        self.categoria_mas_vendida = self._categoria_mas_vendida()

    def _calcular_platillos_vendidos(self):
        """Calcula el total de platillos vendidos"""
        total = 0
        for orden in self.ordenes:
            for item in orden.platillos:
                total += item['cantidad']
        return total

    def _categoria_mas_vendida(self):
        """Determina la categoría más vendida"""
        categorias = {}
        for orden in self.ordenes:
            for item in orden.platillos:
                categoria = item['platillo'].categoria
                if categoria not in categorias:
                    categorias[categoria] = 0
                categorias[categoria] += item['cantidad']
        
        if categorias:
            return max(categorias.items(), key=lambda x: x[1])
        return None

    def __str__(self):
        """Método para mostrar el cierre de caja en formato legible"""
        return f"Cierre de Caja - {self.fecha_cierre.strftime('%d/%m/%Y')} - Total: ${self.total_ingresos:,.0f}"


# ==================== CLASE RESTAURANT ====================
class Restaurant:
    """
    Clase principal que gestiona todo el sistema del restaurant
    """
    def __init__(self):
        """Inicializa el sistema del restaurant y carga los datos existentes"""
        self.platillos = {}
        self.ordenes = []
        self.contador_ordenes = 1
        self.cierre_caja = None
        self.cargar_datos()

    # ==================== CRUD DE PLATILLOS ====================

    def agregar_platillo(self, id_platillo, nombre, precio, categoria):
        """Crea un nuevo platillo en el sistema"""
        if id_platillo in self.platillos:
            print("❌ El ID del platillo ya existe.")
            return False
        
        try:
            precio = float(precio)
            platillo = Platillo(id_platillo, nombre, precio, categoria)
            self.platillos[id_platillo] = platillo
            self.guardar_platillo(platillo)
            print("✅ Platillo agregado correctamente.")
            return True
        except ValueError:
            print("❌ El precio debe ser un número válido.")
            return False

    def mostrar_platillos(self):
        """Muestra todos los platillos del menú organizados por categoría"""
        print("\n" + "="*60)
        print("🍽️  MENÚ DEL RESTAURANT")
        print("="*60)
        
        if not self.platillos:
            print("No hay platillos registrados.")
            return
        
        categorias = {}
        for platillo in self.platillos.values():
            if platillo.categoria not in categorias:
                categorias[platillo.categoria] = []
            categorias[platillo.categoria].append(platillo)
        
        for categoria, platillos in categorias.items():
            print(f"\n📋 {categoria.upper()}:")
            print("-" * 60)
            for platillo in platillos:
                print(f"  {platillo}")

    def buscar_platillo(self, id_platillo):
        """Busca y muestra la información de un platillo específico"""
        if id_platillo in self.platillos:
            platillo = self.platillos[id_platillo]
            print("\n🔍 Platillo encontrado:")
            print(f"  ID: {platillo.id_platillo}")
            print(f"  Nombre: {platillo.nombre}")
            print(f"  Precio: ${platillo.precio:,.0f}")
            print(f"  Categoría: {platillo.categoria}")
            print(f"  Disponible: {'Sí' if platillo.disponible else 'No'}")
            return platillo
        else:
            print("❌ Platillo no encontrado.")
            return None

    def editar_platillo(self, id_platillo):
        """Permite editar los datos de un platillo existente"""
        if id_platillo not in self.platillos:
            print("❌ Platillo no encontrado.")
            return False
        
        platillo = self.platillos[id_platillo]
        print(f"\n📝 Editando: {platillo.nombre}")
        print("(Presiona Enter para mantener el valor actual)")
        
        nuevo_nombre = input(f"Nombre [{platillo.nombre}]: ").strip()
        nuevo_precio = input(f"Precio [${platillo.precio:,.0f}]: ").strip()
        nueva_categoria = input(f"Categoría [{platillo.categoria}]: ").strip()
        disponible = input(f"¿Disponible? (s/n) [{'s' if platillo.disponible else 'n'}]: ").strip().lower()
        
        if nuevo_nombre:
            platillo.nombre = nuevo_nombre
        if nuevo_precio:
            try:
                platillo.precio = float(nuevo_precio)
            except ValueError:
                print("⚠️ Precio inválido, se mantiene el anterior.")
        if nueva_categoria:
            platillo.categoria = nueva_categoria
        if disponible:
            platillo.disponible = disponible == 's'
        
        self.actualizar_platillo(platillo)
        print("✅ Platillo actualizado correctamente.")
        return True

    def eliminar_platillo(self, id_platillo):
        """Elimina un platillo del sistema y su archivo correspondiente"""
        if id_platillo not in self.platillos:
            print("❌ Platillo no encontrado.")
            return False
        
        platillo = self.platillos[id_platillo]
        confirmacion = input(f"¿Está seguro de eliminar '{platillo.nombre}'? (s/n): ").strip().lower()
        
        if confirmacion == 's':
            del self.platillos[id_platillo]
            try:
                os.remove(CARPETA_PLATILLOS + id_platillo + EXTENSION)
                print("✅ Platillo eliminado correctamente.")
                return True
            except OSError as e:
                print(f"⚠️ Error al eliminar el archivo: {e}")
                return False
        else:
            print("❌ Eliminación cancelada.")
            return False

    # ==================== GESTIÓN DE ÓRDENES ====================

    def crear_orden(self):
        """Crea una nueva orden para un cliente"""
        print("\n" + "="*60)
        print("🛒 CREAR NUEVA ORDEN")
        print("="*60)
        
        cliente = input("Nombre del cliente (0 para cancelar): ").strip()
        if cliente == '0':
            print("❌ Creación de orden cancelada.")
            input("\nPresione Enter para volver al menú...")
            return
        
        if not cliente:
            print("❌ Debe ingresar el nombre del cliente.")
            input("\nPresione Enter para volver al menú...")
            return
        
        orden = Orden(self.contador_ordenes, cliente)
        
        print("\n📋 Agregando platillos a la orden...")
        print("💡 Tip: Ingrese '0' en cualquier momento para cancelar la orden")
        
        while True:
            self.mostrar_platillos()
            
            id_platillo = input("\nID del platillo (0 para cancelar orden): ").strip()
            
            if id_platillo == '0':
                confirmacion = input("\n⚠️  ¿Está seguro de cancelar esta orden? (s/n): ").strip().lower()
                if confirmacion == 's':
                    print("❌ Orden cancelada.")
                    input("\nPresione Enter para volver al menú...")
                    return
                else:
                    print("✅ Continuando con la orden...")
                    continue
            
            if id_platillo not in self.platillos:
                print("❌ Platillo no encontrado.")
                continuar = input("\n¿Desea intentar con otro platillo? (s/n): ").strip().lower()
                if continuar != 's':
                    break
                continue
            
            platillo = self.platillos[id_platillo]
            
            if not platillo.disponible:
                print("⚠️ Este platillo no está disponible.")
                continuar = input("\n¿Desea seleccionar otro platillo? (s/n): ").strip().lower()
                if continuar != 's':
                    break
                continue
            
            try:
                cantidad = input(f"Cantidad de '{platillo.nombre}' (0 para cancelar): ")
                
                if cantidad == '0':
                    confirmacion = input("\n⚠️  ¿Está seguro de cancelar esta orden? (s/n): ").strip().lower()
                    if confirmacion == 's':
                        print("❌ Orden cancelada.")
                        input("\nPresione Enter para volver al menú...")
                        return
                    else:
                        print("✅ Continuando con la orden...")
                        continue
                
                cantidad = int(cantidad)
                
                if cantidad <= 0:
                    print("❌ La cantidad debe ser mayor a 0.")
                    continuar = input("\n¿Desea intentar nuevamente? (s/n): ").strip().lower()
                    if continuar != 's':
                        break
                    continue
                
                orden.agregar_platillo(platillo, cantidad)
                print(f"✅ Agregado: {cantidad}x {platillo.nombre} = ${platillo.precio * cantidad:,.0f}")
                print(f"💰 Subtotal actual: ${orden.total:,.0f}")
                
            except ValueError:
                print("❌ Cantidad inválida.")
                continuar = input("\n¿Desea intentar nuevamente? (s/n): ").strip().lower()
                if continuar != 's':
                    break
                continue
            
            print("\n" + "-"*60)
            agregar_mas = input("¿Desea agregar más platillos a la orden? (s/n): ").strip().lower()
            
            if agregar_mas != 's':
                print("🔚 Finalizando orden...")
                break
        
        if len(orden.platillos) == 0:
            print("\n⚠️ No se agregaron platillos. Orden cancelada.")
            input("\nPresione Enter para volver al menú...")
            return
        
        self.ordenes.append(orden)
        self.guardar_orden(orden)
        self.contador_ordenes += 1
        
        print("\n" + "="*60)
        print("✅ ORDEN CREADA EXITOSAMENTE")
        print("="*60)
        self.mostrar_detalle_orden(orden)
        input("\nPresione Enter para volver al menú...")

    def mostrar_detalle_orden(self, orden):
        """Muestra el detalle completo de una orden"""
        print(f"\n🧾 Orden #{orden.numero_orden}")
        print(f"Cliente: {orden.cliente}")
        print(f"Fecha: {orden.fecha.strftime('%d/%m/%Y %H:%M')}")
        print("-" * 60)
        
        for item in orden.platillos:
            platillo = item['platillo']
            cantidad = item['cantidad']
            subtotal = item['subtotal']
            print(f"  {cantidad}x {platillo.nombre:<30} ${subtotal:>10,.0f}")
        
        print("-" * 60)
        print(f"{'TOTAL:':<35} ${orden.total:>10,.0f}")
        print("="*60)

    def mostrar_ordenes(self):
        """Muestra un resumen de todas las órdenes registradas"""
        print("\n" + "="*60)
        print("📋 HISTORIAL DE ÓRDENES")
        print("="*60)
        
        if not self.ordenes:
            print("No hay órdenes registradas.")
            return
        
        for orden in self.ordenes:
            print(orden)

    def buscar_orden(self, numero_orden):
        """Busca y muestra el detalle completo de una orden específica"""
        try:
            numero_orden = int(numero_orden)
            for orden in self.ordenes:
                if orden.numero_orden == numero_orden:
                    self.mostrar_detalle_orden(orden)
                    return orden
            print("❌ Orden no encontrada.")
            return None
        except ValueError:
            print("❌ Número de orden inválido.")
            return None

    def eliminar_orden(self, numero_orden):
        """Elimina una orden del sistema y su archivo correspondiente"""
        try:
            numero_orden = int(numero_orden)
            orden_encontrada = None
            
            for i, orden in enumerate(self.ordenes):
                if orden.numero_orden == numero_orden:
                    orden_encontrada = (i, orden)
                    break
            
            if not orden_encontrada:
                print("❌ Orden no encontrada.")
                return False
            
            indice, orden = orden_encontrada
            
            print("\n📋 Orden a eliminar:")
            self.mostrar_detalle_orden(orden)
            
            confirmacion = input("\n⚠️  ¿Está seguro de eliminar esta orden? (s/n): ").strip().lower()
            
            if confirmacion == 's':
                del self.ordenes[indice]
                
                try:
                    archivos = os.listdir(CARPETA_ORDENES)
                    for archivo in archivos:
                        if archivo.startswith(f'orden_{orden.numero_orden:04d}_'):
                            os.remove(CARPETA_ORDENES + archivo)
                            break
                    
                    print(f"\n✅ Orden #{numero_orden} eliminada correctamente.")
                    return True
                except OSError as e:
                    print(f"⚠️ Error al eliminar el archivo: {e}")
                    return False
            else:
                print("❌ Eliminación cancelada.")
                return False
                
        except ValueError:
            print("❌ Número de orden inválido.")
            return False

    # ==================== CIERRE DE CAJA ====================

    def generar_cierre_caja(self):
        """Genera un cierre de caja con todos los totales del día"""
        if not self.ordenes:
            print("❌ No hay órdenes registradas. No es posible generar cierre de caja.")
            return
        
        self.cierre_caja = CierreCaja(self.ordenes)
        print("\n✅ Cierre de caja generado correctamente.")

    def mostrar_cierre_caja(self):
        """Muestra el cierre de caja con todas sus estadísticas"""
        if self.cierre_caja is None:
            print("❌ No hay cierre de caja generado.")
            print("   Por favor, genere un cierre de caja primero.")
            return
        
        cierre = self.cierre_caja
        
        print("\n" + "="*80)
        print("💰 CIERRE DE CAJA DEL DÍA")
        print("="*80)
        print(f"\nFecha de Cierre: {cierre.fecha_cierre.strftime('%d/%m/%Y %H:%M:%S')}")
        print("\n" + "-"*80)
        print("RESUMEN ESTADÍSTICO:")
        print("-"*80)
        print(f"📊 Total de órdenes:        {cierre.total_ordenes}")
        print(f"💰 Total de ingresos:       ${cierre.total_ingresos:,.0f}")
        print(f"📈 Promedio por orden:      ${cierre.promedio_orden:,.0f}")
        print(f"🍽️  Total de platillos:      {cierre.platillos_vendidos}")
        
        if cierre.categoria_mas_vendida:
            categoria, cantidad = cierre.categoria_mas_vendida
            print(f"⭐ Categoría más vendida:   {categoria} ({cantidad} platillos)")
        
        print("\n" + "-"*80)
        print("DETALLES POR ORDEN:")
        print("-"*80)
        
        for orden in cierre.ordenes:
            print(f"Orden #{orden.numero_orden:<3} - {orden.cliente:<20} ${orden.total:>12,.0f}")
        
        print("\n" + "="*80)
        print(f"{'TOTAL FINAL:':<40} ${cierre.total_ingresos:>12,.0f}")
        print("="*80)

    def guardar_cierre_caja(self):
        """Guarda el cierre de caja en el directorio 'Cierre de caja' organizado por fecha"""
        if self.cierre_caja is None:
            print("❌ No hay cierre de caja generado.")
            print("   Por favor, genere un cierre de caja primero.")
            return
        
        try:
            if not os.path.exists(CARPETA_CIERRE_CAJA):
                os.makedirs(CARPETA_CIERRE_CAJA)
            
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            ruta_fecha = os.path.join(CARPETA_CIERRE_CAJA, fecha_actual)
            
            if not os.path.exists(ruta_fecha):
                os.makedirs(ruta_fecha)
            
            hora_actual = datetime.now().strftime("%H-%M-%S")
            nombre_archivo = f"cierre_caja_{hora_actual}{EXTENSION}"
            ruta_completa = os.path.join(ruta_fecha, nombre_archivo)
            
            cierre = self.cierre_caja
            
            with open(ruta_completa, 'w', encoding='utf-8') as archivo:
                archivo.write("="*80 + "\n")
                archivo.write("💰 CIERRE DE CAJA DEL DÍA\n")
                archivo.write("="*80 + "\n\n")
                archivo.write("🐺🐰 RESTAURANTE WOLFRABBIT - ¡La mejor Comida Salvaje de Chile! 🐺🐰\n\n")
                
                archivo.write(f"Fecha de Cierre: {cierre.fecha_cierre.strftime('%d/%m/%Y %H:%M:%S')}\n")
                archivo.write("\n" + "-"*80 + "\n")
                archivo.write("RESUMEN ESTADÍSTICO:\n")
                archivo.write("-"*80 + "\n")
                archivo.write(f"Total de órdenes:        {cierre.total_ordenes}\n")
                archivo.write(f"Total de ingresos:       ${cierre.total_ingresos:,.0f}\n")
                archivo.write(f"Promedio por orden:      ${cierre.promedio_orden:,.0f}\n")
                archivo.write(f"Total de platillos:      {cierre.platillos_vendidos}\n")
                
                if cierre.categoria_mas_vendida:
                    categoria, cantidad = cierre.categoria_mas_vendida
                    archivo.write(f"Categoría más vendida:   {categoria} ({cantidad} platillos)\n")
                
                archivo.write("\n" + "-"*80 + "\n")
                archivo.write("DETALLES POR ORDEN:\n")
                archivo.write("-"*80 + "\n")
                
                for orden in cierre.ordenes:
                    archivo.write(f"Orden #{orden.numero_orden:<3} - {orden.cliente:<20} ${orden.total:>12,.0f}\n")
                
                archivo.write("\n" + "="*80 + "\n")
                archivo.write(f"{'TOTAL FINAL:':<40} ${cierre.total_ingresos:>12,.0f}\n")
                archivo.write("="*80 + "\n")
            
            print("\n" + "="*60)
            print("✅ Cierre de caja guardado correctamente.")
            print(f"📁 Ubicación: {ruta_completa}")
            print(f"💰 Total guardado: ${cierre.total_ingresos:,.0f}")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error al guardar el cierre de caja: {e}")

    def guardar_ordenes_completo(self):
        """Guarda un reporte completo de todas las órdenes"""
        if not self.ordenes:
            print("❌ No hay órdenes registradas para guardar.")
            return
        
        try:
            if not os.path.exists(CARPETA_ORDENES_GUARDADAS):
                os.makedirs(CARPETA_ORDENES_GUARDADAS)
            
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            ruta_fecha = os.path.join(CARPETA_ORDENES_GUARDADAS, fecha_actual)
            
            if not os.path.exists(ruta_fecha):
                os.makedirs(ruta_fecha)
            
            hora_actual = datetime.now().strftime("%H-%M-%S")
            nombre_archivo = f"listado_ordenes_{hora_actual}{EXTENSION}"
            ruta_completa = os.path.join(ruta_fecha, nombre_archivo)
            
            with open(ruta_completa, 'w', encoding='utf-8') as archivo:
                archivo.write("="*80 + "\n")
                archivo.write(f"LISTADO COMPLETO DE ÓRDENES - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                archivo.write("="*80 + "\n\n")
                archivo.write("🐺🐰 RESTAURANTE WOLFRABBIT - ¡La mejor Comida Salvaje de Chile! 🐺🐰\n\n")
                
                for idx, orden in enumerate(self.ordenes, 1):
                    archivo.write(f"--- ORDEN #{idx} ---\n")
                    archivo.write(f"Número de Orden: {orden.numero_orden}\n")
                    archivo.write(f"Cliente: {orden.cliente}\n")
                    archivo.write(f"Fecha: {orden.fecha.strftime('%d/%m/%Y %H:%M:%S')}\n")
                    archivo.write(f"{'-'*80}\n")
                    archivo.write(f"DETALLE:\n")
                    
                    for item in orden.platillos:
                        platillo = item['platillo']
                        cantidad = item['cantidad']
                        subtotal = item['subtotal']
                        archivo.write(f"  {cantidad}x {platillo.nombre:<40} ${subtotal:>12,.0f}\n")
                    
                    archivo.write(f"{'-'*80}\n")
                    archivo.write(f"{'TOTAL ORDEN:':<50} ${orden.total:>12,.0f}\n")
                    archivo.write("\n")
                
                archivo.write("="*80 + "\n")
                archivo.write("RESUMEN ESTADÍSTICO:\n")
                total_ingresos = sum(orden.total for orden in self.ordenes)
                cantidad_ordenes = len(self.ordenes)
                promedio_orden = total_ingresos / cantidad_ordenes if cantidad_ordenes > 0 else 0
                
                archivo.write(f"Total de órdenes: {cantidad_ordenes}\n")
                archivo.write(f"Total de ingresos: ${total_ingresos:,.0f}\n")
                archivo.write(f"Promedio por orden: ${promedio_orden:,.0f}\n")
                archivo.write("="*80 + "\n")
            
            print("\n" + "="*60)
            print("✅ Órdenes guardadas correctamente.")
            print(f"📁 Ubicación: {ruta_completa}")
            print(f"📊 Total de órdenes guardadas: {len(self.ordenes)}")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error al guardar las órdenes: {e}")

    def eliminar_listado_ordenes(self):
        """Elimina completamente el listado de órdenes del sistema"""
        print("\n" + "="*60)
        print("⚠️  ELIMINAR LISTADO COMPLETO DE ÓRDENES")
        print("="*60)
        
        if not self.ordenes:
            print("❌ No hay órdenes registradas para eliminar.")
            return
        
        total_ordenes = len(self.ordenes)
        total_ingresos = sum(orden.total for orden in self.ordenes)
        
        print(f"\n📊 Total de órdenes registradas: {total_ordenes}")
        print(f"💰 Total de ingresos: ${total_ingresos:,.0f}")
        print("\n⚠️  ADVERTENCIA: Esta acción eliminará TODAS las órdenes del sistema.")
        print("   Los archivos individuales también serán eliminados.")
        
        confirmacion = input("\n¿Está seguro de eliminar TODO el listado de órdenes? (s/n): ").strip().lower()
        
        if confirmacion == 's':
            try:
                archivos_eliminados = 0
                if os.path.exists(CARPETA_ORDENES):
                    archivos = os.listdir(CARPETA_ORDENES)
                    for archivo in archivos:
                        if archivo.endswith(EXTENSION):
                            os.remove(CARPETA_ORDENES + archivo)
                            archivos_eliminados += 1
                
                self.ordenes.clear()
                self.contador_ordenes = 1
                self.cierre_caja = None
                
                print(f"\n✅ Listado de órdenes eliminado correctamente.")
                print(f"📁 {archivos_eliminados} archivo(s) eliminado(s) del directorio.")
                print(f"🔄 Contador de órdenes reiniciado a: 1")
                
            except Exception as e:
                print(f"\n❌ Error al eliminar el listado: {e}")
        else:
            print("\n❌ Eliminación cancelada.")

    # ==================== PERSISTENCIA ====================

    def guardar_platillo(self, platillo):
        """Guarda un platillo en un archivo .txt"""
        with open(CARPETA_PLATILLOS + platillo.id_platillo + EXTENSION, 'w', encoding='utf-8') as archivo:
            archivo.write(f'ID: {platillo.id_platillo}\n')
            archivo.write(f'Nombre: {platillo.nombre}\n')
            archivo.write(f'Precio: {platillo.precio}\n')
            archivo.write(f'Categoría: {platillo.categoria}\n')
            archivo.write(f'Disponible: {platillo.disponible}\n')

    def actualizar_platillo(self, platillo):
        """Actualiza un platillo en el archivo .txt"""
        self.guardar_platillo(platillo)

    def guardar_orden(self, orden):
        """Guarda una orden en un archivo .txt con formato de ticket"""
        nombre_archivo = f'orden_{orden.numero_orden:04d}_{orden.fecha.strftime("%Y%m%d_%H%M%S")}'
        with open(CARPETA_ORDENES + nombre_archivo + EXTENSION, 'w', encoding='utf-8') as archivo:
            archivo.write(f'ORDEN #{orden.numero_orden}\n')
            archivo.write(f'{"="*50}\n')
            archivo.write(f'Cliente: {orden.cliente}\n')
            archivo.write(f'Fecha: {orden.fecha.strftime("%d/%m/%Y %H:%M")}\n')
            archivo.write(f'{"-"*50}\n\n')
            archivo.write(f'DETALLE DE LA ORDEN:\n')
            archivo.write(f'{"-"*50}\n')
            
            for item in orden.platillos:
                platillo = item['platillo']
                cantidad = item['cantidad']
                subtotal = item['subtotal']
                archivo.write(f'{cantidad}x {platillo.nombre:<30} ${subtotal:>10,.0f}\n')
            
            archivo.write(f'{"-"*50}\n')
            archivo.write(f'{"TOTAL:":<35} ${orden.total:>10,.0f}\n')
            archivo.write(f'{"="*50}\n')

    def cargar_datos(self):
        """Carga todos los datos desde archivos al iniciar el sistema"""
        self.cargar_platillos()
        self.cargar_ordenes()

    def cargar_platillos(self):
        """Carga todos los platillos desde archivos .txt"""
        if not os.path.exists(CARPETA_PLATILLOS):
            return

        archivos = os.listdir(CARPETA_PLATILLOS)
        
        for archivo in archivos:
            if archivo.endswith(EXTENSION):
                try:
                    with open(CARPETA_PLATILLOS + archivo, 'r', encoding='utf-8') as f:
                        lineas = f.readlines()
                        id_platillo = lineas[0].split(': ')[1].strip()
                        nombre = lineas[1].split(': ')[1].strip()
                        precio = float(lineas[2].split(': ')[1].strip())
                        categoria = lineas[3].split(': ')[1].strip()
                        disponible = lineas[4].split(': ')[1].strip() == 'True'
                        
                        platillo = Platillo(id_platillo, nombre, precio, categoria)
                        platillo.disponible = disponible
                        self.platillos[id_platillo] = platillo
                except Exception as e:
                    print(f"Error cargando platillo {archivo}: {e}")

    def cargar_ordenes(self):
        """Carga las órdenes desde archivos y actualiza el contador de órdenes"""
        if not os.path.exists(CARPETA_ORDENES):
            return

        archivos = os.listdir(CARPETA_ORDENES)
        max_orden = 0
        
        for archivo in archivos:
            if archivo.endswith(EXTENSION):
                try:
                    partes = archivo.replace(EXTENSION, '').split('_')
                    if len(partes) >= 2:
                        numero_orden = int(partes[1])
                        if numero_orden > max_orden:
                            max_orden = numero_orden
                except Exception as e:
                    print(f"Error procesando {archivo}: {e}")
        
        self.contador_ordenes = max_orden + 1


# ==================== FUNCIONES AUXILIARES ====================

def crear_directorios():
    """Crea los directorios necesarios para almacenar los archivos si no existen"""
    directorios = [CARPETA_PLATILLOS, CARPETA_ORDENES, CARPETA_ORDENES_GUARDADAS, CARPETA_CIERRE_CAJA]
    for directorio in directorios:
        if not os.path.exists(directorio):
            os.makedirs(directorio)


def mostrar_menu():
    """Muestra el menú principal del sistema con todas las opciones disponibles"""
    print("\n" + "="*60)
    print('\n🐺🐰 Bienvenidos al Restaurante WolfRabbit!! 🐺🐰')
    print('¡La mejor Comida Salvaje de Chile!\n')
    print("="*60)
    print("\n" + "="*60)
    print("🍽️  SISTEMA DE GESTIÓN DE RESTAURANT 🍽️")
    print("="*60)
    print("\n--- GESTIÓN DE PLATILLOS ---")
    print("1.  Agregar Platillo")
    print("2.  Mostrar Menú (Todos los Platillos)")
    print("3.  Buscar Platillo")
    print("4.  Editar Platillo")
    print("5.  Eliminar Platillo")
    print("\n--- GESTIÓN DE ÓRDENES ---")
    print("6.  Crear Nueva Orden")
    print("7.  Mostrar Todas las Órdenes")
    print("8.  Buscar Orden")
    print("9.  Eliminar Orden")
    print("\n--- REPORTES Y ÓRDENES GUARDADAS ---")
    print("10. Guardar Listado de Órdenes")
    print("11. Eliminar Listado de Órdenes")
    print("\n--- CIERRE DE CAJA ---")
    print("12. Generar Cierre de Caja")
    print("13. Mostrar Cierre de Caja")
    print("14. Guardar Cierre de Caja")
    print("\n--- SISTEMA ---")
    print("0.  Salir del Sistema")
    print("="*60)


# ==================== FUNCIÓN PRINCIPAL ====================

def app():
    """Función principal que ejecuta el sistema del restaurant"""
    crear_directorios()
    
    restaurant = Restaurant()
    
    print("✅ Sistema de restaurant iniciado correctamente.")
    if restaurant.platillos:
        print(f"📊 Se cargaron {len(restaurant.platillos)} platillos del menú.")
    if restaurant.ordenes:
        print(f"📋 Se cargaron {len(restaurant.ordenes)} órdenes del historial.")
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSeleccione una opción (0-14): ").strip()
            
            if opcion == '1':
                print("\n--- AGREGAR PLATILLO ---")
                id_platillo = input("ID del platillo (ej: P001): ").strip()
                nombre = input("Nombre del platillo: ").strip()
                precio = input("Precio: ").strip()
                categoria = input("Categoría (Entrada/Plato Fuerte/Postre/Bebida): ").strip()
                restaurant.agregar_platillo(id_platillo, nombre, precio, categoria)
            
            elif opcion == '2':
                restaurant.mostrar_platillos()
            
            elif opcion == '3':
                print("\n--- BUSCAR PLATILLO ---")
                id_platillo = input("ID del platillo: ").strip()
                restaurant.buscar_platillo(id_platillo)
            
            elif opcion == '4':
                print("\n--- EDITAR PLATILLO ---")
                id_platillo = input("ID del platillo a editar: ").strip()
                restaurant.editar_platillo(id_platillo)
            
            elif opcion == '5':
                print("\n--- ELIMINAR PLATILLO ---")
                id_platillo = input("ID del platillo a eliminar: ").strip()
                restaurant.eliminar_platillo(id_platillo)
            
            elif opcion == '6':
                restaurant.crear_orden()
            
            elif opcion == '7':
                restaurant.mostrar_ordenes()
            
            elif opcion == '8':
                print("\n--- BUSCAR ORDEN ---")
                numero_orden = input("Número de orden: ").strip()
                restaurant.buscar_orden(numero_orden)
            
            elif opcion == '9':
                print("\n--- ELIMINAR/CANCELAR ORDEN ---")
                numero_orden = input("Número de orden a eliminar: ").strip()
                restaurant.eliminar_orden(numero_orden)
            
            elif opcion == '10':
                restaurant.guardar_ordenes_completo()
                input("\nPresione Enter para volver al menú...")
            
            elif opcion == '11':
                restaurant.eliminar_listado_ordenes()
                input("\nPresione Enter para volver al menú...")
            
            elif opcion == '12':
                restaurant.generar_cierre_caja()
                input("\nPresione Enter para volver al menú...")
            
            elif opcion == '13':
                restaurant.mostrar_cierre_caja()
                input("\nPresione Enter para volver al menú...")
            
            elif opcion == '14':
                restaurant.guardar_cierre_caja()
                input("\nPresione Enter para volver al menú...")
            
            elif opcion == '0':
                print("\n" + "="*60)
                print("👋 ¡Gracias por usar el sistema de restaurant!")
                print("📁 Todos los datos han sido guardados correctamente.")
                print('\n By: MCode-DevOps93 🐺')
                print("="*60)
                break
            
            else:
                print("❌ Opción inválida. Por favor seleccione entre 0-14.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Sistema cerrado por el usuario.")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")


# ==================== PUNTO DE ENTRADA ====================
if __name__ == "__main__":
    """
    Punto de entrada del programa
    Se ejecuta solo si el archivo se ejecuta directamente
    """
    app()

