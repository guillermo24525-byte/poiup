# entradas
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta

# configuración del estilo del programa
FUENTE = ("Arial", 11)                        # fuente principal de la interfaz  
COLOR_FONDO_APP = "darkgreen"                 # color de fondo de la ventana principal            
COLOR_ENTRADA_FONDO = "gray"         # fondo de los campos de entrada
COLOR_ENTRADA_TEXTO = "black"                 # color del texto en los campos

# la base para operaciones de abono y cargo
class Transacciones:
    def abonar(self, cantidad):
        raise NotImplementedError

    def cargar(self, cantidad):
        raise NotImplementedError

    
# nos presenta  los datos personales del cliente
class Cliente:
    def __init__(self, nombre, apellido_paterno, apellido_materno, fecha_nacimiento, domicilio):
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.fecha_nacimiento = fecha_nacimiento
        self.domicilio = domicilio

# nos presenta una cuenta bancaria con saldo inicial y operaciones
class Cuenta(Transacciones):
    def __init__(self, numero_cuenta):
        self.numero_cuenta = numero_cuenta
        self.saldo = 1000.0  # Saldo inicial

    def abonar(self, cantidad):
        self.saldo += cantidad

    def cargar(self, cantidad):
        if self.saldo >= cantidad:
            self.saldo -= cantidad
            return True
        return False

# registro de algun movimiento en la cuenta
class Movimiento:
    def __init__(self, fecha_movimiento, descripcion, cargo, abono, saldo):
        self.fecha_movimiento = fecha_movimiento
        self.descripcion = descripcion
        self.cargo = cargo
        self.abono = abono
        self.saldo = saldo

# en esta parte se administra el estado de cuenta y sus movimientos
class EstadoDeCuenta:
    def __init__(self, cliente: Cliente, cuenta: Cuenta, fecha_ingreso: date):
        self.cliente = cliente
        self.cuenta = cuenta
        self.fecha_ingreso = fecha_ingreso
        self.movimientos = []

    def agregar_movimiento(self, descripcion, tipo, cantidad):
        fecha = self.fecha_ingreso + timedelta(days=len(self.movimientos))
        cargo = abono = 0.0
        if tipo == "Abono":
            self.cuenta.abonar(cantidad)
            abono = cantidad
        elif tipo == "Cargo":
            if not self.cuenta.cargar(cantidad):
                return False
            cargo = cantidad
        else:
            return False

        mov = Movimiento(fecha, descripcion, cargo, abono, self.cuenta.saldo)
        self.movimientos.append(mov)
        return True

    def obtener_totales(self):
        total_cargos = sum(m.cargo for m in self.movimientos)
        total_abonos = sum(m.abono for m in self.movimientos)
        return total_cargos, total_abonos, self.cuenta.saldo

    def generar_texto_estado(self):
        lines = []
        lines.append("===== ESTADO DE CUENTA =====\n")
        lines.append(">> Cliente:")
        lines.append(f"Nombre: {self.cliente.nombre} {self.cliente.apellido_paterno} {self.cliente.apellido_materno}")
        lines.append(f"Fecha de nacimiento: {self.cliente.fecha_nacimiento}")
        lines.append(f"Domicilio: {self.cliente.domicilio}\n")

        lines.append(">> Cuenta:")
        lines.append(f"Número de cuenta: {self.cuenta.numero_cuenta}")
        lines.append(f"Saldo inicial: $1000.00\n")

        lines.append(">> Movimientos:")
        lines.append(f"{'Fecha':10} | {'Descripción':20} | {'Cargo':>10} | {'Abono':>10} | {'Saldo':>10}")
        lines.append("-" * 70)
        for m in self.movimientos:
            lines.append(f"{m.fecha_movimiento} | {m.descripcion[:20]:20} | {m.cargo:10.2f} | {m.abono:10.2f} | {m.saldo:10.2f}")

        total_cargos, total_abonos, saldo_final = self.obtener_totales()
        lines.append("\n>> Totales:")
        lines.append(f"Total cargos: ${total_cargos:.2f}")
        lines.append(f"Total abonos: ${total_abonos:.2f}")
        lines.append(f"Saldo final: ${saldo_final:.2f}")
        lines.append("=============================")
        return "\n".join(lines)

