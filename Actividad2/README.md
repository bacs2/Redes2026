# 🌐 Proyecto: DNS Resolver Recursivo e Iterativo

Este proyecto implementa un servidor DNS de resolución local que escucha peticiones en el puerto `8000` vía UDP. Su principal objetivo es recibir consultas DNS de los clientes (como `dig`), buscar la respuesta en una caché local optimizada y, en caso de no encontrarla, iniciar un proceso de resolución iterativa/recursiva interactuando directamente con los servidores reales de internet.

## 🧠 ¿Cómo funciona?

Cuando intentas acceder a una página (ej. `www.uchile.cl`), tu computadora necesita saber su dirección IP. Este script actúa como el intermediario que averigua esa IP paso a paso:

1. **Intercepta:** El script recibe la pregunta original del cliente.
2. **Revisa la Caché:** Si alguien ya preguntó por `www.uchile.cl` recientemente, el script lo recuerda y responde de inmediato.
3. **Consulta al Servidor Raíz (Root):** Si no sabe la respuesta, le pregunta al servidor principal de internet (`192.33.4.12`).
4. **Navegación Iterativa (Delegación):** El servidor raíz no sabe la IP exacta, pero devuelve la IP del servidor que maneja los dominios `.cl` (TLD). El script entonces le pregunta a ese servidor TLD. Este responde con el servidor "Autoritativo" (el que maneja `uchile.cl`).
5. **Resolución Recursiva:** En caso de que el servidor delegado solo devuelva un *nombre* y no una IP, el script pausa la búsqueda principal, averigua la IP de ese nuevo servidor desde cero, y luego retoma su camino.
6. **Respuesta final:** Una vez obtenida la IP final, la guarda en su historial de frecuencias y devuelve el paquete al cliente original.

---

## 🚀 Cómo ejecutarlo en cualquier máquina

Para correr este servidor en una máquina distinta a tu entorno virtual original, sigue estos pasos:

### 1. Requisitos previos
Asegúrate de tener Python 3 instalado. Luego, instala la librería requerida para manipular paquetes DNS:
```bash
pip install dnslib
```

### 2. Configurar la IP de escucha (Importante)
En el archivo `resolver.py`, la variable `IP` está configurada fijamente para una red específica (`192.168.56.1`). Para que escuche en tu propia máquina de pruebas, debes modificar las primeras líneas del archivo:

Abre `resolver.py` y cambia:
```python
IP = "192.168.56.1"  # <- Cambia esto
```
Por tu IP local o `localhost`:
```python
IP = "127.0.0.1"     # Escucha solo en tu máquina local
# O bien:
# IP = "0.0.0.0"     # Escucha en todas las interfaces de red de la máquina
```

### 3. Iniciar el Servidor
Ejecuta el script directamente desde la terminal. Se quedará corriendo en un ciclo infinito esperando peticiones:
```bash
python3 resolver.py
```
*(Deberías ver el mensaje: `socket escuchando en 127.0.0.1:8000`)*

### 4. Probar la Resolución (Desde otra terminal)
Abre una nueva ventana de terminal y usa el comando `dig` para enviarle una consulta a tu script apuntando al puerto `8000`:
```bash
dig @127.0.0.1 -p 8000 www.uchile.cl
```
Verás en la terminal del servidor todo el rastro de depuración `(debug) Consultando...` saltando por diferentes IPs, y en la terminal cliente obtendrás la respuesta oficial con la bandera correcta indicando resolución recursiva.

---

## 🛠️ Desglose Técnico de Funciones

### `actualizar_cache()`
- **Propósito:** Mantener la caché DNS actualizada para optimizar tiempo.
- **Funcionamiento:** Escanea `historial_dns` (frecuencias de uso) y guarda en memoria temporal (`cache`) el Top 3 de los dominios más consultados.

### `parse_dns_reply_elements(dnslib_reply)`
- **Propósito:** Parseador de paquetes binarios.
- **Funcionamiento:** Construye diccionarios estructurados extrayendo la información en las áreas fundamentales del estándar DNS: `header`, `query`, `answer`, `authority` y `additional`.

### `resolver(query, ip=servidor_raiz)`
- **Propósito:** Ejecutar el mecanismo central recursivo.
- **Funcionamiento:** Revisa la caché. Si falla, consulta la IP destino. Inspecciona la sección *Answer*. Si no hay respuestas, busca delegaciones 'NS' en *Authority*. Extrae las IPs adicionales de *Additional* para saltar al siguiente eslabón, resolviendo recursivamente si le falta la IP de dicho servidor de nombres.

### Bucle Principal (`if __name__ == "__main__":`)
- **Propósito:** Servidor UDP concurrente.
- **Funcionamiento:** Crea un socket escuchando el puerto `8000`. Extrae los IDs de `dig`, los almacena temporalmente y repone esos IDs de vuelta al enviar el resultado. También re-asigna los flags requeridos (`RA=1`, `AA=0`) para no dar Falsos Positivos de Autoridad.
