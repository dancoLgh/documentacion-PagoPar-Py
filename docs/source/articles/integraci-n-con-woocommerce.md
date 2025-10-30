# Integración con Woocommerce

> Categoría: Woocommerce | Idioma: es

Primeramente  se debe instalar Pagopar desde el apartado de plugin/añadir nuevo.

![](https://desk.zoho.com/DocsDisplay?zgId=687739706&mode=inline&blockId=2g9sraf17a057ee3040a4a333b43b75a3a948)

![Notes](https://static.zohocdn.com/zoho-desk-editor/static/images/file.png/)

Por el momento el plugin se debe [descargar el plugin desde el siguiente link](https://drive.google.com/file/d/1g-MbMKbHu5pvrrP8xMoYc9lJus1a7Y1t/view?usp=sharing) ya que no está accesible desde la tienda temporalmente

Luego de la instalación y activación del plugin dentro del sitio web, debe ir en ajustes del plugin de Pagopar, y completar los campos que aparecen en dicha página.

![](https://desk.zoho.com/DocsDisplay?zgId=687739706&mode=inline&blockId=2g9sr61868e2d85524af6b101c76e9b13514f)

Los datos de clave pública y privada lo obtienes desde tu registro de Pagopar.com, en la sección «Integrar con mi sitio web/app».

![](https://desk.zoho.com/DocsDisplay?zgId=687739706&mode=inline&blockId=2g9sr9f13ae55550d408f813d48f3aec96247)

En esa misma página, hay que colocar dos valores inicialmente, que son la URL de respuesta y de redireccionamiento, estos datos lo obtendrás de la página de ajustes del plugin de Pagopar en tu WordPress.​​​​

---

Dependiendo del tipo de producto o servicio que vayas a vender dentro del sitio web, en  los ajustes del plugin aparecerá un desplegable donde podrás seleccionar si deseas o no utilizar el delivery integrado al plugin que es AEX.

![](https://desk.zoho.com/DocsDisplay?zgId=687739706&mode=inline&blockId=2g9src66fb4988a44448098f554629acf7014)

Si no utilizarás AEX podes seleccionar esa opción y posteriormente configurar cualquier opción de envio desde los ajustes de Woocommerce en caso de que sea necesario.

En cambio, si se utilizará AEX es un requisito que los productos de Woocommerce estén asociados a la categoría Pagopar. Estas categorías las encontrarás en "editar producto"

![](https://desk.zoho.com/DocsDisplay?zgId=687739706&mode=inline&blockId=2g9srfd8d7f18b3ab4fe7bc7e0fe24c2095bb)

Para algunos productos se solicitará que se agreguen las dimensiones debido a que el delivery de AEX realiza el cálculo del costo del envio según las dimensiones del producto y la distancia de envio.

---

Una vez que finalices las configuraciones deberás simular un pedido de venta, generando un pedido y posteriormente realizar el pase a producción.
