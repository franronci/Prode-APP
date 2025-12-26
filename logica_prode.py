# 1. Definimos la estructura de la 'Empresa'
class Empresa:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        # Aquí guardaremos a los empleados de esta empresa específica
        self.lista_empleados = []

    def agregar_empleado(self, empleado):
        self.lista_empleados.append(empleado)

    def mostrar_ranking(self):
        print(f"--- Ranking de {self.nombre} ---")
        # Ordenamos a los empleados por puntos de mayor a menor
        ranking = sorted(self.lista_empleados, key=lambda x: x.puntos, reverse=True)
        
        for i, empleado in enumerate(ranking, 1):
            print(f"{i}. {empleado.nombre}: {empleado.puntos} puntos")
        print("-------------------------------")

# 2. Definimos al 'Empleado' (Usuario)
class Empleado:
    def __init__(self, nombre, id_empresa):
        self.nombre = nombre
        self.id_empresa = id_empresa
        self.puntos = 0 # Todos arrancan con 0

    def sumar_puntos(self, puntos_ganados):
        self.puntos += puntos_ganados

# --- SIMULACIÓN DEL SISTEMA ---

# A. Creamos dos empresas (Clientes tuyos)
empresa_tech = Empresa(1, "Tech Solutions Inc.")
empresa_logistica = Empresa(2, "Logística Rápida S.A.")

# B. Creamos empleados y los asignamos a sus empresas
# Nota: En una app real, esto viene de una base de datos cuando se loguean
usuario_1 = Empleado("Ana", 1)    # Ana trabaja en Tech Solutions
usuario_2 = Empleado("Carlos", 1) # Carlos trabaja en Tech Solutions
usuario_3 = Empleado("Beatriz", 2) # Beatriz trabaja en Logística

# Los registramos en sus objetos de empresa correspondientes
empresa_tech.agregar_empleado(usuario_1)
empresa_tech.agregar_empleado(usuario_2)
empresa_logistica.agregar_empleado(usuario_3)

# C. Simulamos que terminó un partido y calculamos puntos
# Supongamos que Ana acertó el resultado exacto (3 puntos)
usuario_1.sumar_puntos(3)
# Carlos solo acertó el ganador (1 punto)
usuario_2.sumar_puntos(1)
# Beatriz acertó resultado exacto en su prode (3 puntos)
usuario_3.sumar_puntos(3)

# D. Mostramos los rankings SEPARADOS
# Al imprimir el ranking de Tech Solutions, Beatriz NO debe aparecer.
empresa_tech.mostrar_ranking()

# Al imprimir el ranking de Logística, Ana y Carlos NO deben aparecer.
empresa_logistica.mostrar_ranking()