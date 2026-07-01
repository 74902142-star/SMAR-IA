# Estado del Arte - Artículo 1: DDoSBlocker

**Autor(es):** Mitali Sinha, Padmalochan Bera, Manoranjan Satpathy, Kshira Sagar Sahoo, Joel J.P.C. Rodrigues  
**Título:** DDoSBlocker: Enhancing SDN security with time-based address mapping and AI-driven approach  
**Journal:** Computer Networks  
**Volumen (issue):** Volume 259  
**Año:** 2025  
**Artículo:** 111078  

---

## Estado del Arte

En la introducción, los autores contextualizan el problema de los ataques DDoS en redes definidas por software (SDN). Explican que SDN separa el plano de control del plano de datos, lo que ofrece ventajas en la gestión de red, pero también introduce vulnerabilidades debido a la comunicación constante entre switches y el controlador a través de la interfaz southbound. Esta comunicación puede ser explotada por atacantes que inyectan paquetes falsos con campos de cabecera spoofeados, saturando el controlador y provocando congestión y caída del servicio.

Los autores revisan las estrategias de defensa existentes, clasificándolas en dos categorías principales: enfoques de prevención y enfoques de detección-mitigación. Entre los primeros, citan los trabajos de Fichera et al. (2015), Deng et al. (2019) y otros, que proponen métodos basados en proxy SYN para ataques TCP-SYN. Estos métodos, aunque efectivos para ese tipo específico de ataque, introducen una sobrecarga significativa en el tiempo de respuesta y procesamiento de paquetes.

En cuanto a los enfoques de detección-mitigación, los autores mencionan los métodos de mapeo de direcciones, como los basados en ARP, DHCP y puertos, que mantienen una tabla de correspondencia entre ubicación de red (host_port), direcciones MAC e IP. Estos métodos, utilizados en trabajos previos, son efectivos contra spoofing de MAC e IP, pero se ven superados por ataques que saturan con solicitudes ARP, DHCP o cambios de estado de puerto, y además pueden clasificar erróneamente hosts legítimos en escenarios de pérdida de paquetes.

También revisan los enfoques basados en machine learning (ML), deep learning (DL) o entropía. Aquí citan trabajos como los de Wang et al. (2023), Liu et al. (2022), Novaes et al. (2021), Giotis et al. (2014), Sahoo et al. (2018), Aladailieh et al. (2021), Najar et al. (2024) y Yungaciela-Naula et al. (2022). Señalan que muchos de estos trabajos solo se centran en la detección de ataques, sin abordar la mitigación, o bien proponen soluciones de mitigación que bloquean tanto tráfico malicioso como legítimo (bloqueo en punto de destino), o que tardan mucho tiempo en mitigar después de la detección, como los métodos de backtracking y clustering mencionados en trabajos de 2024.

Finalmente, los autores identifican tres desafíos clave no resueltos por la literatura existente:

1. La identificación eficiente de puertos de switch maliciosos que generan paquetes falsos con direcciones src_IP y src_MAC spooferadas.
2. La detección de puertos que generan paquetes falsos con campos src_port, dst_IP y dst_port spooferados utilizando direcciones MAC e IP válidas.
3. El bloqueo temprano de atacantes en sus puertos de switch para prevenir actividad maliciosa adicional.

---

## Motivación del Autor (Críticas a Otros Trabajos)

Los autores realizan una crítica fundamentada a los trabajos previos, señalando sus limitaciones y justificando la necesidad de su propuesta:

- **Métodos de prevención basados en proxy SYN**: Aunque detienen ataques TCP-SYN, introducen latencia y sobrecarga de procesamiento, lo que los hace inadecuados para entornos de alta velocidad o con múltiples tipos de ataques.
- **Métodos de mapeo de direcciones existentes**: Son vulnerables a ataques que generan un gran volumen de solicitudes ARP, DHCP y de estado de puertos, lo que los desborda y provoca falsos positivos o bloqueos incorrectos de hosts legítimos. Además, no están diseñados para manejar ataques donde el atacante utiliza direcciones MAC e IP válidas pero falsifica otros campos de la cabecera (como puertos o IP de destino).
- **Enfoques basados en ML, DL o entropía**: La mayoría se limita a la detección sin ofrecer mitigación, o las soluciones de mitigación existentes bloquean todo el tráfico en el punto de destino (afectando a usuarios legítimos) o requieren un tiempo excesivo para mitigar (como backtracking y clustering), lo que permite que el ataque cause daños durante ese intervalo.

