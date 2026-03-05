### Anexo – Detalles del Servicio DHCP

### Alcance

El servicio DHCP opera exclusivamente sobre la **VLAN 100 (staging)**, dedicada al proceso de aprovisionamiento inicial (ZTP).  

Durante el proceso:
- El switch envía su **bootstrap (T0)** con la **Option 60**, indicando su tipo o fabricante.  
- El servidor DHCP responde con la **Option 66**, entregando la **URL del template** que debe descargar desde S3 (Esta URL depende de cómo se haya identificado el equipo mediante la Option 60).
- Dicha URL apunta a un dominio lógico (por ejemplo, `http://ztp-test.s3.amazonaws.com/template.cfg`), lo que evita el uso de direcciones IP fijas y mantiene la infraestructura flexible ante futuros cambios.

>NOTA: La URL utiliza HTTP, por lo que es posible generar un CNAME en Route 53 para acortarla y simplificar su uso.
Esta práctica resulta útil para evitar limitaciones en algunos equipos frente a URLs extensas o certificados SSL.
Dado que el tráfico HTTP viaja a través de la VPN Site-to-Site, no resulta crítico aplicar cifrado extremo a extremo.

---

### Opciones DHCP Usadas (Agnóstico a Fabricante)

| **Opción** | **Propósito** | **Ejemplo de uso en este proyecto** |
|-------------|---------------|-------------------------------------|
| **60 – Vendor Class Identifier** | Identifica el tipo o fabricante del equipo, permitiendo al servidor aplicar distintas políticas o pools. | `SWITCH`, `AP`, `FIREWALL` |
| **66 – Bootfile Server Name** | Indica la ubicación del servidor que contiene el archivo de configuración inicial (Template). | `http://ztp-test.s3.amazonaws.com/template.cfg` |
| **43 – Vendor Specific Info** | Utilizada principalmente por controladoras/APs para incluir parámetros adicionales como URL del controller o site ID. | `controller-url=https://controller.test.net` |

Estas opciones permiten mantener un flujo totalmente automatizado, donde el equipo recién encendido obtiene no solo su IP, sino también la referencia lógica al template correspondiente según su tipo.

---

### Estrategia de Leases y Alta Disponibilidad (HA)

El servicio DHCP se implementa detrás un **Network Load Balancer (NLB)** que distribuye las solicitudes UDP/67 hacia un **Auto Scaling Group** de dos instancias EC2.

Principales características:

- **Sincronización de estado:** uso de almacenamiento compartido o protocolo de failover nativo del servicio DHCP para evitar leases duplicados.  
- **Supervisión:** Health checks del NLB sobre y alarmas CloudWatch que actúan sobre el ASG ante pérdida de respuesta por parte del servidor.
- **Recuperacion automatica**: En caso de falla, el ASG *puede terminar la instancia afectada* y *relanzarla* a partir de una Golden AMI y su correspondiente user data, garantizando la restauración del servicio y la continuidad operativa.

> Se denomina Golden AMI a la imagen maestra funcional de la instancia, mientras que la User Data contiene el script de arranque encargado de descargar dependencias, registrar servicios o inicializar procesos dentro de la VM.
>Ambos elementos son gestionados por el Launch Template, que el ASG utiliza al momento de recrear una instancia.
---

### Justificación del Uso de Amazon S3 como repositorio

El repositorio de templates se aloja en **Amazon S3**, aprovechando sus capacidades nativas de **alta disponibilidad, durabilidad (99.999999999%)** y **versionado**.

**Motivos de elección:**

- **Alta disponibilidad global:** Ideal para entornos distribuidos donde múltiples sitios pueden acceder simultáneamente.  
- **Versioning habilitado:** Cada cambio en un template genera una nueva versión sin sobrescribir la anterior, permitiendo rollback inmediato.  
- **Integración con Route 53:** El acceso se realiza mediante un dominio lógico (`ztp.test.net`), desacoplando el almacenamiento físico de la configuración del equipo.  
- **Compatibilidad HTTP/HTTPS:** Facilita descargas directas.
- **Escalabilidad automática:** Sin límite práctico de objetos , simplificando el crecimiento futuro.

>NOTA: El almacenamiento en S3 es del tipo "Object based", de aqui que se desprende la posibilidad de *versionado* en los objetos almacenados.
