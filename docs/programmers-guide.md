# Guía técnica resumida para integrar PagoPar

Esta guía organiza los contenidos públicos del centro de ayuda de PagoPar en un formato pensado para desarrolladores. Puedes volver a ejecutar `scripts/fetch_pagopar_docs.py` cuando necesites refrescar la información local o generar las copias en `docs/source/articles/` y `data/pagopar_articles.json`.

## Entornos, llaves y pasos previos

- **Ambientes disponibles:** se trabaja inicialmente con las llaves de desarrollo/staging y, una vez verificada la implementación, se realiza el pase a producción para habilitar controles como la validación de IPs y las notificaciones de pagos recurrentes. 【F:docs/source/articles/entornos-pase-a-producci-n.md†L5-L23】
- **Checklist de habilitación:**
  1. Crear pedidos correctamente mediante `iniciar-transaccion`.
  2. Recibir el webhook de pago en la URL de respuesta y devolver exactamente el JSON recibido.
  3. Consultar el estado de un pedido con `/api/pedidos/1.1/traer`.
  Después de estas pruebas, actualiza las IPs habilitadas y copia nuevamente las llaves de producción. 【F:docs/source/articles/entornos-pase-a-producci-n.md†L25-L50】
- **Postman oficial:** PagoPar mantiene una colección pública con todos los endpoints mencionados aquí. 【F:docs/source/articles/api-integracion-medios-pagos.md†L12-L16】

## Patrón de autenticación

Cada endpoint espera un `token` SHA1 calculado con la clave privada del comercio. Los patrones más utilizados son:

| Uso | Fórmula |
| --- | --- |
| Crear pedido (`iniciar-transaccion`) | `sha1(private_key + id_pedido_comercio + monto_total)`【F:docs/source/articles/api-integracion-medios-pagos.md†L20-L51】 |
| Listar medios de pago (`forma-pago/1.1/traer/`) | `sha1(private_key + "FORMA-PAGO")`【F:docs/source/articles/api-integracion-medios-pagos.md†L206-L230】 |
| Consultar pedido (`pedidos/1.1/traer`) | `sha1(private_key + "CONSULTA")`【F:docs/source/articles/api-integracion-medios-pagos.md†L620-L650】 |
| Webhook de pago | `sha1(private_key + hash_pedido)`【F:docs/source/articles/api-integracion-medios-pagos.md†L368-L400】 |
| Link de suscripción | `sha1(private_key + tipo_accion)` (tipo = `suscripcion`, `pagado`, `desuscripcion`).【F:docs/source/articles/link-suscripcion.md†L32-L120】 |
| Preautorizaciones/recurrencias | Cada operación recurrente acepta el `token` generado con la clave privada según corresponda (el mock ignora la validación).【F:docs/source/articles/catastro-tarjetas-pagos-recurrentes-preautorizacion.md†L1-L120】 |

## Flujo base de cobro en línea

1. **Iniciar transacción (`POST https://api.pagopar.com/api/comercios/2.0/iniciar-transaccion`)**: envía los datos del comprador, los ítems y `forma_pago`. El servicio devuelve `resultado[0].data`, que es el hash de pedido a persistir. 【F:docs/source/articles/api-integracion-medios-pagos.md†L30-L168】
2. **Mostrar checkout**: redirige a `https://www.pagopar.com/pagos/$hash?forma_pago=<id>` para que el cliente complete la operación. Consulta `forma-pago/1.1/traer/` si necesitas poblar tu UI con los medios habilitados. 【F:docs/source/articles/api-integracion-medios-pagos.md†L188-L244】
3. **Webhook de resultado**: Pagopar notificará en la URL de respuesta del comercio. Valida el `token` recibido antes de marcar el pedido como pagado o reversado y devuelve exactamente el JSON recibido. 【F:docs/source/articles/api-integracion-medios-pagos.md†L360-L462】
4. **Consulta final (`POST https://api.pagopar.com/api/pedidos/1.1/traer`)**: con el hash confirma en tiempo real el estado del pedido y muestra el resultado al cliente. 【F:docs/source/articles/api-integracion-medios-pagos.md†L608-L708】

| Paso | Endpoint | Método | Notas clave |
| --- | --- | --- | --- |
| 1 | `/api/comercios/2.0/iniciar-transaccion` | POST | Devuelve hash y número de pedido; guarda `resultado[0].data`. |
| 2 | `https://www.pagopar.com/pagos/{hash}` | GET | Adjunta `forma_pago` si deseas forzar un medio específico. |
| 2 (opcional) | `/api/forma-pago/1.1/traer/` | POST | Devuelve ID, descripción y comisión de cada medio. |
| 3 | URL de respuesta del comercio | POST | Pagopar envía `resultado` con el estado actual. Responde con el mismo JSON. |
| 4 | `/api/pedidos/1.1/traer` | POST | Recomendado incluso si recibiste el webhook para verificar el estado real. |

### Manejo de errores

