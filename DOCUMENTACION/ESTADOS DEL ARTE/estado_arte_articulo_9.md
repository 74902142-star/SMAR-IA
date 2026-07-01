# Estado del Arte - Artículo 9: HyPASS - Hybrid-SDN Prevention of Source Spoofing Attacks

**Autor(es):** Ramesh Chand Meena, Surbhi Bhatia, Rutvij H. Jhaveri, Long Cheng, Ankit Kumar, Arwa Mashat  
**Título:** HyPASS: Design of hybrid-SDN prevention of attacks of source spoofing with host discovery and address validation  
**Journal:** Physical Communication  
**Volumen (issue):** Volume 55  
**Año:** 2022  
**Artículo:** 101902  

---

## Estado del Arte

En la introducción y la sección de trabajos relacionados, los autores contextualizan el problema de los ataques de suplantación de dirección de origen (source spoofing) en redes definidas por software (SDN). Explican que SDN separa el plano de control del plano de datos, ofreciendo flexibilidad y facilidad de gestión, pero que esta arquitectura centralizada introduce nuevas vulnerabilidades. En el proceso de funcionamiento de SDN, cuando un switch OpenFlow recibe un paquete que no coincide con ninguna entrada de flujo en su tabla, genera un evento packet_in y envía el paquete al controlador para su procesamiento. Este proceso consume CPU y recursos limitados del switch y del controlador, así como ancho de banda, creando un cuello de botella y una posible puerta de entrada para ataques DoS/DDoS.

Los autores revisan exhaustivamente los trabajos existentes sobre validación de dirección de origen (Source Address Validation - SAV) en SDN. Mencionan que tradicionalmente se utilizan ACLs (Access Control Lists) para filtrar ataques de IP spoofing, pero que las ACLs son complejas y pueden entrar en conflicto con medidas de seguridad activas y políticas de red.

Los autores revisan varias soluciones propuestas en la literatura:

1. **SAWSH (IP Source Address Validation for SDN Hybrid Networks)**: Los autores señalan que la conversión de topología de SAWSH estaba restringida a enlaces entre dispositivos de reenvío, y que la información de hosts conectados no formaba parte del árbol de sumidero (sink tree), por lo que los cambios en los estados de los hosts no se reflejaban. Además, utilizaban prefijos IP en reglas de filtrado, lo que permitía a los atacantes realizar ataques de IP spoofing utilizando otras IPs de la misma red.

2. **ISASA (Integrated Source Address Spoofing Prevention Architecture for SDN)**: Esta solución también se basa en el uso de OpenFlow, pero los autores no detallan sus limitaciones específicas.

3. **PacketChecker y DosDefender**: Estos sistemas utilizan mensajes packet_in para obtener detalles del host (IP y MAC) y filtrar paquetes con direcciones spoofeadas a nivel de puerto del switch. Sin embargo, dependen de que el host comience a enviar paquetes para detectar su presencia, lo que no es proactivo.

4. **INSPECTOR**: Utiliza un dispositivo único para identificar paquetes sospechosos y filtrarlos, también basado en mensajes packet_in.

5. **SDNSAVI**: Este enfoque reenvía mensajes de asignación de direcciones (AAM) al controlador y configura entradas de flujo en la tabla del switch. Utiliza el puerto del switch y la dirección IP del host para el enlace y filtrado de paquetes. Los autores critican que un atacante podría utilizar paquetes AAM para engañar a la tabla de enlace. Además, SDNSAVI solo utiliza el puerto del switch y la IP del host, sin considerar la MAC, lo que proporciona un nivel de precisión más bajo. Los autores argumentan que la identidad completa del host incluye tanto la MAC como la IP, y que el enlace entre el puerto del switch y ambas direcciones proporciona una mejor filtración.