Los autores justifican su trabajo en la necesidad de superar estos vacíos: proponen un sistema ligero e independiente del protocolo que detecte y mitigue ataques DDoS en SDN bloqueando en el origen (switch port) sin afectar al tráfico legítimo, combinando un método de mapeo de direcciones basado en tiempo (resistente a inundaciones ARP/DHCP) con un enfoque de ML activado por disparadores (triggering-based) que introduce nuevas características de flujo para mejorar la precisión y reducir los falsos positivos.

---

## Descripción del Aporte

El aporte principal de los autores es el sistema **DDoSBlocker**, una solución de defensa contra ataques DDoS en redes SDN que es ligera, independiente del protocolo y capaz de identificar y bloquear los puntos de origen de los ataques sin interrumpir el tráfico legítimo.

El sistema se compone de dos módulos principales:

### 1. Módulo de autenticación de packet in (Packet in Authentication Module)

Utiliza un método de mapeo de direcciones basado en tiempo para verificar la legitimidad de los paquetes entrantes. Mantiene una tabla de mapeo que asocia cada host_port (puerto del switch) con las direcciones MAC e IP válidas. A diferencia de soluciones anteriores, este mapeo se actualiza periódicamente y es resistente a ataques de inundación ARP/DHCP porque solo verifica los primeros dos paquetes de un nuevo flujo, en lugar de procesar cada solicitud. Esto permite detectar ataques de spoofing de src_IP y src_MAC con solo dos paquetes, reduciendo drásticamente el tiempo de detección.

### 2. Módulo de detección DDoS (DDoS Detection Module)

Se activa mediante un mecanismo de disparo (triggering-based) cuando el controlador recibe una tasa anormalmente alta de mensajes packet_in desde un puerto específico. En ese momento, el módulo extrae características de los flujos y utiliza un clasificador de machine learning (Random Forest) para determinar si el puerto está generando tráfico malicioso. Para ello, introduce cuatro nuevas características:

- **Porcentaje de IP de destino falsas (percentage of fake destination IPs)**: Mide la proporción de paquetes con direcciones IP de destino que no existen en la red.
- **Promedio de bytes por paquete (average bytes per packet)**: Analiza el tamaño medio de los paquetes, que en ataques suele ser anormalmente pequeño o grande.
- **Porcentaje de reglas de flujo bidireccionales (percentage of bidirectional flow rules)**: Evalúa cuántas reglas de flujo son bidireccionales, ya que en ataques suelen ser unidireccionales.
- **Porcentaje de reglas de flujo falsas (percentage of fake flow rules)**: Detecta reglas de flujo que no corresponden a comunicaciones reales.

Una vez identificado el puerto atacante, el sistema instala reglas de bloqueo directamente en el switch origen, deteniendo el ataque en su punto de entrada y evitando que el tráfico malicioso llegue al controlador o a otros dispositivos.

El sistema fue implementado en el controlador Floodlight y evaluado en cuatro escenarios de ataque diferentes, mostrando una precisión del 99.71%, un tiempo de detección promedio de 3 segundos, un tiempo de mitigación de 0.5 segundos y una tasa de falsos positivos del 0.51%.

---

## Proceso para Obtener el Aporte

Los autores describen un proceso metodológico riguroso para obtener su aporte, que combina técnicas de autenticación de paquetes y machine learning. El proceso se estructura en las siguientes etapas:

1. **Formulación de modelos de ataque**: Identifican y definen cinco tipos de ataques DDoS basados en el spoofing de diferentes campos de la cabecera de los paquetes: (a) inundación MAC (spoofing de src_MAC), (b) spoofing de src_IP, (c) spoofing de src_port, (d) spoofing de dst_IP, y (e) spoofing de dst_port. Esta clasificación les permite diseñar un sistema que aborde todas las variantes.

2. **Diseño del módulo de autenticación de packet_in**: Proponen un método de mapeo de direcciones basado en tiempo que mantiene una tabla de correspondencia entre host_port, MAC e IP. La clave está en que este mapeo no se actualiza con cada paquete, sino que se construye a partir de tráfico de control (ARP, DHCP, etc.) y se valida periódicamente. Cuando llega un packet_in, el módulo extrae la información de la cabecera y la compara con la tabla.

