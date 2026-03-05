This repository is published for educational and demonstration purposes.

# Propuesta de Arquitectura ZTP – Centro Logístico

Este repositorio presenta una propuesta de arquitectura para implementar un proceso de **Zero Touch Provisioning (ZTP)** orientado al aprovisionamiento masivo de infraestructura de red en un entorno logístico.

La idea surge a partir de un challenge técnico recibido durante un proceso de entrevista. Me pareció una buena oportunidad para documentar y compartir el razonamiento detrás de la solución propuesta, así como el enfoque arquitectónico y las herramientas que podrían utilizarse para resolver el problema.

El objetivo fue diseñar un proceso automatizado y escalable para el aprovisionamiento de switches, access points y firewalls, considerando buenas prácticas de automatización de redes, principios DevOps y el uso de servicios cloud.

Dado que actualmente no dispongo de un entorno sandbox de AWS, la arquitectura presentada es principalmente conceptual y no fue desplegada completamente. Por este motivo, es posible que existan aspectos perfectibles o detalles que podrían optimizarse en un entorno real.

Todo el trabajo fue desarrollado como parte de mis estudios autodidactas en automatización de redes, cloud y prácticas DevOps.

Además, es mi primer repositorio público en GitHub, por lo que cualquier sugerencia o feedback será más que bienvenido.

Muchas gracias por tomarte el tiempo de revisarlo.


## Contexto
Una empresa de logística está por inaugurar un nuevo sector crítico en su Centro de Distribución.  
El objetivo es diseñar y automatizar el aprovisionamiento, configuración y operación de la red con alta disponibilidad y mínima intervención manual.

---

## Arquitectura requerida
- 48 Switches de acceso
- 500 Access Points gestionados por controladora
- Firewalls perimetrales
- Enlaces de Internet redundantes

## Principios de diseño:
- Zero Touch Provisioning (ZTP)
- Alta disponibilidad
- Escalabilidad y consistencia (CI/CD)
- Backups automáticos y recuperabilidad
- Logs y Monitoria

---
## Introduccion
Se decidió adoptar una infraestructura 100% Cloud como base para el proyecto, con el objetivo de aprovechar las capacidades nativas de alta disponibilidad, elasticidad y resiliencia que ofrece este entorno.
Esta elección permite garantizar la continuidad operativa, reducir los puntos únicos de falla y simplificar las tareas de recuperación ante incidentes.

El entorno Cloud actúa como plataforma central de control y orquestación. De esta forma, se minimiza la intervención manual y se asegura que el despliegue de la infraestructura sea agnóstico a la cantidad final de equipamiento a instalar, garantizando una completa escalabilidad a demanda.
El diseño permite versionar plantillas, distribuir configuraciones estándar y ejecutar aprovisionamientos masivos mediante scripts y APIs, logrando una operación más confiable y auditable.

## 🧩 Componentes del diseño

- **Route 53**  
  Servicio que permita hostear dominios y resolución DNS. En este proyecto se utilizará para abstraer de IP's al servicio de Zero Touch Provisioning [ZTP]. Este principio para la escalabilidad ya que, de requerirse cambios o migracion en la infraestructura backend, resulta transparente para el consumo del servicio que resuelve por URL.

- **VPN Endpoint**  
  Túnel privado on-prem ⇄ AWS. Aísla el tráfico ZTP y evita exposición pública.

- **Network Load Balancer [NLB] (Cross-AZ) + Target Group**  
  Balanceo UDP hacia las instancias ZTP/DHCP distribuidas en múltiples zonas de disponibilidad.  
  Health checks y alta disponibilidad activa/activa.

- **Auto Scaling Group [ASG] ]+ Launch Template + Gold AMI**  
  Mecanismo de auto-recuperación para los nodos del servicio ZTP/DHCP.  
  La AMI “gold” incluye la configuración base y dependencias necesarias, mientras que el ASG reemplaza instancias ante fallas o mantenimiento.
  Dado que las soluciones DHCP resilientes soportan un máximo de dos, es que se decidió que la configuracion del ASG sea de: Min=Desired=Max=2 

- **Elastic Compute Cloud [EC2] (Pares HA) – Servicio DHCP**  
  Servidor DHCP redundante hosteado en máquinas virtuales en nube AWS [EC2].  
  Asigna direcciones IP y entrega **Option 66** con la URL de descarga de configuración según la **Option 60**. La combinación de estas dos opciones permite el autoaprovisionamiento de equipamiento según su identificación respectivamente.