6. **SIPAVSDN**: Esta técnica verifica la validez de la dirección de origen de los paquetes y reenvía solo los paquetes con direcciones legítimas. Utiliza paquetes ARP para identificar la información del host y configura entradas de flujo basadas en el enlace entre el puerto del switch, la IP y la MAC del host. Los autores critican que, al utilizar paquetes ARP para extraer los detalles del host, un atacante puede generar paquetes ARP con direcciones spoofeadas para manipular el comportamiento de la técnica y realizar diversos ataques de IP spoofing.

Los autores identifican varios desafíos no resueltos:
1. La necesidad de un descubrimiento proactivo de hosts conectados.
2. La identificación automática de paquetes con direcciones spoofeadas.
3. La prevención en tiempo real de ataques de suplantación de dirección.
4. La necesidad de almacenar en el controlador una tabla HostLink que contenga la MAC del host, el ID del switch SDN y el ID del puerto.

También señalan que la mayoría de los enfoques no cargan entradas de flujo esenciales en la tabla de flujo del switch OpenFlow antes de que el host comience a generar paquetes de datos reales.

---

## Motivación del Autor (Críticas a Otros Trabajos)

Los autores realizan una crítica fundamentada a los trabajos previos, señalando sus limitaciones y justificando la necesidad de su propuesta:

- **Falta de descubrimiento proactivo**: La mayoría de las soluciones existentes no proporcionan un descubrimiento proactivo de hosts conectados. La mayoría de los enfoques dependen de que el host comience a enviar paquetes (usando packet_in o ARP) para detectar su presencia, lo que crea un retraso y permite que los ataques se inicien antes de que se establezcan las defensas.

- **Limitaciones de SAWSH**: La topología se limita a enlaces entre dispositivos de reenvío, excluyendo la información de los hosts conectados. Además, los cambios en los estados de los hosts no se reflejan en el árbol de sumidero, lo que puede llevar a una detección incorrecta. El uso de prefijos IP en reglas de filtrado permite a los atacantes realizar ataques de IP spoofing utilizando otras IPs de la misma red.

- **Limitaciones de SDNSAVI**: Un atacante puede utilizar paquetes AAM para engañar a la tabla de enlace. El sistema solo utiliza el puerto del switch y la IP del host para el enlace, sin considerar la MAC, lo que proporciona un nivel de precisión más bajo. La identidad completa del host (MAC + IP) debe ser verificada para una validación robusta.

- **Limitaciones de SIPAVSDN**: El uso de paquetes ARP para extraer detalles del host es vulnerable, ya que un atacante puede generar paquetes ARP con direcciones spoofeadas para manipular el comportamiento del sistema y realizar diversos ataques de IP spoofing.

Los autores justifican su trabajo en la necesidad de superar estos vacíos: proponen HyPASS, un sistema que combina el descubrimiento proactivo de hosts (utilizando mensajes SARP en lugar de ARP), la validación de direcciones (MAC + IP) y la prevención en tiempo real de ataques de suplantación de dirección. Además, HyPASS carga entradas de flujo esenciales en el switch antes de que el host comience a generar paquetes de datos, lo que reduce el retraso y mejora la seguridad.

---

## Descripción del Aporte

El aporte principal de los autores es **HyPASS (Hybrid-SDN Prevention of Source Spoofing Attacks with Host Discovery and Address Validation)**, un sistema diseñado para prevenir ataques de suplantación de dirección de origen en redes SDN híbridas. El problema que abordan es crítico: los ataques de suplantación de dirección de origen (source spoofing) permiten a los atacantes ocultar su identidad y lanzar diversos tipos de ataques, como Denial of Service (DoS), Distributed DoS (DDoS), Man-in-the-Middle (MiM), robo de datos valiosos, propagación de malware, evasión de controles de seguridad, modificación de datos en tránsito y secuestro de sesiones. Estos ataques pueden tener graves consecuencias para las empresas y la sociedad, incluyendo pérdida de datos, interrupción de servicios, daños reputacionales y pérdidas económicas significativas.

