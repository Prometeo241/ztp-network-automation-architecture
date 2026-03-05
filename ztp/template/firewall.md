## NOTA: Dado que los uplink de los switches contra el firewall serán en modo PortChannel desde t0, todas las bocas de servicio del firewall deberán configurarse en dicho modo y de a pares. Así, se garantiza que sin importar dónde se conecte el switch "n", mientras sea conectado a un *puerto par* del firewall, el port-channel levantará automáticamente y las VLAN permitidas cursarán tráfico.

En este proyecto se documenta el comportamiento esperado del equipo Firewall y su diseño conceptual, no incluye configuraciones de CLI ni comandos específicos, el fin es explicar la lógica de separación y control que se realizará sobre el tráfico.

El objetivo principal es asegurar el flujo necesario para la provisión automática (ZTP) y la comunicación entre dispositivos gestionados y la controladora.
Para la presente propuesta de ZTP (Zero Touch Provisioning) el equipo firewall debe estar previamente configurado en laboratorio.


### Segmentación lógica

| VRF          | Desscripción                                                    | VLAN asociada |
| ------------ | --------------------------------------------------------------- | ------------- |
| MGMT     | Tráfico de gestión y ZTP (Switches, APs, controladora, backups) | VLAN 100  |
| SERVICIO | Tráfico de usuarios y servicios internos / salida a Internet / etc   | VLAN 200  |


| Servicio                                 | Descripción                                                                                                                                       
| --------------------------------------- | -------------------------------------------------------------------------------------------- | 
| DHCP Relay – VLAN 100               | Reenvío de solicitudes DHCP de equipos en la VLAN de gestión hacia el servidor alojado en la nube.         
| Salida a Internet – VLAN 200  | Enrutar tráfico de usuarios o servicios interno . 
| DHCP Snooping (opcional) | Proteccion contra ataque de IP Spoofing.|
| Limitación de MAC (opcional)        | Controla la cantidad de MAC aprendidas por puerto para evitar ataque de IP Starvation.                                          


### Interacción con el entorno ZTP

El firewall debe permitir tráfico DHCP, DNS y HTTP desde la VLAN 100 hacia el servidor de aprovisionamiento y la controladora de los Access Point.

La VLAN 200 se reserva para servicios o conectividad Internet, pero no se utiliza directamente durante la fase de staging/aprovisionamiento [ZTE].

La comunicación de control (Por ej: SSH) también se canaliza a través de la VLAN 100.