3. **Diseño del módulo de detección DDoS con ML**: Para ataques que utilizan direcciones MAC e IP válidas pero falsifican otros campos (puertos, IP destino), el módulo de autenticación no es suficiente. Por ello, implementan un módulo de detección basado en ML que se activa cuando la tasa de packet_in supera un umbral (triggering-based). En ese momento, el módulo extrae de los flujos las cuatro características novedosas mencionadas anteriormente y las alimenta a un clasificador Random Forest. Este clasificador fue entrenado con un conjunto de datos generado en su entorno de simulación, que incluye tráfico normal y diferentes tipos de ataques.

4. **Integración y bloqueo en el origen**: Una vez que el clasificador identifica un puerto como malicioso, el sistema instala una regla de bloqueo (drop) en la tabla de flujo del switch correspondiente, utilizando la interfaz OpenFlow. Esto detiene el ataque en su fuente, sin afectar a otros puertos o dispositivos.

5. **Implementación y validación**: Implementan DDoSBlocker como un módulo adicional en el controlador Floodlight. Utilizan Mininet para emular la topología de red y generan tráfico de ataque y benigno para evaluar el sistema. El proceso incluye la recolección de datos de rendimiento (tiempos de detección, mitigación, precisión, tasa de falsos positivos) y la comparación con otros métodos de referencia.

---

## Proceso para Resolver el Problema

Los autores realizan una evaluación exhaustiva de DDoSBlocker para resolver el problema de los ataques DDoS en SDN. El proceso de validación incluye los siguientes pasos:

1. **Configuración experimental**: Utilizan el emulador Mininet para crear una topología de red realista (Topología-1) que consta de un controlador Floodlight, 11 switches compatibles con OpenFlow 1.0 y 123 hosts distribuidos en diferentes subredes. Esta topología simula un entorno de red empresarial o de centro de datos. El experimento se ejecuta en una PC con procesador Intel Core i7-1165G7 a 2.80 GHz y 8 GB de RAM.

2. **Generación de escenarios de ataque**: Definen cuatro escenarios de ataque basados en los modelos formulados anteriormente. Por ejemplo, un escenario donde los atacantes generan paquetes con direcciones MAC falsas, otro con IP falsas, etc.

3. **Medición de rendimiento**: Durante los experimentos, registran múltiples métricas:
   - **Tiempo de detección**: Tiempo transcurrido desde el inicio del ataque hasta que el sistema lo identifica.
   - **Tiempo de mitigación**: Tiempo que tarda el sistema en instalar las reglas de bloqueo después de la detección.
   - **Precisión (Accuracy)**: Proporción de clasificaciones correctas (ataque vs. benigno).
   - **Tasa de falsos positivos (FPR)**: Proporción de tráfico benigno clasificado erróneamente como ataque.
   - **Tasa de falsos negativos (FNR)**: Proporción de tráfico de ataque no detectado.

4. **Comparación con otras soluciones**: Comparan el rendimiento de DDoSBlocker con tres enfoques existentes:
   - **Bloqueo en punto de destino**: Bloquea todo el tráfico hacia el destino atacado, afectando también a usuarios legítimos.
   - **Clustering**: Agrupa flujos similares para identificar ataques, pero tarda más en mitigar.
   - **Backtracking**: Rastreo inverso para encontrar la fuente del ataque, que también es lento.

Los resultados muestran que DDoSBlocker supera a estos métodos en todos los aspectos. Por ejemplo, el tiempo de detección es aproximadamente un 50-53% menor que el de las soluciones existentes, y el tiempo de mitigación es de solo 0.5 segundos, mientras que el backtracking y clustering requieren varios segundos más. Además, la precisión de DDoSBlocker (99.71%) es superior, y su tasa de falsos positivos (0.51%) es significativamente más baja que la de otros métodos.

---

## Métricas y Resultados

Los autores utilizan métricas estándar de rendimiento en sistemas de detección y mitigación de DDoS: precisión (accuracy), tiempo de detección, tiempo de mitigación, tasa de falsos positivos (FPR) y tasa de falsos negativos (FNR). Además, comparan estas métricas con las de otros enfoques.