### El sistema HyPASS se basa en varios principios clave:

**1. Descubrimiento proactivo de hosts:**
A diferencia de las soluciones existentes que dependen de que los hosts envíen paquetes para ser detectados (enfoque reactivo), HyPASS descubre proactivamente los hosts conectados a la red antes de que comiencen a generar tráfico de datos. Para ello, utiliza mensajes **SARP (Source Address Request Protocol)** que se generan durante el handshaking o cuando cambia el estado de cualquier puerto del switch. Esto permite que el sistema conozca la ubicación exacta de cada host (switch ID y puerto) y sus direcciones MAC e IP antes de que se produzca cualquier ataque.

**2. Tabla HostLink en el controlador:**
El sistema mantiene una tabla HostLink en el controlador que almacena la información de cada host conectado: dirección MAC, dirección IP, ID del switch SDN y ID del puerto. Esta tabla se actualiza dinámicamente a medida que los hosts se conectan o desconectan de la red.

**3. Validación de dirección de origen:**
Cuando se recibe un paquete en un switch OpenFlow, el sistema verifica la dirección de origen del paquete (MAC e IP) comparándola con la información almacenada en la tabla HostLink para el puerto correspondiente. Si la dirección coincide, el paquete se considera legítimo y se reenvía; si no coincide, el paquete se descarta (drop). El sistema utiliza el enlace entre el puerto del switch y la combinación MAC+IP del host para proporcionar una validación más precisa que los sistemas que solo usan IP o MAC por separado.

**4. Configuración proactiva de entradas de flujo:**
HyPASS carga entradas de flujo esenciales en la tabla de flujo del switch OpenFlow antes de que el host comience a generar paquetes de datos reales. Esto reduce el número de mensajes packet_in enviados al controlador, ahorrando recursos de CPU y ancho de banda, y evitando la creación de cuellos de botella que podrían ser explotados por atacantes.

**5. Prevención en tiempo real:**
El sistema identifica y bloquea paquetes con direcciones de origen falsificadas en tiempo real, en el propio switch, sin necesidad de enviar cada paquete al controlador para su análisis. Esto reduce la latencia y mejora la eficiencia del sistema.

**6. Implementación híbrida:**
HyPASS se implementa en SDN híbrido, combinando switches OpenFlow con dispositivos de red tradicionales, lo que permite su despliegue en entornos de red existentes sin necesidad de una migración completa a SDN.

### El sistema HyPASS se compone de varios módulos:
- **Módulo de descubrimiento de hosts**: Genera mensajes SARP para descubrir proactivamente los hosts conectados.
- **Módulo de validación de direcciones**: Verifica la dirección de origen de los paquetes entrantes.
- **Módulo de gestión de la tabla HostLink**: Mantiene y actualiza la tabla HostLink en el controlador.
- **Módulo de configuración de flujos**: Carga entradas de flujo esenciales en los switches.

El impacto en la empresa y la sociedad es significativo: al prevenir ataques de suplantación de dirección, HyPASS protege la integridad y disponibilidad de los servicios de red, evita interrupciones del servicio, protege datos sensibles y reduce el riesgo de pérdidas económicas y daños reputacionales. El sistema es especialmente relevante para empresas que dependen de redes SDN para sus operaciones críticas.

Los autores evalúan HyPASS mediante simulaciones en Mininet con controladores RYU y POX, utilizando cuatro escenarios de red diferentes (con hasta 127 switches y 483 puertos). Los resultados demuestran que HyPASS identifica y descarta el 99.99% de los paquetes con dirección de origen falsificada.

---

## Proceso para Obtener el Aporte

Los autores describen un proceso metodológico estructurado para obtener su aporte, que combina el descubrimiento proactivo de hosts, la validación de direcciones y la configuración proactiva de flujos en SDN híbrido. El proceso se desarrolla en las siguientes etapas:

