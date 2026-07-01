# Estado del Arte - Artículo 7: Packet Injection Exploiting Attack and Mitigation in SDN (PIEDefender)

**Autor(es):** Jishuai Li, Sujuan Qin, Tengfei Tu, Hua Zhang, Yongsheng Li  
**Título:** Packet Injection Exploiting Attack and Mitigation in Software-Defined Networks  
**Journal:** Applied Sciences (MDPI)  
**Volumen (issue):** Volume 12, Issue 3  
**Año:** 2022  
**Artículo:** 1103  

---

## Estado del Arte

En la introducción y la sección de trabajos relacionados, los autores contextualizan el problema de la seguridad en redes definidas por software (SDN). Explican que SDN ha surgido como un paradigma revolucionario que separa el plano de control del plano de datos, reemplazando el plano de control clásico basado en sistemas embebidos por un plano de control abierto y programable. Gracias a esta apertura y programabilidad, SDN se ha aplicado a diversos campos, como redes empresariales y centros de datos. Sin embargo, la separación lógica entre el control y la función de reenvío expande la superficie de ataque, y los planos de control, datos y aplicaciones enfrentan desafíos de seguridad.

Los autores revisan exhaustivamente los trabajos existentes sobre seguridad en SDN, clasificándolos en diferentes categorías según el tipo de ataque abordado:

**Seguridad de topología en SDN:** Los autores citan TopoGuard (Hong et al., 2015), que puede descubrir automáticamente ataques de envenenamiento de topología en tiempo real, aunque ignoró el origen de los mensajes Packet-In en el manejo del ataque de secuestro de ubicación de host. Mencionan Hauth (Xin et al., 2016), que propuso resolver el ataque de usurpación de host implementando confirmación para hosts legítimos mediante un servidor de autenticación, aunque requiere medidas adicionales para asegurar que el servidor no se dañe. También citan SECUREBINDER (Jero et al., 2017), que previene problemas de vinculación de identificadores, aunque el objetivo debe usar DHCP para que sea aplicable. CTAD (Chou et al., 2019) detecta diferentes tipos de ataques de topología analizando la relevancia del tráfico de red y verificando tramas LLDP. TrustTopo (Huang et al., 2020) es un esquema de verificación de topología SDN ligero y eficiente que maneja el secuestro de hosts y ataques de fabricación de enlaces, aunque no considera las amenazas en la etapa de inicio de la red.

**Ataques de saturación de recursos:** SA-Detector (Li et al., 2019) calcula la autosimilitud del tráfico regular y anormal y analiza la diferencia contra ataques de saturación, aunque no considera el origen del ataque. SDNGuardian (Xu et al., 2020) describe un ataque de saturación mejorado y propone un marco de defensa eficiente. vSwitchGuard (Khamaiseh et al., 2020) identifica switches comprometidos mediante clasificadores de machine learning, aunque solo estudia cinco ataques de saturación.

**Seguridad de la tabla de flujo:** FTGuard (Zhang et al., 2017) implementa una estrategia de defensa prioritaria basada en comportamiento para hacer frente al ataque de desbordamiento de tabla de flujo. WedgeTail (Shaghaghi et al., 2017) distingue dispositivos de reenvío maliciosos mediante el cálculo de trayectorias esperadas y reales de paquetes. Siyi et al. (2018) propusieron un mecanismo de compartición de tabla de flujo que mitiga eficazmente el daño causado por ataques de sobrecarga de tabla de flujo.

**Ataques DoS en SDN:** Abhiroop et al. (2018) propusieron un enfoque de machine learning para detectar ataques DoS en switches SDN usando información de tabla de flujo y tráfico OpenFlow. Carvalho et al. (2019) construyeron un mecanismo que monitorea la red y puede diferenciar tráfico DoS de tráfico benigno usando entropía. De Assis et al. (2018) y Arivudainambi et al. (2019) utilizaron redes neuronales para detectar ataques DoS. SDN-Guard (Dridi et al., 2016) y FloodDefender (Shang et al., 2017) mitigan ataques DoS en SDN mediante la gestión dinámica de reglas de flujo. DoSDefender (Deng et al., 2019) defiende contra ataques DoS mediante el mantenimiento de la relación de mapeo entre switches y hosts asociados, aunque usa un enfoque basado en umbrales que puede llevar a falsos positivos.