# gráfica principal de la aplicación
class AppEstadoCuenta:
    def __init__(self, root):
        self.root = root
        self.root.title("Estado de Cuenta Bancario")
        self.estado = None
        self.movimientos_hechos = 0
        self.root.configure(bg=COLOR_FONDO_APP)

        self._crear_widgets_cliente()
        self._crear_widgets_movimiento()
        self._crear_widget_resumen()

    # parte para ingresar datos del cliente y de la cuenta
    def _crear_widgets_cliente(self):
        frame = tk.LabelFrame(self.root, text="Datos del Cliente / Cuenta", 
                              bg=COLOR_FONDO_APP, font=FUENTE, fg="white")
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.var_nombre = tk.StringVar()
        self.var_apellido_p = tk.StringVar()
        self.var_apellido_m = tk.StringVar()
        self.var_fecha_nac = tk.StringVar()
        self.var_domicilio = tk.StringVar()
        self.var_num_cuenta = tk.StringVar()

        campos = [
            ("Nombre:", self.var_nombre),
            ("Apellido Paterno:", self.var_apellido_p),
            ("Apellido Materno:", self.var_apellido_m),
            ("Fecha Nacimiento (YYYY-MM-DD):", self.var_fecha_nac),
            ("Domicilio:", self.var_domicilio),
            ("Número de cuenta:", self.var_num_cuenta),
        ]

        for i, (texto, var) in enumerate(campos):
            tk.Label(frame, text=texto, font=FUENTE, bg=COLOR_FONDO_APP, fg="black").grid(row=i, column=0, sticky="w")
            tk.Entry(frame, textvariable=var, font=FUENTE,
                     bg=COLOR_ENTRADA_FONDO, fg=COLOR_ENTRADA_TEXTO).grid(row=i, column=1, sticky="ew")

        tk.Button(frame, text="Crear Cuenta", font=FUENTE, bg="white", command=self.crear_cuenta).grid(row=len(campos), column=1, pady=5, sticky="e")

    # para añadir un movimiento a la cuenta
    def _crear_widgets_movimiento(self):
        frame = tk.LabelFrame(self.root, text="Agregar Movimiento", 
                              bg=COLOR_FONDO_APP, font=FUENTE, fg="black")
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.var_descripcion = tk.StringVar()
        self.var_tipo = tk.StringVar(value="Abono")
        self.var_monto = tk.StringVar()

        tk.Label(frame, text="Descripción:", font=FUENTE, bg=COLOR_FONDO_APP, fg="white").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.var_descripcion, font=FUENTE,
                 bg=COLOR_ENTRADA_FONDO, fg=COLOR_ENTRADA_TEXTO).grid(row=0, column=1, sticky="ew")

        tk.Label(frame, text="Tipo:", font=FUENTE, bg=COLOR_FONDO_APP, fg="white").grid(row=1, column=0, sticky="w")
        combo = ttk.Combobox(frame, textvariable=self.var_tipo, values=("Abono", "Cargo"), state="readonly", font=FUENTE)
        combo.grid(row=1, column=1, sticky="ew")

        tk.Label(frame, text="Monto:", font=FUENTE, bg=COLOR_FONDO_APP, fg="white").grid(row=2, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.var_monto, font=FUENTE,
                 bg=COLOR_ENTRADA_FONDO, fg=COLOR_ENTRADA_TEXTO).grid(row=2, column=1, sticky="ew")

        tk.Button(frame, text="Agregar movimiento", font=FUENTE, bg="white", command=self.agregar_movimiento).grid(row=3, column=1, pady=5, sticky="e")

    # esta parte es donde se muestra el estado de cuenta completo
    def _crear_widget_resumen(self):
        frame = tk.LabelFrame(self.root, text="Estado de Cuenta - Resumen",
                              bg=COLOR_FONDO_APP, font=FUENTE, fg="white")
        frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.text_resumen = tk.Text(frame, width=80, height=20, font=FUENTE,
                                   bg=COLOR_ENTRADA_FONDO, fg=COLOR_ENTRADA_TEXTO)
        self.text_resumen.pack(fill="both", expand=True)

        tk.Button(frame, text="Mostrar Estado de Cuenta", font=FUENTE, bg="white", command=self.mostrar_estado).pack(pady=5)

    # para crear un cliente y su cuenta
    def crear_cuenta(self):
        if not all([self.var_nombre.get(), self.var_apellido_p.get(), self.var_apellido_m.get(),
                    self.var_fecha_nac.get(), self.var_domicilio.get(), self.var_num_cuenta.get()]):
            messagebox.showwarning("Datos faltantes", "Por favor completa todos los datos del cliente y la cuenta.")
            return

        try:
            cliente = Cliente(
                self.var_nombre.get(),
                self.var_apellido_p.get(),
                self.var_apellido_m.get(),
                self.var_fecha_nac.get(),
                self.var_domicilio.get()
            )
            cuenta = Cuenta(self.var_num_cuenta.get())
            self.estado = EstadoDeCuenta(cliente, cuenta, date.today())
            messagebox.showinfo("Cuenta creada", "La cuenta ha sido creada con saldo inicial de $1000.00")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la cuenta: {e}")

    # agrega un nuevo movimiento a la cuenta y corrige si algo falla y nuevamente pide datos
    def agregar_movimiento(self):
        if not self.estado:
            messagebox.showwarning("Cuenta no creada", "Primero debes crear la cuenta.")
            return

        descripcion = self.var_descripcion.get()
        tipo = self.var_tipo.get()
        monto_texto = self.var_monto.get()

        if not descripcion or not monto_texto:
            messagebox.showwarning("Datos faltantes", "Por favor escribe descripción y monto.")
            return

        try:
            monto = float(monto_texto)
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Monto inválido", "Introduce un número válido y mayor a cero.")
            return

        if not self.estado.agregar_movimiento(descripcion, tipo, monto):
            messagebox.showwarning("Saldo insuficiente", "No se puede hacer el cargo porque no hay saldo suficiente.")
        else:
            self.var_descripcion.set("")
            self.var_monto.set("")

    # nos muestra el estado de cuenta completo
    def mostrar_estado(self):
        if not self.estado:
            messagebox.showwarning("Cuenta no creada", "Primero debes crear la cuenta.")
            return

        resumen = self.estado.generar_texto_estado()
        self.text_resumen.delete("1.0", tk.END)
        self.text_resumen.insert(tk.END, resumen)


# aqui se abre la ventana de la aplicación y se usa el programa
if __name__ == "__main__":
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(2, weight=1)
    app = AppEstadoCuenta(root)
    root.mainloop()