1. **Identificación de requisitos y limitaciones**: Analizan las soluciones existentes (SAWSH, ISASA, PacketChecker, DosDefender, INSPECTOR, SDNSAVI, SIPAVSDN) e identifican sus limitaciones: dependencia de ARP o packet_in para descubrir hosts, vulnerabilidad a ataques de suplantación de ARP, falta de información completa del host (MAC+IP), y ausencia de configuración proactiva de flujos.

2. **Definición de los objetivos de diseño**: Establecen los objetivos clave de HyPASS: (a) descubrimiento proactivo de hosts conectados; (b) identificación automática de paquetes con direcciones spoofeadas; (c) prevención en tiempo real de ataques de suplantación; (d) almacenamiento de la tabla HostLink en el controlador (MAC, switch ID, puerto ID); (e) carga de entradas de flujo esenciales antes de que el host genere paquetes de datos.

3. **Diseño del protocolo SARP**: Diseñan un nuevo protocolo, **SARP (Source Address Request Protocol)**, para el descubrimiento proactivo de hosts. A diferencia de ARP, que puede ser manipulado por atacantes, SARP se utiliza durante el handshaking o cuando cambia el estado de un puerto del switch. El protocolo SARP consta de mensajes SARP-Request y SARP-Reply. El switch envía un SARP-Request a todos los IPs en el rango de direcciones, y el host responde con un SARP-Reply que contiene su MAC e IP. Esto permite al sistema descubrir hosts sin depender de ARP.

4. **Diseño de la tabla HostLink**: Diseñan la estructura de la tabla HostLink que se almacena en el controlador, que contiene los campos: Host MAC, Host IP, Switch ID, Port ID. Esta tabla se actualiza dinámicamente cuando se descubren nuevos hosts o cuando cambia el estado de un puerto.

5. **Desarrollo de los módulos del sistema**: Implementan los módulos del sistema HyPASS:
   - **Módulo de descubrimiento de hosts**: Gestiona el intercambio de mensajes SARP.
   - **Módulo de validación de direcciones**: Compara la dirección de origen de los paquetes entrantes con la tabla HostLink.
   - **Módulo de gestión de la tabla HostLink**: Mantiene y actualiza la tabla.
   - **Módulo de configuración de flujos**: Genera y carga entradas de flujo en los switches.

6. **Implementación del mecanismo de configuración de flujos**: Diseñan un mecanismo que carga entradas de flujo esenciales en la tabla de flujo del switch OpenFlow antes de que el host comience a generar paquetes de datos. Esto se logra durante el descubrimiento proactivo del host, cuando el sistema instala una entrada de flujo que permite al switch reenviar paquetes del host sin necesidad de enviar mensajes packet_in al controlador.

7. **Integración en SDN híbrido**: El sistema se diseña para funcionar en entornos SDN híbridos, que combinan switches OpenFlow con dispositivos de red tradicionales. Esto permite su despliegue en redes existentes sin necesidad de una migración completa a SDN.

8. **Validación y pruebas**: Implementan HyPASS en Python y lo prueban en el emulador Mininet con los controladores RYU y POX. Utilizan cuatro escenarios de red diferentes con topologías variables (hasta 127 switches y 483 puertos) para evaluar el rendimiento del sistema.

---

## Proceso para Resolver el Problema

Los autores realizan una evaluación exhaustiva de HyPASS para resolver el problema de la prevención de ataques de suplantación de dirección de origen en SDN. El proceso de validación incluye los siguientes pasos:

1. **Configuración experimental**: Utilizan el emulador Mininet para crear cuatro escenarios de red diferentes:
   - Escenario 1: 121 switches, 483 puertos
   - Escenario 2: 127 switches, 380 puertos
   - Escenario 3: 31 switches, 185 puertos
   - Escenario 4: 10 switches, 48 puertos

   Utilizan dos controladores diferentes: RYU y POX. La implementación se realiza en Python. Los switches son OpenFlow compatibles.

