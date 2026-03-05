# Alcance de la entrega

Dado que el comportamiento principal de los APs se gestiona desde la controladora, este proyecto se centra en garantizar el proceso de descubrimiento automático (ZTP) y la conectividad de capa 2/3, sin desarrollar configuraciones de SSID, autenticación o políticas WLAN.

Los Access Points forman la capa más externa de la infraestructura, encargados de brindar conectividad inalámbrica dentro del nuevo sector operativo.
En este diseño, se adopta un enfoque agnóstico de fabricante, aunque se toma como referencia el modelo de trabajo de Ruckus, por ser una solución compatible con provisión automática mediante controladora.

Enfoque adoptado

Los APs se gestionan a través de una controladora central responsable de su registro, firmware, configuración y políticas WLAN.
Por esta razón, el alcance de este proyecto se limita a la infraestructura de red necesaria para su descubrimiento y registro automático, sin profundizar en la configuración interna del backend WLAN.

Flujo operativo ejemplo para este supuesto:

1. El AP se energiza a través del switch de acceso (PoE).
2. Solicita dirección IP mediante DHCP dentro de la VLAN 100 (staging).
3. El servidor DHCP detecta el tipo de cliente y entrega parámetros según corresponda:
    1. Option 60 (Vendor Class Identifier): Enviada automáticamente por el AP Ruckus, permite al servidor identificarlo como dispositivo del fabricante.
    2. Option 43 (Vendor Specific Info): Enviada por el servidor DHCP solo a clientes que se identifican como Ruckus, informando la dirección IP o FQDN de la controladora.
    3. El AP contacta a la controladora, se registra y descarga su configuración.
    > Parámetros estándar: IP, gateway, DNS, etc.