Pagopar publica un catálogo de errores comunes al iniciar la transacción (token incorrecto, forma de pago no habilitada, IDs duplicados, montos inválidos, etc.). Consulta esta lista cuando recibas una respuesta negativa y ajusta los datos enviados. 【F:docs/source/articles/listado-de-errores-al-iniciar-transacci-n.md†L5-L25】

## Envíos tercerizados (pickup/delivery)

Si usas los servicios logísticos integrados, incorpora los siguientes endpoints antes de crear el pedido:

| Objetivo | Endpoint | Observaciones |
| --- | --- | --- |
| Obtener ciudades | `/api/ciudades/1.1/traer` | Entrega los IDs necesarios para `comprador.ciudad`. |
| Obtener categorías | `/api/categorias/2.0/traer` | Devuelve las categorías de envío requeridas por los couriers. |
| Calcular flete | `/api/calcular-flete/2.0/traer` | El token se genera con `sha1(private_key + "CALCULAR-FLETE")`. |
| Crear pedido con envío | `/api/comercios/2.0/iniciar-transaccion` | Incluye los campos de logística descritos en la guía de pickup/delivery. |

Estos pasos permiten que Pagopar muestre costos y opciones de entrega en su checkout. 【F:docs/source/articles/integraci-n-de-servicios-de-pickup-delivery.md†L1-L210】

## Pagos recurrentes, tokenización y preautorizaciones

La API recurrente (v3.0) cubre todo el ciclo de vida de la tarjeta tokenizada:

| Acción | Endpoint | Respuesta típica |
| --- | --- | --- |
| Registrar cliente | `/api/pago-recurrente/3.0/agregar-cliente/` | Devuelve `token_cliente`. |
| Agregar tarjeta | `/api/pago-recurrente/3.0/agregar-tarjeta/` | Devuelve `token_tarjeta` en estado `pendiente`. |
| Confirmar tarjeta | `/api/pago-recurrente/3.0/confirmar-tarjeta/` | Cambia el estado a `confirmada`. |
| Listar tarjetas | `/api/pago-recurrente/3.0/listar-tarjeta/` | Retorna los tokens activos con sus alias. |
| Eliminar tarjeta | `/api/pago-recurrente/3.0/eliminar-tarjeta/` | Marca la tarjeta como eliminada. |
| Cobrar | `/api/pago-recurrente/3.0/pagar/` | Genera un nuevo `hash_pedido` pagado. |
| Preautorizar | `/api/pago-recurrente/3.0/preautorizar/` | Devuelve `token_preauthorizacion`. |
| Confirmar preautorización | `/api/pago-recurrente/3.0/confirmar-preautorizacion/` | Confirma un monto menor o igual al máximo. |
| Cancelar preautorización | `/api/pago-recurrente/3.0/cancelar-preautorizacion/` | Cambia el estado a `cancelada`. |

La versión 1.1 de la API recurrente mantiene los mismos conceptos pero con rutas `1.1`/`2.0`, útiles si mantienes integraciones legadas. 【F:docs/source/articles/catastro-tarjetas-pagos-recurrentes-preautorizacion.md†L1-L200】【F:docs/source/articles/pagos-recurrentes-v-a-bancard-pagopar.md†L1-L160】

## Links de suscripción y notificaciones

Los links de suscripción generan notificaciones en la URL configurada con el siguiente esquema:

- Campos principales: `tipo_accion` (`suscripcion`, `pagado`, `desuscripcion`), `token`, datos del `usuario` y de la `suscripcion` o del `pago`.
- Responde siempre con el mismo JSON que recibiste para confirmar la recepción y evitar reintentos. 【F:docs/source/articles/link-suscripcion.md†L14-L116】

## Sincronización de productos

Para sincronizar links de venta desde tu catálogo externo utiliza:

| Acción | Endpoint |
| --- | --- |
| Crear producto | `/api/links-venta/1.1/agregar/` |
| Editar producto | `/api/links-venta/1.1/editar/` |

Ambos servicios comparten la misma estructura de autenticación basada en la clave privada del comercio. 【F:docs/source/articles/sincronizaci-n-de-productos.md†L1-L40】

## Complementos y plugins

- **WooCommerce**: la guía oficial detalla la configuración del plugin, incluyendo dónde ingresar las llaves y cómo probar pedidos en staging antes de pasar a producción. 【F:docs/source/articles/integraci-n-con-woocommerce.md†L1-L120】
- **Servicio de delivery**: revisa la guía completa cuando necesites enviar parámetros adicionales como dirección del vendedor, referencia y coordenadas. 【F:docs/source/articles/integraci-n-de-servicios-de-pickup-delivery.md†L220-L360】

## Herramientas del repositorio

- `scripts/fetch_pagopar_docs.py`: re-descarga los artículos públicos en JSON y Markdown.
- `mock_server/app.py`: expone un entorno simulado con los endpoints principales para pruebas locales (`uvicorn mock_server.app:app --reload`).
- `mock_server/README.md`: detalla los pasos para levantar el mock y un flujo típico de prueba.