2. **Implementación de HyPASS en el controlador**: Implementan HyPASS como un módulo en el controlador RYU y POX. El módulo incluye las funciones de descubrimiento de hosts (SARP), gestión de la tabla HostLink, validación de direcciones y configuración de flujos.

3. **Configuración de hosts y generación de tráfico**: Los hosts se configuran con direcciones IP y MAC. Se genera tráfico legítimo entre hosts para verificar el funcionamiento normal del sistema. También se generan paquetes maliciosos con direcciones de origen falsificadas (spoofed) para evaluar la capacidad de detección del sistema.

4. **Prueba del descubrimiento proactivo de hosts**: Verifican que HyPASS descubre proactivamente los hosts conectados mediante mensajes SARP durante el handshaking o cuando cambia el estado de los puertos. Se confirma que la tabla HostLink se actualiza correctamente con la información de cada host.

5. **Prueba de validación de direcciones**: Envían paquetes desde hosts legítimos y desde hosts atacantes con direcciones spoofeadas. Se verifica que HyPASS:
   - Permite el paso de paquetes con direcciones de origen que coinciden con la tabla HostLink (legítimos).
   - Descarta (drop) paquetes con direcciones de origen que no coinciden con la tabla HostLink (spoofeados).
   - Mide la tasa de detección y el porcentaje de paquetes descartados.

6. **Prueba de configuración proactiva de flujos**: Verifican que HyPASS carga entradas de flujo esenciales en la tabla de flujo del switch antes de que los hosts comiencen a generar paquetes de datos. Se confirma que los paquetes legítimos se reenvían sin necesidad de generar mensajes packet_in al controlador, lo que reduce la sobrecarga en el controlador y los switches.

7. **Medición de métricas de rendimiento**: Durante los experimentos, registran varias métricas:
   - **Tasa de detección**: Proporción de paquetes spoofeados correctamente identificados y descartados.
   - **Tasa de falsos positivos**: Proporción de paquetes legítimos incorrectamente descartados (esperado: 0%).
   - **Sobrecarga en el controlador**: Número de mensajes packet_in generados.
   - **Tiempo de procesamiento**: Tiempo requerido para validar y reenviar paquetes.

8. **Comparación con soluciones existentes**: Comparan el rendimiento de HyPASS con soluciones existentes como SAWSH, SDNSAVI y SIPAVSDN en términos de tasa de detección, falsos positivos y sobrecarga.

9. **Resultados obtenidos**: Los resultados demuestran que HyPASS:
   - Identifica y descarta el **99.99%** de los paquetes con dirección de origen falsificada.
   - No produce falsos positivos (los paquetes legítimos siempre se reenvían correctamente).
   - Reduce significativamente la sobrecarga en el controlador al cargar entradas de flujo de manera proactiva.
   - Funciona eficazmente en todos los escenarios de red probados.

10. **Análisis de limitaciones**: Discuten las limitaciones del sistema, como la generación de un gran número de mensajes SARP en redes grandes, y proponen optimizaciones (como verificar la IP de destino de SARP-Request con la tabla HostLink para evitar mensajes innecesarios).

---

## Métricas y Resultados

Los autores utilizan métricas clave para evaluar HyPASS: tasa de detección (proporción de paquetes spoofeados identificados y descartados), tasa de falsos positivos (paquetes legítimos incorrectamente descartados), y sobrecarga en el controlador (número de mensajes packet_in generados).

### Resultados obtenidos:

| Métrica | Resultado |
|---|---|
| Tasa de detección | 99.99% de paquetes con dirección de origen falsificada identificados y descartados |
| Tasa de falsos positivos | 0% (ningún paquete legítimo fue descartado incorrectamente) |
| Reducción de sobrecarga | La configuración proactiva de flujos reduce significativamente el número de mensajes packet_in enviados al controlador |

