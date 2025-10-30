"""Mock server that simulates the PagoPar API documented in soporte.pagopar.com."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="PagoPar Mock API", version="0.1.0")


class BaseRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    token: str = Field(..., description="Token generado por el comercio")
    token_publico: Optional[str] = Field(None, description="Clave pública del comercio")


class Buyer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: str
    documento: str
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    razon_social: Optional[str] = None


class Item(BaseModel):
    model_config = ConfigDict(extra="ignore")

    nombre: str
    cantidad: int = 1
    precio_total: float


class TransactionRequest(BaseRequest):
    id_pedido_comercio: str
    monto_total: float
    comprador: Buyer
    compras_items: List[Item]
    forma_pago: Optional[int] = None
    descripcion_resumen: Optional[str] = None
    fecha_maxima_pago: Optional[str] = None


class TransactionResult(BaseModel):
    data: str
    pedido: str


class FormasPagoRequest(BaseRequest):
    pass


class PedidoStatusRequest(BaseRequest):
    hash_pedido: str


class PedidoStatus(BaseModel):
    pagado: bool
    forma_pago: str
    fecha_pago: Optional[str]
    monto: float
    fecha_maxima_pago: Optional[str]
    hash_pedido: str
    numero_pedido: str
    cancelado: bool
    forma_pago_identificador: str
    token: str
    mensaje_resultado_pago: Dict[str, str]


class ClienteRequest(BaseRequest):
    identificador_cliente: str
    email: str
    nombre: Optional[str] = None
    documento: Optional[str] = None


class TarjetaRequest(BaseRequest):
    token_cliente: str
    alias_tarjeta: Optional[str] = None


class ConfirmarTarjetaRequest(BaseRequest):
    token_tarjeta: str
    codigo_autorizacion: str


class ListarTarjetasRequest(BaseRequest):
    token_cliente: str


class EliminarTarjetaRequest(BaseRequest):
    token_tarjeta: str


class CobroRecurrenteRequest(BaseRequest):
    token_cliente: str
    token_tarjeta: str
    monto: float
    descripcion: Optional[str] = None


class PreautorizarRequest(CobroRecurrenteRequest):
    monto_maximo: float


class ConfirmarPreautorizarRequest(BaseRequest):
    token_preauthorizacion: str
    monto: float


class CancelarPreautorizarRequest(BaseRequest):
    token_preauthorizacion: str


class SimularPagoRequest(BaseModel):
    hash_pedido: str
    pagado: bool = True
    forma_pago: str = "Tarjetas de crédito/débito"


orders: Dict[str, Dict] = {}
customers: Dict[str, Dict] = {}
cards: Dict[str, Dict] = {}
preauths: Dict[str, Dict] = {}


def _now_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


@app.post("/api/comercios/2.0/iniciar-transaccion")
def iniciar_transaccion(payload: TransactionRequest):
    hash_pedido = uuid4().hex
    numero_pedido = str(len(orders) + 1)
    orders[hash_pedido] = {
        "pagado": False,
        "forma_pago": payload.forma_pago or 9,
        "monto": float(payload.monto_total),
        "hash_pedido": hash_pedido,
        "numero_pedido": numero_pedido,
        "fecha_maxima_pago": payload.fecha_maxima_pago or (
            datetime.utcnow() + timedelta(days=3)
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "mensaje_resultado_pago": {
            "titulo": "Pedido pendiente de pago",
            "descripcion": "Pago simulado en espera de confirmación."
        },
    }
    return {
        "respuesta": True,
        "resultado": [TransactionResult(data=hash_pedido, pedido=numero_pedido).model_dump()],
    }


@app.post("/api/forma-pago/1.1/traer/")
def formas_pago(_: FormasPagoRequest):
    return {
        "respuesta": True,
        "resultado": [
            {
                "forma_pago": "25",
                "titulo": "PIX",
                "descripcion": "PIX vía QR",
                "monto_minimo": "1000",
                "porcentaje_comision": "3.00",
            },
            {
                "forma_pago": "9",
                "titulo": "Tarjetas de crédito",
                "descripcion": "Acepta Visa, Mastercard, American Express, Cabal, Panal, Discover, Diners Club.",
                "monto_minimo": "1000",
                "porcentaje_comision": "6.82",
            },
            {
                "forma_pago": "10",
                "titulo": "Tigo Money",
                "descripcion": "Utilice sus fondos de Tigo Money",
                "monto_minimo": "1000",
                "porcentaje_comision": "6.82",
            },
        ],
    }


@app.post("/api/pedidos/1.1/traer")
def traer_pedido(payload: PedidoStatusRequest):
    order = orders.get(payload.hash_pedido)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    status = PedidoStatus(
        pagado=order["pagado"],
        forma_pago="Tarjetas de crédito" if order["forma_pago"] == 9 else "Desconocido",
        fecha_pago=order.get("fecha_pago"),
        monto=order["monto"],
        fecha_maxima_pago=order["fecha_maxima_pago"],
        hash_pedido=order["hash_pedido"],
        numero_pedido=order["numero_pedido"],
        cancelado=order.get("cancelado", False),
        forma_pago_identificador=str(order["forma_pago"]),
        token=payload.token,
        mensaje_resultado_pago=order["mensaje_resultado_pago"],
    )
    return {"respuesta": True, "resultado": [status.model_dump()]}


@app.post("/api/pago-recurrente/3.0/agregar-cliente/")
def agregar_cliente(payload: ClienteRequest):
    token_cliente = uuid4().hex
    customers[token_cliente] = {
        "identificador": payload.identificador_cliente,
        "email": payload.email,
        "nombre": payload.nombre,
        "documento": payload.documento,
        "creado": _now_str(),
    }
    return {
        "respuesta": True,
        "resultado": {
            "token_cliente": token_cliente,
            "identificador_cliente": payload.identificador_cliente,
        },
    }


@app.post("/api/pago-recurrente/3.0/agregar-tarjeta/")
def agregar_tarjeta(payload: TarjetaRequest):
    if payload.token_cliente not in customers:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    token_tarjeta = uuid4().hex
    cards[token_tarjeta] = {
        "token_cliente": payload.token_cliente,
        "alias": payload.alias_tarjeta or "Tarjeta",
        "estado": "pendiente",
        "creado": _now_str(),
    }
    return {
        "respuesta": True,
        "resultado": {
            "token_tarjeta": token_tarjeta,
            "alias": cards[token_tarjeta]["alias"],
            "estado": "pendiente",
        },
    }


@app.post("/api/pago-recurrente/3.0/confirmar-tarjeta/")
def confirmar_tarjeta(payload: ConfirmarTarjetaRequest):
    tarjeta = cards.get(payload.token_tarjeta)
    if not tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    tarjeta["estado"] = "confirmada"
    tarjeta["confirmada"] = _now_str()
    tarjeta["codigo_autorizacion"] = payload.codigo_autorizacion
    return {"respuesta": True, "resultado": tarjeta}


@app.post("/api/pago-recurrente/3.0/listar-tarjeta/")
def listar_tarjeta(payload: ListarTarjetasRequest):
    resultado = []
    for token, tarjeta in cards.items():
        if tarjeta["token_cliente"] == payload.token_cliente:
            resultado.append({"token_tarjeta": token, **tarjeta})
    return {"respuesta": True, "resultado": resultado}


@app.post("/api/pago-recurrente/3.0/eliminar-tarjeta/")
def eliminar_tarjeta(payload: EliminarTarjetaRequest):
    tarjeta = cards.pop(payload.token_tarjeta, None)
    if not tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    return {"respuesta": True, "resultado": {"token_tarjeta": payload.token_tarjeta, "estado": "eliminada"}}


@app.post("/api/pago-recurrente/3.0/pagar/")
def cobro_recurrente(payload: CobroRecurrenteRequest):
    if payload.token_cliente not in customers or payload.token_tarjeta not in cards:
        raise HTTPException(status_code=404, detail="Cliente o tarjeta no encontrada")
    hash_pedido = uuid4().hex
    numero_pedido = str(len(orders) + 1)
    orders[hash_pedido] = {
        "pagado": True,
        "forma_pago": 9,
        "monto": payload.monto,
        "hash_pedido": hash_pedido,
        "numero_pedido": numero_pedido,
        "fecha_pago": _now_str(),
        "fecha_maxima_pago": _now_str(),
        "mensaje_resultado_pago": {
            "titulo": "Pago recurrente exitoso",
            "descripcion": payload.descripcion or "Cobro simulado aprobado.",
        },
    }
    return {
        "respuesta": True,
        "resultado": {
            "hash_pedido": hash_pedido,
            "numero_pedido": numero_pedido,
            "fecha_pago": orders[hash_pedido]["fecha_pago"],
            "monto": payload.monto,
        },
    }


@app.post("/api/pago-recurrente/3.0/preautorizar/")
def preautorizar(payload: PreautorizarRequest):
    if payload.token_cliente not in customers or payload.token_tarjeta not in cards:
        raise HTTPException(status_code=404, detail="Cliente o tarjeta no encontrada")
    token_preauthorizacion = uuid4().hex
    preauths[token_preauthorizacion] = {
        "token_cliente": payload.token_cliente,
        "token_tarjeta": payload.token_tarjeta,
        "monto_maximo": payload.monto_maximo,
        "monto_confirmado": None,
        "estado": "pendiente",
        "creado": _now_str(),
    }
    return {
        "respuesta": True,
        "resultado": {
            "token_preauthorizacion": token_preauthorizacion,
            "estado": "pendiente",
        },
    }


@app.post("/api/pago-recurrente/3.0/confirmar-preautorizacion/")
def confirmar_preauthorizacion(payload: ConfirmarPreautorizarRequest):
    preauth = preauths.get(payload.token_preauthorizacion)
    if not preauth:
        raise HTTPException(status_code=404, detail="Preautorización no encontrada")
    if payload.monto > preauth["monto_maximo"]:
        raise HTTPException(status_code=400, detail="El monto supera el máximo permitido")
    preauth["estado"] = "confirmada"
    preauth["monto_confirmado"] = payload.monto
    preauth["confirmada"] = _now_str()
    return {"respuesta": True, "resultado": preauth}


@app.post("/api/pago-recurrente/3.0/cancelar-preautorizacion/")
def cancelar_preauthorizacion(payload: CancelarPreautorizarRequest):
    preauth = preauths.get(payload.token_preauthorizacion)
    if not preauth:
        raise HTTPException(status_code=404, detail="Preautorización no encontrada")
    preauth["estado"] = "cancelada"
    preauth["cancelada"] = _now_str()
    return {"respuesta": True, "resultado": preauth}


@app.post("/simulador/pagar")
def simular_pago(payload: SimularPagoRequest):
    order = orders.get(payload.hash_pedido)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    order["pagado"] = payload.pagado
    order["fecha_pago"] = _now_str() if payload.pagado else None
    order["forma_pago"] = 9 if payload.pagado else order.get("forma_pago", 9)
    order["mensaje_resultado_pago"] = {
        "titulo": "Pedido pagado" if payload.pagado else "Pago revertido",
        "descripcion": "Estado actualizado manualmente en el simulador.",
    }
    return {"respuesta": True, "resultado": order}