### Resultados obtenidos:

| Métrica | Valor |
|---|---|
| Precisión (Accuracy) | 99.71% |
| Tiempo de detección (promedio) | 3 segundos |
| Tiempo de mitigación (promedio) | 0.5 segundos |
| Tasa de falsos positivos (FPR) | 0.51% |

### Comparación con otros enfoques:

- **Bloqueo en punto de destino**: Suele tener una FPR más alta porque bloquea tráfico legítimo.
- **Backtracking y clustering**: Tienen tiempos de mitigación mucho mayores (varios segundos o más).
- La precisión del 99.71% es excepcionalmente alta, superando a muchos modelos de ML reportados en la literatura para detección de DDoS en SDN.

**Comentario sobre las métricas y el enfoque**: Considero que las métricas elegidas son adecuadas y cubren los aspectos clave de un sistema de defensa: exactitud, rapidez y capacidad de no afectar al tráfico benigno. La inclusión del tiempo de mitigación es especialmente relevante, ya que muchos trabajos se centran solo en la detección. El uso de cuatro nuevas características es un acierto, ya que permite capturar patrones específicos de ataques en SDN que otras características no consideran. Sin embargo, sería interesante evaluar el sistema bajo ataques de baja tasa (low-rate DDoS) o ataques distribuidos con patrones variables, ya que estos pueden eludir los umbrales de disparo. También sería valioso medir el consumo de recursos del módulo de ML (CPU, memoria) en el controlador, para asegurar que realmente es "ligero" como afirman.

---

## Observaciones Críticas

El artículo presenta una solución innovadora y bien fundamentada para la defensa contra DDoS en SDN. A continuación, realizo algunas observaciones y críticas constructivas:

1. **Escalabilidad**: El sistema fue evaluado en una topología de 11 switches y 123 hosts. Sería interesante probar su escalabilidad en redes más grandes (por ejemplo, cientos de switches y miles de hosts) para verificar que el tiempo de detección y mitigación se mantiene, y que el módulo de ML no se convierte en un cuello de botella.

2. **Ataques de baja tasa**: El mecanismo de disparo basado en umbral de tasa de packet_in podría no activarse ante ataques de baja tasa (low-rate DDoS), que están diseñados para evadir la detección basada en umbrales. Los autores no evalúan este escenario.

3. **Actualización del mapeo temporal**: El método de mapeo de direcciones basado en tiempo requiere una actualización periódica. Los autores no detallan con qué frecuencia se actualiza ni cómo se manejan los cambios legítimos de direcciones (por ejemplo, un host que se mueve a otro puerto). Si la actualización es lenta, podría generar falsos positivos en entornos dinámicos.

4. **Consumo de recursos**: Aunque el sistema es denominado "ligero", no se proporcionan mediciones concretas del consumo de CPU y memoria del módulo de ML en el controlador. Esto es relevante para entornos con recursos limitados.

5. **Comparación con otros clasificadores**: Los autores utilizan Random Forest, pero no justifican por qué lo eligieron sobre otros algoritmos (por ejemplo, SVM, redes neuronales). Sería útil incluir una comparativa de rendimiento entre varios clasificadores para demostrar que Random Forest es la mejor opción.

6. **Generalización**: El sistema fue validado con ataques generados en un entorno controlado. Sería deseable probarlo con conjuntos de datos públicos (como CIC-DDoS2019) para asegurar que los resultados son reproducibles y generalizables.

---

## Relevancia para el Proyecto

DDoSBlocker es una solución completa que cubre tanto la detección como la mitigación de ataques DDoS en SDN, con un enfoque práctico que combina autenticación por mapeo temporal y ML. Su alta precisión y baja latencia lo hacen adecuado para entornos en tiempo real. Además, introduce características novedosas que mejoran la detección de ataques sofisticados con spoofing de múltiples campos. Es una referencia obligada para el diseño de un sistema de defensa SDN-ML.

---

**Referencia:**  
Sinha, M., Bera, P., Satpathy, M., Sahoo, K. S., & Rodrigues, J. J. P. C. (2025). DDoSBlocker: Enhancing SDN security with time-based address mapping and AI-driven approach. *Computer Networks*, 259, 111078.