# Chatbot Comercial

Chatbot web integrable para PyMEs que utiliza Claude AI para conversaciones naturales.

## Características

- ✅ Widget integrable en cualquier sitio web
- ✅ Configuraciones específicas por industria (restaurantes, e-commerce, etc.)
- ✅ Conversaciones persistentes por sesión
- ✅ Diseño responsive y moderno
- ✅ API REST para integraciones custom

## Demo

Visita `/demo` para ver el chatbot en acción.

## Integración

```html
<script src="https://tu-dominio.com/widget.js"></script>
<script>
  inicializarChatbot({
    empresa_id: "tu_empresa",
    tipo_negocio: "restaurante", // o "ecommerce", "general"
    api_url: "https://tu-dominio.com"
  });
</script>
```

## Variables de Entorno

- `CLAUDE_API_KEY`: Tu API key de Anthropic Claude
- `PORT`: Puerto del servidor (por defecto 5000)

## Deployment

1. Hacer fork de este repositorio
2. Conectar con Railway/DigitalOcean
3. Configurar variables de entorno
4. Deploy automático

## Precios

- Hobby: $200 USD/mes por cliente
- Profesional: $500 USD/mes por cliente
- Empresarial: Cotización personalizada