### Comparación con soluciones existentes:

- **SAWSH y ISASA**: Tienen tasas de detección más bajas y pueden ser vulnerables a ataques de IP spoofing utilizando IPs de la misma red.
- **SDNSAVI**: Tiene una tasa de detección menor debido a que solo utiliza IP y puerto para el enlace, sin considerar la MAC, y es vulnerable a ataques de envenenamiento de AAM.
- **SIPAVSDN**: Tiene una tasa de detección menor debido a su dependencia de ARP, que puede ser manipulado por atacantes.

**Comentario sobre las métricas y el enfoque:** Considero que las métricas elegidas son adecuadas y cubren los aspectos clave de un sistema de prevención de suplantación de dirección: efectividad en la detección (tasa de detección del 99.99%), precisión (0% de falsos positivos) y eficiencia (reducción de la sobrecarga). La tasa de detección del 99.99% es excepcionalmente alta y supera a la mayoría de las soluciones reportadas en la literatura.

El enfoque de HyPASS es particularmente acertado por varias razones:
1. El descubrimiento proactivo de hosts mediante SARP (en lugar de ARP) elimina la vulnerabilidad a ataques de suplantación de ARP.
2. La validación basada en el enlace entre el puerto del switch y la combinación MAC+IP del host proporciona una precisión mucho mayor que los sistemas que solo utilizan IP o MAC por separado.
3. La configuración proactiva de flujos reduce la sobrecarga en el controlador y los switches, evitando la creación de cuellos de botella que podrían ser explotados por atacantes para lanzar ataques DoS/DDoS.

Sin embargo, hay aspectos que podrían mejorarse:
1. La generación de mensajes SARP para cada IP en el rango de direcciones durante el handshaking podría generar una sobrecarga significativa en redes grandes con miles de hosts. Los autores proponen optimizaciones (verificar la IP de destino con la tabla HostLink), pero no proporcionan mediciones detalladas del impacto de esta optimización.
2. El sistema se evalúa en un entorno simulado (Mininet) y no en un testbed real, lo que podría ocultar problemas de rendimiento en condiciones de red reales.
3. Aunque el sistema protege contra ataques de suplantación de dirección, no aborda otros tipos de ataques como DDoS o ataques basados en contenido.
4. La escalabilidad del sistema en redes muy grandes (más de 1000 switches) no se evalúa directamente, aunque los escenarios probados (hasta 127 switches) son razonablemente grandes.

---

## Observaciones Críticas

El artículo presenta un enfoque innovador y bien fundamentado para la prevención de ataques de suplantación de dirección de origen en SDN. A continuación, realizo algunas observaciones y críticas constructivas:

1. **Validación en entornos reales**: Aunque los autores utilizan Mininet para la simulación, que es ampliamente aceptado en la investigación, la evaluación en un testbed real con hardware de switches SDN y tráfico de red realista sería un valor añadido significativo para validar la eficacia de HyPASS en condiciones reales.

2. **Sobrecarga de mensajes SARP**: En redes grandes con muchos hosts, la generación de mensajes SARP para cada IP en el rango de direcciones podría generar una sobrecarga significativa durante el handshaking. Aunque los autores mencionan la optimización de verificar la IP de destino con la tabla HostLink, no proporcionan mediciones detalladas del impacto de esta optimización en el tráfico de red.

3. **Seguridad del protocolo SARP**: El artículo no aborda en profundidad la seguridad del propio protocolo SARP. ¿Qué impide que un atacante envíe mensajes SARP-Reply falsos para engañar a la tabla HostLink? Aunque SARP es menos vulnerable que ARP (que se utiliza en SIPAVSDN), sigue siendo susceptible a ataques de suplantación si no se implementan mecanismos de autenticación.

