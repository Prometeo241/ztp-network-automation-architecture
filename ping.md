## Funcionamiento

- El ASG mantiene la instancia EC2 en ejecución y la reemplaza automáticamente en caso de fallo (auto-healing).
- La EC2 itera la lista de IPs de gestión (VLAN100) y ejecuta comprobaciones ICMP periódicas.
    - Si detecta pérdida de conectividad: Envía alertas a SNS (correo o Slack).
-Opcionalmente, se puede reportar métricas personalizadas a CloudWatch, para que Dashboards las visualice en tiempo real.

> Amazon QuickSight, potenciado con Amazon Q, agrega una capa de análisis inteligente y narrativas automáticas sobre las métricas recolectadas, permitiendo detectar patrones o anomalías de forma visual y asistida por IA.

![challenge-Página-3](https://github.com/user-attachments/assets/b9a227f4-2831-4058-ab61-01104c6f91e2)

> Costo mínimo y operación simple: Una única instancia con auto-recuperación y sin dependencias externas.