- **Simple Storage Service [S3] (Repositorio de alta disponibilidad)**  
  Almacena los `.cfg` finales generados por el motor de plantillas Jinja2.  
  Configurado en modo público con **bucket policy restringida por IP origen **.  
  Se habilita **versioning** para mantener histórico y permitir rollback.

- **CloudWatch**  
  Supervisión de todo el entorno Cloud mediante alarmas nativas y customizadas. Recolecta métricas y alarmas de disponibilidad del entorno ZTP.

- **Quicksight + Amazon Q**  
  Se integra QuickSight con Amazon Q y CloudWatch Metrics para ofrecer visualizaciones inteligentes y análisis asistido por IA, aprovechando las métricas nativas de la infraestructura para monitorear el rendimiento y la        disponibilidad de la red.

---

### A continuación, se detallan los pasos de la solución propuesta junto con su implementación técnica, abarcando desde el diseño de aprovisionamiento hasta la automatización operativa y el monitoreo inteligente.

#### 1. Aprovisionamiento Automatizado (ZTP)
**Patrón elegido: DHCP - Opcion 60 + 66 - Modelo híbrido con backend en AWS**  
Durante la etapa de diseño inicial se evaluó un enfoque on-premise, montando un servidor local de DHCP + ZTP junto al firewall.
Si bien este método es efectivo para el despliegue inicial (por ejemplo, los 48 switches y 500 APs previstos), se identificaron limitaciones operativas:

❌ Dependencia de un servidor temporal: Una vez retirado el servidor de staging, nuevos equipos (como un eventual switch 501) no podrían autoprovisionarse.  
❌ Falta de alta disponibilidad: El ZTP local dependería de un único nodo sin redundancia ni escalabilidad.  
❌ Gestión manual de reactivación: Cada incorporación de equipamiento requeriría volver a levantar el entorno de provisión temporal.  

💡Para resolver estas limitaciones se adoptó un modelo híbrido con backend en AWS, conservando la lógica pero moviendo la capa de servicio y DNS a la nube.

**Flujo general:**
1. El firewall on-premise actúa como DHCP Relay, reenviando los mensajes DISCOVER hacia la nube mediante una VPN Site-to-Site levantada en una conectividad redundante a internet.
2. En AWS, el tráfico DHCP es recibido por un Network Load Balancer (NLB), que distribuye las solicitudes hacia un grupo de instancias EC2 donde esta hosteado el servicio DHCP en manera redundante.
3. Cada servidor DHCP responde incluyendo en la Option 66 la URL correspondiente al archivo de configuración alojado en Amazon S3. El parámetro Option 60 permite identificar el tipo de equipo (switch, AP, firewall) y devolver la URL del template que le corresponda.
4. El equipo descarga su plantilla desde S3 (por HTTP/HTTPS) y ejecuta el **.cfg** que aplica la configuración.

De esta manera, Route 53 [DNS] + NLB + ASG + S3 conforman una arquitectura resiliente, modular y 100 % agnóstica de fabricante, manteniendo el patrón clásico de Zero Touch Provisioning pero con disponibilidad y escalabilidad propias de la nube.

- [Zero Touch Provisioning (ZTP)](./ztp/README.md)

---

#### 2. Servicio DHCP en la nube

El **servicio DHCP** cumple un rol clave dentro del flujo ZTP, al proveer a cada equipo la información necesaria para iniciar su configuración automática.

El **firewall on-premise** actúa como **DHCP Relay**, reenviando los mensajes durante todo el intercambio del proceso DHCP hacia la nube a través de la **VPN Site-to-Site**.  
En AWS, un **Network Load Balancer (NLB)** con listeners **UDP/67 [bootps]** distribuye las solicitudes hacia un **Auto Scaling Group** de **dos instancias EC2** que ejecutan el servicio DHCP en modo **High Availability (HA)**.

- [DHCP Configuration](./dhcp.md)

#### 3. Backups Automáticos

La infraestructura debe garantizar no solo su despliegue inicial (ZTP), sino también su capacidad de recuperación y trazabilidad.
Para ello, se implementa un proceso de backups automáticos de configuraciones de switches, Access Points y firewall, sin intervención manual.

###### Objetivo

Respaldar rutinariamente las configuraciones y almacenarlas en una ubicación central, segura y versionada, manteniendo trazabilidad, integridad y posibilidad de restauración rápida.