4. **Escalabilidad**: Aunque el sistema se prueba en escenarios con hasta 127 switches, no se evalúa su rendimiento en redes con miles de switches o con una alta tasa de cambios en la topología (hosts que se mueven frecuentemente). La gestión de la tabla HostLink podría convertirse en un cuello de botella en redes muy dinámicas.

5. **Integración con otros mecanismos de seguridad**: HyPASS se centra exclusivamente en la prevención de suplantación de dirección. No aborda otros tipos de ataques como DDoS, ataques de capa de aplicación o ataques basados en contenido. Sería interesante explorar cómo HyPASS podría integrarse con otros mecanismos de seguridad (como sistemas de detección de intrusos, firewalls, etc.) para proporcionar una defensa en profundidad.

6. **Mitigación de ataques DoS**: El sistema podría ser vulnerable a ataques DoS si un atacante envía un gran número de paquetes con direcciones spoofeadas que no coinciden con la tabla HostLink. Aunque estos paquetes se descartan en el switch, el switch aún tiene que procesarlos (verificar la dirección y descartarlos), lo que podría consumir recursos y degradar el rendimiento.

7. **Soporte para IPv6**: El artículo se centra en IPv4 (utilizando direcciones IP de 32 bits). No se menciona el soporte para IPv6, que es cada vez más relevante en redes modernas. Sería interesante explorar cómo se adapta HyPASS a direcciones IPv6 y si las direcciones más largas afectan al rendimiento del sistema.

8. **Tiempo de convergencia**: Cuando un host se desconecta o se mueve a otro puerto, ¿cuánto tiempo tarda el sistema en actualizar la tabla HostLink y eliminar las entradas de flujo obsoletas? Un tiempo de convergencia lento podría permitir que un atacante explote la ventana de tiempo entre la desconexión legítima y la actualización de la tabla.

9. **Comparación cuantitativa con otras soluciones**: Aunque los autores mencionan trabajos previos, no proporcionan una comparación cuantitativa detallada en términos de tiempo de detección, sobrecarga de CPU, o consumo de memoria. Una comparación más exhaustiva fortalecería las conclusiones.

10. **Disponibilidad del código**: No se menciona si el código fuente de HyPASS está disponible públicamente. La disponibilidad del código facilitaría la replicabilidad y extensión del estudio por parte de otros investigadores.

---

## Relevancia para el Proyecto

HyPASS es especialmente relevante para nuestro proyecto porque aborda la **prevención de ataques de suplantación de dirección de origen (source spoofing)** en SDN, un vector de ataque crítico que puede ser un precursor de ataques DDoS y MITM. Los aspectos clave aplicables a nuestro sistema SDN-ML son:

1. **Descubrimiento proactivo de hosts**: El protocolo SARP permite conocer la ubicación y dirección de los hosts antes de que generen tráfico, eliminando la ventana de vulnerabilidad que existe en enfoques reactivos.

2. **Validación de dirección (MAC + IP)**: La verificación de ambas direcciones proporciona una precisión mucho mayor que los sistemas que solo usan IP o MAC por separado, reduciendo los falsos positivos.

3. **Configuración proactiva de flujos**: Cargar entradas de flujo antes de que el host genere tráfico reduce la sobrecarga en el controlador y previene ataques DoS basados en packet_in.

4. **Implementación híbrida**: La compatibilidad con entornos SDN híbridos facilita el despliegue en redes existentes.

5. **Alta tasa de detección**: El 99.99% de detección y 0% de falsos positivos son resultados excepcionales que demuestran la efectividad del enfoque.

HyPASS puede integrarse como una capa de prevención de spoofing en nuestro sistema, complementando los mecanismos de detección de DDoS basados en ML y proporcionando una defensa en profundidad.

---

**Referencia:**  
Meena, R. C., Bhatia, S., Jhaveri, R. H., Cheng, L., Kumar, A., & Mashat, A. (2022). HyPASS: Design of hybrid-SDN prevention of attacks of source spoofing with host discovery and address validation. *Physical Communication*, 55, 101902.