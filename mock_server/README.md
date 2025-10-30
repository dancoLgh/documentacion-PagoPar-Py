# PagoPar mock server

Este mock reproduce los endpoints principales descritos en la documentación pública de PagoPar para que puedas ensayar la integración sin consumir los servicios reales.

## Requisitos

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn mock_server.app:app --reload
```

El servidor quedará disponible en `http://127.0.0.1:8000`. Puedes navegar a `http://127.0.0.1:8000/docs` para revisar el contrato generado automáticamente.

## Endpoints soportados

| Método | Ruta | Descripción |
| --- | --- | --- |
| POST | `/api/comercios/2.0/iniciar-transaccion` | Crea un pedido simulado y devuelve el hash (`resultado[0].data`). |
| POST | `/api/forma-pago/1.1/traer/` | Lista medios de pago habilitados en el mock. |
| POST | `/api/pedidos/1.1/traer` | Devuelve el estado actual de un pedido usando su `hash_pedido`. |
| POST | `/api/pago-recurrente/3.0/agregar-cliente/` | Registra un cliente recurrente y devuelve su token. |
| POST | `/api/pago-recurrente/3.0/agregar-tarjeta/` | Guarda una tarjeta asociada al cliente. |
| POST | `/api/pago-recurrente/3.0/confirmar-tarjeta/` | Marca la tarjeta como confirmada. |
| POST | `/api/pago-recurrente/3.0/listar-tarjeta/` | Lista las tarjetas activas de un cliente. |
| POST | `/api/pago-recurrente/3.0/eliminar-tarjeta/` | Elimina una tarjeta por token. |
| POST | `/api/pago-recurrente/3.0/pagar/` | Ejecuta un cobro recurrente y marca el pedido como pagado. |
| POST | `/api/pago-recurrente/3.0/preautorizar/` | Genera una preautorización con monto máximo. |
| POST | `/api/pago-recurrente/3.0/confirmar-preautorizacion/` | Confirma un monto dentro de la preautorización. |
| POST | `/api/pago-recurrente/3.0/cancelar-preautorizacion/` | Cancela una preautorización activa. |
| POST | `/simulador/pagar` | Cambia el estado de un pedido existente para probar notificaciones. |

## Flujo de ejemplo

1. **Crear pedido**: envía la carga JSON del endpoint `iniciar-transaccion` y guarda el `hash_pedido` que retorna.
2. **Consultar medios de pago**: invoca `forma-pago/1.1/traer/` para mostrar opciones en tu UI.
3. **Simular pago**: usa `/simulador/pagar` con el hash obtenido en el paso 1 para marcarlo como pagado o revertido.
4. **Confirmar estado**: consulta `/api/pedidos/1.1/traer` para obtener el estado actualizado.

Todos los endpoints aceptan los campos reales descritos en la documentación, pero el mock ignora los valores extras para facilitar las pruebas.
