### Alcance

Estas plantillas constituyen la base mínima funcional para la etapa de ZTP y provisión inicial.
A medida que se completen las fases siguientes, podrán extenderse con:

- VLANs adicionales (servicios específicos, invitados, IoT).
- Políticas de seguridad (ACLs, SNMP, Syslog, NTP).
- Automatizaciones CI/CD o validaciones automáticas post-provisión.

### Sintaxis

Las variables aparecen con la forma {{ VARIABLE }} y utilizan la sintaxis Jinja2.

> Este formato permite reemplazar valores dinámicamente desde inventarios o scripts, sin modificar el template base.

### Supuestos de diseño

✅ Se asume la existencia de dos VLAN principales:

- VLAN 100 → Gestión / Staging (DHCP + ZTP + Controller (Si aplica. Ej, Access Points)).
- VLAN 200 → Servicios / Internet / etc.

✅ Todos los puertos de los switches de acceso —tanto hacia Access Points como hacia el uplink— operan en modo trunk, permitiendo el paso de las "n" VLANs.

✅ Desde el inicio, todo Uplink se configurará siempre en formato EtherChannel (Port-channel1) en modo trunk.

>Su implementación física puede comenzar con un único puerto y escalar posteriormente sin impacto sobre la configuración base.

✅ Los Access Points reciben dirección IP en VLAN 100 y se gestionan desde una controladora central.

✅ No se implementa DHCP Relay ni ruteo en los switches de acceso: el objetivo es mantener la red simple, dejando la lógica de control al firewall y a la controladora.

### Equipamiento:
Los archivos de configuración en esta carpeta están diseñados como plantillas paramétricas, facilitando su reutilización en caso de cambios:

- [Access Points](./access_points.md)
- [Switch de acceso](./switches)
- [Firewall](./firewall.md)

