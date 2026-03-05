
Este documento amplía la información presentada en la *etapa 3 – Backups Automáticos*, detallando el flujo completo, las interacciones entre servicios y el paso a paso del proceso.

Diagrama general

![challenge-Página-2](https://github.com/user-attachments/assets/091b0bd8-3d76-4421-ba08-00242dbdcb3b)


---

### Flujo lógico

1. EventBridge ejecuta la tarea programada (ej. todos los días a las 03:00 AM).
2. Tarea “Export DHCP” corre primero y publica el inventario en S3.
3. Lambda, ejecutando un script Python, toma el inventario de dispositivos desde S3 y establece conexión SSH a través de la IP que dinámicamente el DHCP asignó a la interface VLAN 100 de los dispositivos.
    > Lambda se integra con Secrets Manager para evitar hardcodear credenciales en el código.   
5. Se ejecuta show running-config (o equivalente) y el archivo se sube al bucket S3.
    > Sugerencia: Puede aprovecharse este proceso para nomenclar a los switches según su dirección IP, por ejemplo: 100.10.0.10 => Switch ID#10.
7. CloudWatch Logs registra ejecución y métricas; SNS/Slack notifica estado (OK/ERROR).

| Componente                 | Función               | Acción                                   |
| -------------------------- | --------------------- | --------------------------------------------- |
| **EventBridge**            | Planificador          | Desencadena la ejecución automática diaria.   |
| **Lambda ** | Servicio serverless para alojar código  | Extrae y sube las configuraciones.            |
| **S3 (versionado)**        | Repositorio central   | Almacena y preserva los backups.   |
| **CloudWatch Logs**        | Monitoreo y auditoría | Guarda métricas, logs y tiempos de ejecución. |
| **SNS**    | Push de notificacion          | Informa estado final del proceso.             |
| **Secrets Manager**        | Seguridad             | Repositorio para credenciales.       |
