# Reto 3: Integración de estructuras de datos en el sistema de inventario y pedidos
#
#   Lista enlazada -> el inventario de productos (crece y se achica sin límite)
#   Cola           -> pedidos pendientes (se atienden en orden de llegada)
#   Pila           -> historial de acciones del inventario (para deshacer)
#   datetime       -> guarda la fecha y hora de cada pedido y de cada acción

from datetime import datetime

# NODO BÁSICO (lo usan la pila y la cola)
class Nodo:
    def __init__(self, dato):
        self.dato = dato          # lo que guarda el nodo
        self.siguiente = None     # el nodo que sigue (None = no hay)

# PILA (LIFO): historial para deshacer

class Pila:
    def __init__(self):
        self.tope = None          # el nodo de arriba

    def push(self, dato):         # agrega un dato arriba
        nuevo = Nodo(dato)
        nuevo.siguiente = self.tope
        self.tope = nuevo

    def pop(self):                # saca y devuelve el dato de arriba
        if self.tope == None:
            return None
        dato = self.tope.dato
        self.tope = self.tope.siguiente
        return dato

    def peek(self):               # mira el dato de arriba sin sacarlo
        if self.tope == None:
            return None
        return self.tope.dato

    def esta_vacia(self):
        return self.tope == None


# COLA (FIFO): pedidos pendientes
class Cola:
    def __init__(self):
        self.inicio = None        # el primero en la fila
        self.fin = None           # el último en la fila

    def enqueue(self, dato):      # agrega al final
        nuevo = Nodo(dato)
        if self.fin == None:
            self.inicio = nuevo
        else:
            self.fin.siguiente = nuevo
        self.fin = nuevo

    def dequeue(self):            # saca y devuelve el primero
        if self.inicio == None:
            return None
        dato = self.inicio.dato
        self.inicio = self.inicio.siguiente
        if self.inicio == None:
            self.fin = None
        return dato

    def esta_vacia(self):
        return self.inicio == None

    def mostrar(self):            # muestra los pedidos en orden de llegada
        actual = self.inicio
        numero = 1
        while actual != None:
            cliente, producto, cantidad, fecha = actual.dato
            print(numero, "-", cliente, "| Producto:", producto, "| Cantidad:", cantidad, "| Llegó:", fecha)
            actual = actual.siguiente
            numero = numero + 1


# LISTA ENLAZADA: inventario de productos
class NodoProducto:
    def __init__(self, nombre, cantidad, precio):
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio
        self.siguiente = None


class ListaProductos:
    def __init__(self):
        self.primero = None       # el primer producto de la lista

    def esta_vacia(self):
        return self.primero == None

    def agregar(self, nombre, cantidad, precio):      # agrega al final de la lista
        nuevo = NodoProducto(nombre, cantidad, precio)
        if self.primero == None:
            self.primero = nuevo
        else:
            actual = self.primero
            while actual.siguiente != None:
                actual = actual.siguiente
            actual.siguiente = nuevo

    def buscar(self, nombre):                         # devuelve el nodo o None si no existe
        actual = self.primero
        while actual != None:
            if actual.nombre.lower() == nombre.lower():
                return actual
            actual = actual.siguiente
        return None

    def eliminar(self, nombre):                       # quita el producto devuelve True si lo encontró
        actual = self.primero
        anterior = None
        while actual != None:
            if actual.nombre.lower() == nombre.lower():
                if anterior == None:
                    self.primero = actual.siguiente  
                else:
                    anterior.siguiente = actual.siguiente
                return True
            anterior = actual
            actual = actual.siguiente
        return False

    def mostrar(self):
        actual = self.primero
        numero = 1
        while actual != None:
            print(numero, "-", actual.nombre, "| Cantidad:", actual.cantidad, "| Precio: $", actual.precio)
            actual = actual.siguiente
            numero = numero + 1


# Las tres estructuras del sistema
inventario = ListaProductos()
pedidos = Cola()
historial = Pila()

# Productos de ejemplo (no se guardan en el historial)
inventario.agregar("Mouse", 20, 12.50)
inventario.agregar("Teclado", 15, 25.00)
inventario.agregar("Monitor", 5, 150.00)


# FUNCIONES DE AYUDA (validan lo que escribe el usuario)

def ahora():
    # Devuelve la fecha y hora actual como texto
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def pedir_entero(mensaje, minimo, maximo):
    while True:
        texto = input(mensaje)
        if texto.isdigit() and int(texto) >= minimo and int(texto) <= maximo:
            return int(texto)
        print("Valor no válido, escriba un número entre", minimo, "y", maximo)


def pedir_decimal(mensaje):
    while True:
        texto = input(mensaje)
        if texto.replace(".", "", 1).isdigit():
            return float(texto)
        print("Escriba un número válido, por ejemplo 2.50")


# INVENTARIO (lista enlazada + historial en la pila)