**Ataques de inyección de paquetes:** Los autores mencionan que Deng et al. (2017) propusieron por primera vez el ataque de inyección de paquetes, señalando que los atacantes pueden inyectar nodos falsos en SDN manipulando paquetes maliciosamente. También citan INSPECTOR (Alshra'A y Seitz, 2019), que utiliza un dispositivo único para identificar paquetes sospechosos.

Los autores identifican que los trabajos existentes abordan diversos aspectos de la seguridad SDN, pero que aún se necesitan descubrir y estudiar nuevos métodos de ataque y estrategias de defensa. Su propuesta se basa en continuar la investigación sobre el ataque de inyección de paquetes, explorando cómo los atacantes pueden explotar aún más estos hosts inexistentes para lanzar ataques DoS.

---

## Motivación del Autor (Críticas a Otros Trabajos)

Los autores realizan una crítica fundamentada a los trabajos previos, señalando sus limitaciones y justificando la necesidad de su propuesta:

- **Explotación del ataque de inyección**: Aunque Deng et al. (2017) propusieron el ataque de inyección de paquetes, no exploraron cómo los atacantes pueden explotar aún más estos hosts inexistentes para lanzar ataques más destructivos. Los autores argumentan que la respuesta a esta pregunta es positiva: los atacantes pueden usar estos hosts falsos para lanzar ataques DoS.

- **Limitaciones de TopoGuard**: TopoGuard, aunque efectivo para ataques de envenenamiento de topología, ignora el origen de los mensajes Packet-In en el manejo del ataque de secuestro de ubicación de host, lo que limita su efectividad contra ataques de inyección de paquetes.

- **Limitaciones de Hauth y SECUREBINDER**: Hauth requiere medidas adicionales para asegurar que el servidor de autenticación no se dañe, añadiendo complejidad. SECUREBINDER solo es aplicable cuando el objetivo usa DHCP, lo que limita su aplicabilidad en entornos donde no se usa DHCP.

- **Limitaciones de TrustTopo**: TrustTopo no considera las amenazas en la etapa de inicio de la red, lo que deja una ventana de vulnerabilidad.

- **Limitaciones de los enfoques de detección de DoS**: DoSDefender utiliza un enfoque basado en umbrales para detectar ataques que falsifican puertos de origen, lo que puede llevar fácilmente a falsos positivos. SA-Detector no considera el origen del ataque durante un ataque de saturación, limitando su capacidad para identificar y bloquear a los atacantes.

- **Limitaciones de PacketChecker**: PacketChecker asume que la dirección MAC del host en el plano de datos no cambiará. Los autores consideran que esta suposición es demasiado estricta, ya que los hosts pueden cambiar legítimamente su dirección MAC o migrar a otra ubicación.

Los autores justifican su trabajo en la necesidad de superar estos vacíos: proponen PIEDefender, un componente ligero e independiente del protocolo construido sobre controladores SDN que detecta y mitiga eficazmente el ataque de inyección de paquetes y su explotación para ataques DoS. PIEDefender verifica la consistencia de la información de los mensajes Packet-In y OFPT_PORT_STATUS, y utiliza un clasificador SVM con características de mensajes OpenFlow y flujos para detectar ataques DoS basados en hosts inyectados.

---

## Descripción del Aporte

El aporte principal de los autores es el **ataque de inyección de paquetes explotador (packet injection exploiting attack)** y su sistema de defensa **PIEDefender (Packet Injection Exploiting Attack Defender)**. El problema que abordan es crítico: los atacantes pueden inyectar hosts falsos en la topología de red SDN mediante la manipulación de paquetes con direcciones MAC de origen falsificadas, y luego explotar estos hosts inexistentes para lanzar ataques DoS que afectan al controlador, los switches y el ancho de banda del canal seguro.

### El ataque propuesto se desarrolla en dos fases:

**Fase 1: Inyección de hosts falsos:** El atacante envía una gran cantidad de paquetes con direcciones MAC de origen falsificadas a la red SDN. Cuando el switch recibe un paquete desconocido sin una regla de flujo correspondiente, encapsula el paquete en un mensaje Packet-In y lo envía al controlador. El controlador, al recibir el mensaje, recupera el archivo Host Profile. Como el atacante ha falsificado la dirección MAC de origen, el servicio de seguimiento de hosts asume que un nuevo host se ha unido a la red, añadiendo un host falso a la topología SDN.

**Fase 2: Ataque DoS basado en hosts inyectados:** Después de inyectar muchos hosts falsos, el atacante construye paquetes específicos con la dirección MAC de destino apuntando a cualquiera de los hosts inyectados, y genera aleatoriamente la dirección IP de destino y el número de puerto. Como los hosts falsos han sido añadidos a la topología SDN, el controlador no elimina estos paquetes desconocidos. El controlador calcula la estrategia de reenvío de paquetes desconocidos e instala reglas de tabla de flujo en el switch. Si el atacante envía frecuentemente paquetes desconocidos, esto sobrecarga la capacidad de procesamiento del controlador y la tabla de flujo de los switches, y consume un ancho de banda excesivo de la interfaz southbound, afectando a toda la red.

### El sistema PIEDefender se sitúa entre la plataforma del controlador y otras aplicaciones del controlador, e incluye tres módulos funcionales:

**1. Módulo de detección de inyección (Injection Detection):** Este módulo construye y mantiene la tabla de mapeo MT entre switches y hosts conectados. Cada entrada en MT está compuesta por maci, dpidj y portij. El módulo verifica los mensajes Packet-In de la siguiente manera:
- **Caso 1:** No hay entrada en MT. Se considera un nuevo host y se crea una nueva entrada.
- **Caso 2:** Hay entrada en MT y maci ≡ mac. El mensaje es legal.
- **Caso 3:** Hay entrada en MT pero maci ≠ mac. Se considera un ataque de inyección.

Además, el módulo verifica los mensajes OFPT_PORT_STATUS para gestionar dinámicamente la información de mapeo. Cuando se recibe un mensaje OFPT_PORT_STATUS, se crea una tabla de mapeo temporal MT para almacenar la información del switch y host en mensajes Packet-In posteriores. Si MT contiene solo una entrada de mapeo cuando los mensajes Packet-In alcanzan el umbral establecido (counter = 8), se considera que el mensaje es legal y se actualiza MT. De lo contrario, se considera que el mensaje OFPT_PORT_STATUS es ilegal.

**2. Módulo de detección DoS simplificado (Simplified DoS Detection):** Este módulo utiliza un clasificador SVM con un vector de características de cinco elementos:
- **RPI (Rate of Packet-In messages):** Tasa de mensajes Packet-In.
- **RFM (Rate of Flow-Mod messages):** Tasa de mensajes Flow-Mod.
- **PIRF (Percentage of Irreversible Flows):** Porcentaje de flujos irreversibles (aquellos que no establecen una conexión bidireccional completa).
- **PFSP (Percentage of Flows with Small Packets):** Porcentaje de flujos con paquetes pequeños (1-3 paquetes por flujo).
- **PFSL (Percentage of Flows with Short Lifetime):** Porcentaje de flujos con vida corta.

El clasificador SVM fue entrenado con un dataset de 30,000 tráficos (16,925 normales y 13,075 de ataque) generado en el entorno experimental.

**3. Módulo de gestión de reglas de flujo (Flow Rule Management):** Este módulo recibe notificaciones de los módulos de detección de inyección y detección DoS. Extrae el host comprometido e instala reglas de flujo en el switch conectado para bloquear y eliminar el tráfico malicioso. Las reglas de flujo se construyen sin ninguna acción de salida (drop), por lo que cualquier paquete que coincida con la regla será descartado según la especificación OpenFlow 1.3.

El impacto en la empresa y la sociedad es significativo: los ataques de inyección de paquetes y su explotación para DoS pueden afectar gravemente la disponibilidad y rendimiento de las redes SDN, causando interrupciones del servicio, pérdidas económicas y daños reputacionales. PIEDefender proporciona una defensa eficaz con una sobrecarga limitada (10% de CPU en promedio), protegiendo tanto el plano de control como el plano de datos.

---

## Proceso para Obtener el Aporte

Los autores describen un proceso metodológico estructurado para obtener su aporte, que abarca desde la identificación del ataque hasta el diseño, implementación y evaluación de PIEDefender. El proceso se desarrolla en las siguientes etapas:

1. **Identificación del ataque de inyección de paquetes explotador**: Los autores parten del trabajo previo de Deng et al. (2017) sobre el ataque de inyección de paquetes. Se preguntan si los atacantes pueden explotar aún más estos hosts inexistentes para lanzar ataques más destructivos. La respuesta es positiva, y proponen el ataque de inyección de paquetes explotador.

2. **Verificación de la viabilidad del ataque**: Realizan experimentos en un entorno de software (Mininet con controlador Floodlight) para verificar la viabilidad y efectividad del ataque. Utilizan Scapy para forjar paquetes con direcciones MAC de origen falsificadas e inyectar hosts falsos en la topología. Luego, utilizan estos hosts falsos para lanzar ataques DoS y miden el impacto en el controlador (utilización de CPU) y en los switches (ocupación de la tabla de flujo).

3. **Diseño del sistema PIEDefender**: Diseñan PIEDefender como un componente ligero que se sitúa entre la plataforma del controlador y otras aplicaciones. El sistema consta de tres módulos: detección de inyección, detección DoS simplificada, y gestión de reglas de flujo.

4. **Implementación del módulo de detección de inyección**: Implementan el algoritmo de verificación de mensajes Packet-In y el algoritmo de verificación de mensajes OFPT_PORT_STATUS. El módulo construye y mantiene la tabla de mapeo MT entre switches y hosts conectados. La verificación de OFPT_PORT_STATUS utiliza un umbral (counter = 8) para determinar si el mensaje es legal o malicioso.

5. **Implementación del módulo de detección DoS simplificado**: Implementan el algoritmo de detección de ataques basado en SVM. Seleccionan cinco características (RPI, RFM, PIRF, PFSP, PFSL) que son indicativas de ataques DoS basados en hosts inyectados. Generan un dataset de 30,000 tráficos (16,925 normales y 13,075 de ataque) para entrenar el clasificador SVM.

6. **Implementación del módulo de gestión de reglas de flujo**: Implementan el módulo que recibe notificaciones de los módulos de detección y construye reglas de flujo sin acción de salida para bloquear el tráfico malicioso.

7. **Implementación del prototipo PIEDefender**: Implementan el prototipo de PIEDefender en el controlador Floodlight. PIEDefender se ejecuta como un componente adicional en el controlador.

8. **Evaluación del sistema**: Evalúan PIEDefender en el mismo entorno de software (Mininet con Floodlight). Miden la precisión de detección de inyección (97.8%), la precisión de detección DoS (97.96%), y la sobrecarga de defensa (CPU y memoria). También evalúan la efectividad de la defensa en el controlador y en los switches.

9. **Análisis de aplicabilidad**: Discuten la aplicabilidad de PIEDefender a otros tipos de ataques (desbordamiento de tabla de flujo, conflicto de reglas de flujo, ataque de fingerprinting, envenenamiento de topología, saturación, DoS basado en nuevos flujos, y DoS de baja tasa).

---

## Proceso para Resolver el Problema

Los autores realizan una evaluación exhaustiva de PIEDefender para resolver el problema del ataque de inyección de paquetes explotador en SDN. El proceso de validación incluye los siguientes pasos:

1. **Configuración experimental**: Utilizan Mininet para simular la topología de red con un controlador Floodlight v1.2, interfaz southbound OpenFlow 1.3, ejecutándose en una máquina virtual Ubuntu con Intel Core i5-8400 2.80 GHz y 8 GB de RAM. Seleccionan h1 y h6 como hosts atacantes. h1 lanza el ataque de inyección de paquetes, y h6 implementa ataques DoS basados en hosts inyectados.

2. **Verificación de la viabilidad del ataque**: Realizan dos experimentos para verificar el ataque:
   - **Inyección de hosts falsos**: h1 forja paquetes con direcciones MAC de origen generadas aleatoriamente (RandMAC() de Scapy) y los inyecta en la red a una tasa fija. Se verifica que el controlador Floodlight aprende los hosts inyectados y los añade a la topología.
   - **Ataque DoS**: h6 construye paquetes con dirección MAC de destino apuntando a hosts inyectados y direcciones IP y puertos generados aleatoriamente. Se mide el impacto en la CPU del controlador y en la ocupación de la tabla de flujo del switch.

3. **Generación del dataset para detección DoS**: Generan un dataset de 30,000 tráficos (16,925 normales y 13,075 de ataque) en el mismo entorno experimental. Los datos se utilizan para entrenar el clasificador SVM y comparar con otros algoritmos (KNN, K-Means, BayesNet, Decision Tree, Random Forest).

4. **Evaluación de la detección de inyección**: Comparan PIEDefender con PacketChecker y DoSDefender. Miden el número de hosts inyectados detectados y la precisión de detección para diferentes escalas de inyección (50, 100, 150, 200 hosts).

5. **Evaluación de la detección DoS**: Comparan SVM con otros algoritmos (KNN, K-Means, BayesNet, Decision Tree, Random Forest) en términos de precisión, recall y F1-score. También comparan PIEDefender con otros sistemas de detección DoS (entropy-based, Detpro, DoSDefender).

6. **Evaluación de la defensa en el controlador**: Miden la utilización de CPU del controlador con y sin PIEDefender durante ataques con diferentes números de hosts inyectados (50, 100, 150, 200).

7. **Evaluación de la defensa en el switch**: Miden la ocupación de la tabla de flujo del switch con y sin PIEDefender durante ataques con diferentes números de hosts inyectados.

8. **Evaluación de la sobrecarga de defensa**: Miden el consumo de CPU y memoria de PIEDefender con y sin ataques durante 60 segundos (con el ataque comenzando en el segundo 15).

9. **Análisis de aplicabilidad**: Discuten la aplicabilidad de PIEDefender a otros tipos de ataques comunes en SDN. Identifican que PIEDefender es aplicable a ataques de desbordamiento de tabla de flujo, conflicto de reglas de flujo, inyección de paquetes, envenenamiento de topología, saturación y DoS basado en nuevos flujos. No es aplicable a ataques de fingerprinting y DoS de baja tasa.

---

## Métricas y Resultados

Los autores utilizan métricas estándar de rendimiento para sistemas de detección y defensa: precisión (precision), recall, F1-score, y sobrecarga de recursos (CPU y memoria). La precisión, recall y F1-score se calculan a partir de la matriz de confusión (TP, FP, FN).

### Resultados obtenidos:

**Detección de inyección:**
- **PacketChecker**: Precisión promedio del 96.4%
- **DoSDefender**: Precisión promedio del 96.9%
- **PIEDefender**: Precisión promedio del 97.8%

**Detección DoS (Comparación de algoritmos):**
- **SVM**: Precisión 98%, Recall 98%, F1-score 98%
- **KNN**: Precisión 94%, Recall 94%, F1-score 94%
- **K-Means**: Precisión 96%, Recall 96%, F1-score 96%
- **BayesNet**: Precisión 95.92%, Recall 94%, F1-score 94.95%
- **Decision Tree**: Precisión 96.08%, Recall 98%, F1-score 97.03%
- **Random Forest**: Precisión 90%, Recall 90%, F1-score 90%

**Comparación con otros sistemas DoS:**
- **Entropy-based**: Precisión 93.88%, Recall 92%, F1-score 92.93%
- **Detpro**: Precisión 97.92%, Recall 94%, F1-score 95.92%
- **DoSDefender**: Precisión 95.92%, Recall 94%, F1-score 94.95%
- **PIEDefender**: Precisión 97.96%, Recall 96%, F1-score 96.97%

**Sobrecarga de defensa:**
- **CPU**: Promedio de 10% (pico de 24% durante la detección)
- **Memoria**: Aumento aproximado del 4% durante ataques

**Comentario sobre las métricas y el enfoque:** Considero que las métricas elegidas son adecuadas y cubren los aspectos clave de un sistema de detección y defensa: precisión (capacidad de evitar falsos positivos), recall (capacidad de detectar ataques), F1-score (equilibrio entre precisión y recall), y sobrecarga de recursos (CPU y memoria). La inclusión de la sobrecarga de defensa es particularmente importante para evaluar la viabilidad del sistema en entornos SDN con recursos limitados.

PIEDefender supera a PacketChecker y DoSDefender en la detección de inyección (97.8% vs 96.4% y 96.9%), y su precisión es más estable independientemente de la escala de inyección. En la detección DoS, SVM supera a otros algoritmos y PIEDefender supera a entropy-based, Detpro y DoSDefender en precisión y F1-score. La sobrecarga de CPU (promedio 10%) es aceptable para un sistema de defensa en tiempo real.

El enfoque de PIEDefender es particularmente acertado por varias razones:
1. La combinación de detección de inyección (basada en verificación de consistencia de mensajes) y detección DoS (basada en SVM con cinco características) proporciona una defensa en capas que aborda tanto la fase de inyección como la fase de explotación del ataque.
2. La verificación de mensajes OFPT_PORT_STATUS con un umbral evita que los atacantes puedan evadir la defensa mediante la activación falsa de mensajes de cambio de estado de puerto.
3. El uso de SVM como clasificador es apropiado porque SVM es robusto frente a datos ruidosos y tiene un buen rendimiento con un número limitado de características.
4. PIEDefender es independiente del protocolo y no requiere hardware adicional ni modificaciones en el plano de datos, lo que facilita su despliegue.

Sin embargo, hay aspectos que podrían mejorarse:
1. El sistema no es aplicable a redes inalámbricas, donde todos los hosts se conectan a través de puntos de acceso (AP) y el AP es un único puerto, lo que impide la identificación efectiva de cada terminal.
2. PIEDefender no es efectivo contra ataques de fingerprinting y DoS de baja tasa, lo que limita su aplicabilidad general.
3. La dependencia de un umbral (counter = 8) para la verificación de OFPT_PORT_STATUS podría no ser óptima en todos los entornos de red y podría requerir ajustes manuales.
4. Aunque SVM es efectivo, el dataset de entrenamiento (30,000 tráficos) podría no ser suficiente para cubrir todas las variantes de ataques DoS.
5. La evaluación se realiza en un entorno de software (Mininet) y no en un testbed real, lo que podría ocultar problemas de rendimiento en condiciones de red reales.

---

## Observaciones Críticas

El artículo presenta una contribución valiosa al introducir un nuevo ataque de inyección de paquetes explotador y su defensa PIEDefender. A continuación, realizo algunas observaciones y críticas constructivas:

1. **Validación en entornos reales**: Aunque utilizan Mininet, que es ampliamente aceptado en la investigación SDN, la evaluación se limita a un entorno simulado. Sería interesante validar PIEDefender en un testbed real con hardware de switches SDN (como switches OpenFlow físicos) y tráfico de red realista.

2. **Limitación en redes inalámbricas**: Los autores reconocen que PIEDefender no es aplicable a redes inalámbricas. Esta es una limitación significativa, ya que las redes SDN se están desplegando cada vez más en entornos inalámbricos (WiFi, 5G). Sería interesante explorar extensiones del mecanismo de detección de inyección para redes inalámbricas.

3. **Ataques de baja tasa y fingerprinting**: PIEDefender no es efectivo contra ataques de fingerprinting y DoS de baja tasa. Estos ataques están diseñados para evadir la detección basada en umbrales y tasas de mensajes, y representan una amenaza creciente en SDN. Sería valioso extender PIEDefender para detectar estos ataques.

4. **Ajuste de umbrales**: La verificación de OFPT_PORT_STATUS utiliza un umbral fijo (counter = 8). En redes con diferentes patrones de tráfico, este umbral podría no ser óptimo y podría llevar a falsos positivos o falsos negativos. Un enfoque que ajuste dinámicamente el umbral basado en las características de la red podría mejorar la robustez del sistema.

5. **Dependencia de SVM y dataset**: El módulo de detección DoS utiliza SVM con un dataset de 30,000 tráficos. En entornos con patrones de ataque en evolución, el modelo SVM podría volverse obsoleto y requerir un reentrenamiento periódico. Los autores no discuten cómo se mantendría el modelo actualizado en un entorno operativo.

6. **Impacto en el tráfico legítimo**: PIEDefender instala reglas de flujo para bloquear el tráfico malicioso. Sin embargo, no se evalúa el impacto de estas reglas en el tráfico legítimo que podría compartir características similares. Por ejemplo, si un flujo legítimo tiene un número pequeño de paquetes (PFSP) o una vida corta (PFSL), podría ser clasificado erróneamente como malicioso.

7. **Integración con otros mecanismos de seguridad**: PIEDefender se presenta como un componente independiente. Sería interesante explorar cómo se integra con otros mecanismos de seguridad en SDN para proporcionar una defensa más completa.

8. **Escalabilidad**: El sistema se evalúa en una topología con un número limitado de hosts (hasta 200 hosts inyectados). No se evalúa la escalabilidad en redes SDN grandes con miles de hosts o switches. El rendimiento del mapeo MT y el clasificador SVM podría degradarse en redes de gran escala.

9. **Complejidad computacional**: Aunque los autores afirman que PIEDefender es "ligero", no proporcionan un análisis detallado de la complejidad computacional de los algoritmos de detección. Por ejemplo, la complejidad de la verificación de mensajes OFPT_PORT_STATUS con la tabla temporal MT podría ser O(n) donde n es el número de mensajes Packet-In recibidos durante el período de verificación.

10. **Comparación con otros trabajos**: Aunque comparan PIEDefender con PacketChecker, DoSDefender y otros sistemas, no se mencionan otros trabajos relevantes como SDN-Guard (Dridi et al., 2016) o FloodDefender (Shang et al., 2017) en el contexto de la detección de DoS. Una comparación más amplia con el estado del arte fortalecería las conclusiones.

---

## Relevancia para el Proyecto

PIEDefender es especialmente relevante porque aborda los **ataques de inyección de paquetes y su explotación para DoS** en SDN, un vector de ataque que otros sistemas no cubren adecuadamente. Los aspectos clave aplicables a nuestro proyecto son:

1. **Detección de inyección de hosts falsos**: El método de verificación de consistencia de mensajes Packet-In y OFPT_PORT_STATUS es aplicable para prevenir la inyección de hosts falsos en la topología SDN.

2. **Características para detección DoS**: Las cinco características utilizadas por el clasificador SVM (RPI, RFM, PIRF, PFSP, PFSL) son relevantes para detectar ataques DoS basados en inyección de paquetes y pueden ser adaptadas para nuestro sistema.

3. **Defensa en capas**: La combinación de detección de inyección y detección DoS proporciona una defensa en capas que aborda tanto la fase de inyección como la fase de explotación del ataque.

4. **Baja sobrecarga**: Con un promedio de 10% de CPU, PIEDefender demuestra que es posible implementar una defensa efectiva sin sobrecargar el controlador.

5. **Independencia del protocolo**: PIEDefender no requiere modificaciones en el plano de datos ni hardware adicional, lo que facilita su despliegue en entornos SDN existentes.

Aunque PIEDefender tiene limitaciones (no aplicable a redes inalámbricas, no efectivo contra baja tasa), sus principios de detección y mitigación son aplicables a nuestro sistema SDN-ML.

---

**Referencia:**  
Li, J., Qin, S., Tu, T., Zhang, H., & Li, Y. (2022). Packet Injection Exploiting Attack and Mitigation in Software-Defined Networks. *Applied Sciences (MDPI)*, 12(3), 1103.