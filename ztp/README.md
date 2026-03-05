# Zero Touch Provisioning (ZTP)

Este módulo define el diseño y automatización del proceso de aprovisionamiento inicial de la infraestructura de red (Switches, access points y firewalls).

---
## Arquitectura propuesta

![Diagrama sin título](https://github.com/user-attachments/assets/6322da48-efd3-496c-b8d7-1ec826791018)

---

## ⚙️ Componentes principales
- **DHCP**: Asignación de IP y entrega de Options 60/66.
- **Bootstrap**: Archivo inicial indicando como debe venir el equipo pre-configurado de fábrica.
- **Templates**: Archivos finales que serán descargados por los equipos.

---

##  Premisas de diseño
- La **VLAN 100 (staging)** es el segmento de aprovisionamiento inicial.  
- El **firewall on-premise** actúa como **DHCP Relay** y salida a la VPN Site-to-Site con AWS.  
- **Route 53** se implementa como capa lógica de resolución interna para:
  - Mantener **flexibilidad** ante cambios de backend.  
  - Evitar **dependencias estáticas de IPs**.  

> Es decir, el tráfico podría operar directamente por IP, pero se adopta **DNS interno (Route 53 Private Zone)** para lograr un diseño más escalable y **desacoplado**.

---

### 📑 Filosofía de diseño

Se decidió mantener separados los archivos de **bootstrap** y **template** para lograr un mayor desacoplamiento funcional entre las fases de aprovisionamiento.

- **Bootstrap:** garantiza conectividad mínima mediante la pre-carga de la VLAN de gestión y el requerimietno de IP vía DHCP.
- **Template:** contiene la configuración final a aplicar una vez establecida la comunicación.
  
---

## Flujo de trabajo
1. El dispositivo enciende y solicita IP vía DHCP ya que hará match su VLAN 100 pre configurada con la del Firewall.  
2. El dispotivio hará DHCP Relay enviando el paquete, *ahora unicast* a la infraestructura cloud [ztp.test.net]
3. El Load Balancer distribuirá aleatoriamente el paquete a alguna de las dos instancias disponibles. Dado que Minimo = Deseado = Maximo = 2.
4. El servidor DHCP, identifico al solicitante (Host) vía la Opcton 60, devuelve la Option 66 con la URL del objeto especifico en el repositorio S3.  
5. El equipo solicitante recibe el paquete, se configura IP, DNS, resuelve el URL y descarga el FTP.  
6. Ejecuta y configura el .cfg descargado.  
7. La acción GETObject en el S3 dispara una alarma de evento que luego es canalizada mediante el servicio Simple Notification Service [SNS] y la retransmite mediante Slack o email segun se desee.

---
## Submódulos
- [Templates](./template/README.md)