###### Enfoque Cloud-Friendly

El sistema de backups se apoya en servicios nativos de AWS, permitiendo escalar sin necesidad de infraestructura on-prem adicional.

- [BackUp Configuration](./backup.md)

#### 4. Restauración y Recuperación de Configuración

La estructura propuesta en [BackUp Configuration](./backup.md) es totalmente consistente con el ciclo de restauración o recuperación de equipos.
Ambos procesos comparten la misma arquitectura base: DHCP → Lambda → S3 → CloudWatch → SNS.

##### Diferencia principal

Durante el proceso de backup, la función Lambda ejecuta un *GET remoto de la running-config* desde cada switch y la almacena en S3 con versionado habilitado.
En cambio, *en el proceso de restauración, la función Lambda realiza la operación inversa*:
*recupera (GET) la configuración almacenada en S3* y la aplica al switch vía conexión SSH segura.

##### Consideraciones

- La lógica Python difiere (modo lectura vs. modo escritura), pero la arquitectura, la trazabilidad y los mecanismos de monitoreo se mantienen idénticos.
- El versionado en S3 permite restaurar cualquier versión histórica de la configuración.
- Las alertas y métricas continúan integradas mediante CloudWatch y SNS, sin necesidad de agregar servicios nuevos.

> El mismo diseño que garantiza backups seguros y auditables permite también la restauración confiable y automatizada, cerrando el ciclo operativo de gestión de configuración de red.

#### 5. Integración Continua y Despliegue (CI/CD)

La infraestructura propuesta se complementa con un flujo de CI/CD (Continuous Integration / Continuous Deployment) que automatiza la validación y distribución de configuraciones de red.

- Aprovisionamiento [ZTP] y restauracion leen desde S3 → config se aplica.
- CI/CD: Cualquier cambio o nueva necesidad de configuracion "out of the box" hacia S3 → config actualizada.

Desde S3, ese .cfg se convierte en la referencia viva que los switches descargan durante ZTP o que Lambda aplica en modo restore.
El versionado [Versioning] y lifecycle de S3 permiten rollback, auditoría y trazabilidad sin agregar herramientas adicionales.

>El objetivo detrás de *LifeCycle* es reducir costos al guardar archivos luego de cierto tiempo. Ya que los costos de almacenaje en las categorías Glacier de S3 son menores debido a su retraso en la recuperacion (Retrieval).

#### 6. Monitoría
El ecosistema se completa con una capa de monitoreo, enfocada en la trazabilidad, alertas tempranas y visibilidad operativa.

##### Componentes
Al tener toda la infraestructura en Cloud, es posible apalancarse completamente en las herramientas nativas que ofrece este entorno:

- CloudWatch Logs & Metrics: Recopilan tiempos de ejecución, resultados y errores.
- CloudWatch Alarms + SNS: Notificación automáticamente ante fallos, latencias o anomalias. Pueden utilizarse las alarmas Cloud-native o crear *custom alarms*.
- Dashboard de estado: Con Quicksight, puede automatizarse la creación de reportería visual.

> NOTA: Quicksight puede potenciarse integrándoselo con Amazon Q, un motor de Inteligencia Artificial desarrollado por AWS, para ofrecer visualizaciones inteligentes y análisis asistido por IA sobre los datos operativos de la red.

🌐 Monitoreo de Conectividad (Ping Keep-Alive)

La solución de monitoría de red se apoya en una instancia EC2 dedicada dentro de un Auto Scaling Group (ASG) con capacidad fija de un nodo (Min=Desired=Max=1), encargada de realizar comprobaciones ICMP continuas hacia las interfaces de gestión (VLAN 100) de los switches (Cuyas IP conoce gracias al reporte en S3)

🧩 Arquitectura
- [Diagrama de flujo](./ping.md)
- [Script](./pingscript.py)

> Se descartó el uso de AWS Lambda para el servicio de PING, ya que requiere ejecución continua. Lambda impone un límite de 15 min por invocación y un costo por llamada, por lo que se implementó en una EC2 dedicada integrada con CloudWatch y Auto Scaling para asegurar disponibilidad constante.

## Conclusión General

La solución propuesta integra de forma modular todos los componentes necesarios para una gestión moderna y automatizada de infraestructura de red, combinando Zero Touch Provisioning (ZTP), backups automáticos, restauración controlada, CI/CD, y monitoría inteligente — todo dentro del ecosistema AWS.