def registrar_producto():
    nombre = input("Nombre del producto: ")
    if inventario.buscar(nombre) != None:
        print("Ese producto ya existe")
    else:
        cantidad = pedir_entero("Cantidad en stock: ", 0, 100000)
        precio = pedir_decimal("Precio de cada unidad: ")
        inventario.agregar(nombre, cantidad, precio)
        historial.push(("registrar", nombre, ahora()))   # se anota para poder deshacer
        print("Producto registrado")


def mostrar_inventario():
    print("\n--- INVENTARIO ---")
    if inventario.esta_vacia():
        print("No hay productos")
    else:
        inventario.mostrar()


def editar_producto():
    nombre = input("Nombre del producto a editar: ")
    nodo = inventario.buscar(nombre)
    if nodo == None:
        print("Ese producto no existe")
    else:
        print("Valores actuales -> Cantidad:", nodo.cantidad, "| Precio: $", nodo.precio)
        # Antes de cambiar, se guardan los valores viejos en el historial
        historial.push(("editar", nodo.nombre, nodo.cantidad, nodo.precio, ahora()))
        nodo.cantidad = pedir_entero("Nueva cantidad en stock: ", 0, 100000)
        nodo.precio = pedir_decimal("Nuevo precio: ")
        print("Producto actualizado")


def eliminar_producto():
    nombre = input("Nombre del producto a eliminar: ")
    nodo = inventario.buscar(nombre)
    if nodo == None:
        print("Ese producto no existe")
    else:
        historial.push(("eliminar", nodo.nombre, nodo.cantidad, nodo.precio, ahora()))
        inventario.eliminar(nombre)
        print("Producto eliminado")


def deshacer():
    if historial.esta_vacia():
        print("No hay acciones para deshacer")
    else:
        accion = historial.peek()                     # se mira la última acción...
        # La fecha siempre es el último dato de la acción
        print("Última acción:", accion[0], accion[1], "| Hecha el:", accion[-1])
        historial.pop()                               
        tipo = accion[0]
        nombre = accion[1]
        if tipo == "registrar":
            inventario.eliminar(nombre)
            print("Deshecho: se quitó el producto", nombre)
        elif tipo == "eliminar":
            inventario.agregar(nombre, accion[2], accion[3])
            print("Deshecho: se volvió a agregar el producto", nombre)
        else:
            nodo = inventario.buscar(nombre)
            nodo.cantidad = accion[2]
            nodo.precio = accion[3]
            print("Deshecho: se restauraron los valores de", nombre)


# PEDIDOS (cola FIFO)
def registrar_pedido():
    mostrar_inventario()
    cliente = input("Nombre del cliente: ")
    producto = input("Nombre del producto que pide: ")
    nodo = inventario.buscar(producto)
    if nodo == None:
        print("Ese producto no existe")
    else:
        cantidad = pedir_entero("Cantidad a pedir: ", 1, 100000)
        pedidos.enqueue((cliente, nodo.nombre, cantidad, ahora()))     # entra al final de la cola con su hora
        print("Pedido en espera")


def mostrar_pedidos():
    print("\n--- PEDIDOS PENDIENTES ---")
    if pedidos.esta_vacia():
        print("No hay pedidos pendientes")
    else:
        pedidos.mostrar()


def procesar_pedido():
    if pedidos.esta_vacia():
        print("No hay pedidos para procesar")
    else:
        cliente, producto, cantidad, fecha = pedidos.dequeue()       # sale el que llegó primero
        nodo = inventario.buscar(producto)
        if nodo == None:
            print("Pedido de", cliente, "rechazado: el producto ya no existe")
        elif cantidad > nodo.cantidad:
            print("Pedido de", cliente, "rechazado: solo hay", nodo.cantidad, "unidades de", producto)
        else:
            nodo.cantidad = nodo.cantidad - cantidad
            print("Pedido de", cliente, "atendido. Total a pagar: $", cantidad * nodo.precio)


# MENÚ PRINCIPAL
def mostrar_menu():
    print("\n===== INVENTARIO Y PEDIDOS =====")
    print("1. Registrar producto")
    print("2. Mostrar inventario")
    print("3. Editar producto")
    print("4. Eliminar producto")
    print("5. Registrar pedido (entra a la cola)")
    print("6. Mostrar pedidos pendientes")
    print("7. Procesar siguiente pedido")
    print("8. Deshacer última acción del inventario")
    print("0. Salir")


opcion = -1
while opcion != 0:
    mostrar_menu()
    opcion = pedir_entero("Elija una opción: ", 0, 8)
    if opcion == 1:
        registrar_producto()
    elif opcion == 2:
        mostrar_inventario()
    elif opcion == 3:
        editar_producto()
    elif opcion == 4:
        eliminar_producto()
    elif opcion == 5:
        registrar_pedido()
    elif opcion == 6:
        mostrar_pedidos()
    elif opcion == 7:
        procesar_pedido()
    elif opcion == 8:
        deshacer()
    else:
        print("Hasta luego")
