# Estado del Arte - Artículo 2: Machine-Learning-Enabled DDoS Attacks Detection in P4 Programmable Networks

**Autor(es):** Francesco Musumeci, Ali Can Fidanci, Francesco Paolucci, Filippo Cugini, Massimo Tornatore  
**Título:** Machine-Learning-Enabled DDoS Attacks Detection in P4 Programmable Networks  
**Journal:** Journal of Network and Systems Management  
**Volumen (issue):** 30 (21)  
**Año:** 2022  
**Páginas:** 1 – 27  

---

## Estado del Arte

En la sección de trabajos relacionados (Related Work), los autores realizan una revisión exhaustiva de las estrategias de detección de ataques DDoS basadas en Machine Learning y del contexto de redes SDN con planos de datos programables mediante P4.

### Detección de ataques DDoS con ML:
Los autores citan numerosos trabajos que utilizan algoritmos de ML para detectar ataques DDoS, clasificándolos por tipo de algoritmo:
- **SVM (Support Vector Machine):** Hoyos et al. (2016), Ramamoorthi et al. (2011), Sahoo et al. (2020), Saini et al. (2020), Subbulakshmi et al. (2011), Ye et al. (2018).
- **Redes neuronales artificiales (ANN):** Bhardwaj et al. (2020), Sumathi y Karthikeyan (2020), Yuan et al. (2017).
- **Otros algoritmos de ML:** Aljuhani (2021), AlMomin e Ibrahim (2020), Correa et al. (2021), Gu et al. (2019), Mhamdi et al. (2020), de Miranda Rios et al. (2021).
- **Reinforcement learning:** Simpson et al. (2020) para mitigación de DDoS.

### Detección de ataques en el contexto específico de SDN:
Los autores revisan trabajos que abordan la detección de DDoS en arquitecturas SDN, incluyendo:
- Abou El Houda et al. (2020): Inteligencia en SDN para mitigar DDoS.
- Alamri y Thayananthan (2020): XGBoost para proteger SDN.
- Dinh y Park (2021): Marco de big data para detección en SDN.
- Dong y Sarem (2020): KNN mejorado con grado de ataque DDoS.
- Kokila et al. (2014): SVM para detección en SDN.
- Mousavi y St-Hilaire (2018): Detección temprana de DDoS contra controladores SDN.
- Pérez-Díaz et al. (2020): Arquitectura flexible para ataques de baja tasa.
- Phan et al. (2020): DeepGuard con monitoreo granular de flujos.
- Ravi y Shalinie (2020): Detección impulsada por aprendizaje en IoT vía SDN.
- Sudar et al. (2021): Técnicas de ML en SDN.
- Tan et al. (2020): Nuevo marco para detección y defensa en SDN.
- Zhijun et al. (2020): Detección de ataques de baja tasa con factorization machine.
- Zhu et al. (2018): Detección preservando privacidad usando tráfico cross-domain.

### Planos de datos stateful y P4 para mitigación de DDoS:
Los autores destacan que, aunque ha surgido una cantidad significativa de trabajo sobre planos de datos stateful en SDN para mitigación de DDoS, la mayoría no explota mecanismos de detección sofisticados basados en ML. Citando trabajos específicos:
- Afek et al. (2017): Arquitectura distribuida de switches stateful.
- Sviridov et al. (2018): Modelo de coordinación de switches stateful (LODGE).
- Lapolli et al. (2019): Offloading de detección en tiempo real a planos de datos programables.
- Ilha et al. (2020): Euclid, enfoque P4-based completamente in-network.
- Paolucci et al. (2019): P4 edge node para traffic engineering y ciberseguridad.
- Febro et al. (2019): Defensa distribuida SIP DDoS con P4.
- Zhang et al. (2020): Poseidon, mitigación de ataques volumétricos con switches programables.
- Friday et al. (2020): Estrategia unificada de detección y mitigación in-network.

### Lenguaje P4:
Los autores describen P4 como un lenguaje de alto nivel, independiente del vendor, diseñado para habilitar pipelines y planos de reenvío personalizados en switches SDN, no limitados por la pila de protocolos de funciones fijas tradicionales.

---

## Motivación del Autor (Críticas a Otros Trabajos)

La motivación principal de Musumeci et al. surge de una crítica estructural a las limitaciones de los enfoques existentes:

1. **Sobrecarga del controlador SDN:** En arquitecturas SDN tradicionales, los controladores son puntos críticos de fallo. Los ataques DDoS pueden afectar los controladores directamente (inundándolos con paquetes no legítimos) o indirectamente, provocando que los switches generen un exceso de mensajes packet_in hacia el controlador.
2. **Limitaciones de detección basada en umbrales:** Los trabajos previos que utilizan P4 para mitigación de DDoS (como Zhang et al. con Poseidon, o Friday et al.) emplean mecanismos de defensa basados en umbrales (threshold-based). Estos enfoques son rígidos y no se adaptan bien a cambios en las características del tráfico legítimo, pudiendo generar falsos positivos o no detectar ataques de baja tasa.
3. **Falta de integración ML + P4:** Aunque existen trabajos sobre detección DDoS con ML y trabajos sobre mitigación con P4, según los autores esta es la primera vez que se combinan ambos aspectos en el contexto de ciberseguridad. Los trabajos previos con P4 no explotan mecanismos de detección sofisticados como los basados en ML, y los trabajos con ML para DDoS no aprovechan las capacidades de procesamiento en el plano de datos que ofrece P4.
4. **Latencia en la extracción de características:** Las soluciones tradicionales que realizan deep packet inspection en el módulo de detección (ya sea en el controlador o en una entidad externa) introducen latencias significativas. Los autores identifican que el offloading de la extracción de características al plano de datos puede reducir drásticamente el tiempo de detección.
5. **Limitaciones de su trabajo previo:** En su artículo anterior (Musumeci et al., ICC 2020), los autores ya habían combinado ML y P4 para detección de ataques TCP flood, pero este trabajo lo extiende significativamente:
   - Incluyen redes neuronales artificiales (ANN) entre los algoritmos considerados.
   - Evalúan no solo accuracy sino también precision, recall y F1-score, más adecuados para datasets desbalanceados.
   - Comparan dos arquitecturas distintas: Standalone y Correlated DAD.
   - Evalúan el impacto de la tasa de ataque en el rendimiento de la detección.
   - Analizan tres escenarios de implementación en tiempo real: packet mirroring, header mirroring y P4-metadata extraction.

Los autores justifican su trabajo argumentando que se necesita una solución que combine la capacidad de ML para detectar patrones de anomalías con el potencial de los planos de datos stateful (P4) para procesar y recolectar información de tráfico como características, minimizando el riesgo de saturación del controlador SDN y reduciendo la latencia de detección.

---

## Descripción del Aporte

El aporte central de Musumeci et al. es un marco de detección de ataques DDoS asistido por ML que opera en redes SDN con planos de datos programables mediante P4, específicamente diseñado para ataques TCP SYN flood. Los componentes clave son:

### 1. Dos arquitecturas de detección comparadas:
- **Standalone DAD:** Cada switch P4 ejecuta un módulo de detección ML localmente, basándose únicamente en el tráfico observado localmente.
- **Correlated DAD:** Un único módulo de detección recibe información de tráfico de múltiples switches P4 y toma decisiones basadas en información global de la red.

### 2. Cuatro algoritmos de ML evaluados:
Random Forest (RF), K-Nearest Neighbours (KNN), Support Vector Machine (SVM) y Artificial Neural Network (ANN). Se seleccionan los mejores hiperparámetros mediante validación cruzada de cinco pliegues.

### 3. Cinco características de tráfico extraídas:
Para cada ventana de tiempo de duración T, se extraen:
- Longitud promedio de paquetes (Len(t))
- Ratio de paquetes TCP (R_TCP(t))
- Ratio de paquetes UDP (R_UDP(t))
- Ratio TCP/UDP (R_TU(t))
- Porcentaje de paquetes TCP con flag SYN activo (Flags(t))

### 4. Tres escenarios de implementación P4 para extracción de características:
- **Packet mirroring:** El switch reenvía paquetes completos al módulo ML.
- **Header mirroring:** El switch reenvía solo los headers de los paquetes.
- **P4-metadata extraction:** El switch extrae las características directamente en el plano de datos y envía solo los metadatos (features) al clasificador ML.

### 5. Validación en tiempo real:
Los autores evalúan el tiempo de detección en un escenario "online" donde el módulo ML interactúa directamente con el switch P4.

El impacto de esta contribución es significativo para la seguridad de redes SDN modernas. Los ataques DDoS, especialmente TCP SYN flood, representan una de las amenazas más críticas porque explotan el mecanismo de establecimiento de conexiones TCP, consumiendo recursos de memoria y computación en el sistema víctima. En arquitecturas SDN, estos ataques tienen un efecto multiplicador porque pueden saturar el controlador centralizado, afectando toda la red. La solución propuesta permite detectar y mitigar estos ataques directamente en el plano de datos, preservando la estabilidad del controlador y reduciendo la latencia de detección a menos de 200 μs.

---

## Proceso para Obtener el Aporte

Los autores describen un proceso metodológico estructurado para obtener su aporte, que combina el diseño de arquitecturas, la selección de características y la implementación en P4:

1. **Modelado del problema de detección:** El DAD se modela como un problema de clasificación binaria. Dado el tráfico observado en una ventana de tiempo de duración T predefinida, el módulo de detección emite una decisión: etiqueta "1: ataque" o "0: sin ataque".

2. **Diseño de arquitecturas:**
   - **Standalone DAD:** Un módulo ML-asistido se despliega en cada switch P4. Cada switch realiza detección basándose únicamente en tráfico localmente observado.
   - **Correlated DAD:** Un único módulo DAD recibe información de tráfico de varios switches P4 y toma decisiones basadas en tráfico globalmente observado. El módulo puede estar co-ubicado con el controlador SDN o desplegado físicamente en uno de los switches P4.

3. **Selección de características:** Se eligen cinco características (f1-f5) basadas en la literatura sobre detección DDoS, adaptadas específicamente para ataques TCP flood: longitud promedio de paquetes, ratios de TCP/UDP, ratio TCP/UDP y porcentaje de flags SYN.

4. **Implementación de extracción de características en P4:**
   - Definición de parsers para headers Ethernet, IP, UDP y TCP.
   - Definición de registros (stateful objects) para almacenar contadores de paquetes IP, UDP, TCP y TCP SYN.
   - Definición de un header extra personalizado (my_int_header_t) para transmitir las estadísticas al módulo DAD.
   - Pipeline de control condicional que actualiza registros, verifica si la ventana de tráfico terminó (basada en conteo de paquetes, 10^5 paquetes en el código), y genera paquetes de reporte con las características extraídas.

5. **Selección de algoritmos ML y hiperparámetros:** Se evalúan RF, KNN, SVM y ANN con diferentes combinaciones de hiperparámetros mediante validación cruzada de cinco pliegues. Se seleccionan los hiperparámetros que logran accuracy > 97% con duración de entrenamiento razonablemente baja.

---

## Proceso para Resolver el Problema

Los autores validan su propuesta mediante un riguroso proceso experimental:

### Generación de tráfico y datasets:
- Se utiliza un generador de tráfico Spirent N4U para crear tráficos realistas de 15 minutos.
- Tráfico de fondo: 13.5 Mbit/s TCP, 11.4 Mbit/s UDP, 5.1 Mbit/s IP raw (perfil IMIX según RFC 6985 y RFC 2544).
- Tráfico de ataque: TCP SYN flood a 26.5 kbit/s (tasa baja para probar sensibilidad), con duración promedio de 10s, IPs fuente aleatorias y escaneo incremental de puertos TCP.
- Se generan datasets extrayendo ventanas de duración T ∈ {0.5, 1, 2, 10} s con período de muestreo δ ∈ {0.01, 0.05, 0.1, 0.2, 0.5, 1} s.
- Las ventanas se etiquetan como "1: TCP flood" si contienen al menos un paquete de ataque, de lo contrario "0: no-ataque".

### Evaluación de algoritmos ML:
- Implementación en Python con librerías keras y sklearn.
- Validación cruzada de cinco pliegues.
- Evaluación de impacto de T y δ en accuracy, precision, recall y F1-score.
- Medición de tiempo de entrenamiento y tiempo de clasificación (test time).

### Comparación de arquitecturas Standalone vs. Correlated:
- Red de muestra con 3 switches P4.
- Se generan 6 escenarios con tasas de ataque: 26.5, 13.25, 10.6, 8, 6.7 y 4 kbit/s (100%, 50%, 40%, 30%, 25% y 15% de la tasa máxima).
- En Standalone, el tráfico se divide aleatoriamente en tres subconjuntos iguales, uno por switch.
- En Correlated, la clasificación se basa en información agregada de los tres switches.

### Evaluación de implementación en tiempo real con P4:
- Se evalúan tres escenarios: packet mirroring, header mirroring y P4-metadata extraction.
- Se miden tres contribuciones de latencia:
  - t1: tiempo de procesamiento en el switch P4.
  - t2: tiempo de extracción de características.
  - t3: tiempo de clasificación ML.
- El switch P4 se evalúa usando BMV2 en Linux Box (Intel Xeon E5-2620v2, 16GB RAM, interfaces 10GbE).
- Las latencias se miden con Spirent N4U Traffic generator y analyzer.

---

## Métricas y Resultados

Los autores utilizan un conjunto completo de métricas para evaluar el rendimiento:

**Métricas de clasificación:**
- **Accuracy (A):** Fracción de ventanas correctamente clasificadas.
- **Precision (P):** Fracción de ventanas positivas correctamente clasificadas sobre el total clasificado como positivo.
- **Recall (R):** Fracción de ventanas positivas correctamente clasificadas sobre el total realmente positivo.
- **F1-score:** Media armónica de precision y recall.

**Métricas de complejidad algorítmica:**
- **Training duration:** Tiempo promedio de entrenamiento (en validación cruzada de 5 pliegues).
- **Test time:** Tiempo de clasificación de una sola ventana de tráfico.

### Resultados principales:

| Algoritmo | Accuracy | Precision | Recall | F1-score | Test Time (μs) |
|---|---|---|---|---|---|
| KNN | > 96.6% | > 96.6% | ~96.6% | > 96.6% | 113.18 |
| RF | > 98.6% | > 98.6% | ~98.6% | > 98.6% | 112.68 |
| SVM | > 98.6% | > 98.6% | ~98.6% | > 98.6% | 1.75 |
| ANN | > 98.6% | > 98.6% | ~98.6% | > 98.6% | 279.95 |

### Comparación Standalone vs. Correlated:
- La arquitectura Correlated muestra mayor accuracy que cualquier switch individual en Standalone, especialmente para tasas de ataque bajas (< 8 kbit/s).
- Para tasas de ataque > 13.25 kbit/s, la accuracy de Standalone supera el 99% y se aproxima a la de Correlated.

### Latencia de implementación en tiempo real (T=1s, δ=0.01s):

| Escenario | RF t1 (μs) | RF t2 (s) | RF t3 (μs) | SVM t1 (μs) | SVM t2 (s) | SVM t3 (μs) |
|---|---|---|---|---|---|---|
| Packet mirroring | 75 | 16.9 | 5.6 | 75 | 16.3 | 14.4 |
| Header mirroring | 65 | 14.9 | 5.6 | 65 | 14.3 | 14.4 |
| P4-metadata | 110 | ~0 | 5.6 | 110 | ~0 | 14.4 |

**Comentario sobre las métricas y resultados:** Considero que la elección de métricas es apropiada y completa. El uso de accuracy, precision, recall y F1-score proporciona una visión holística del desempeño del clasificador, especialmente importante dado que el dataset está desbalanceado (ventanas con ataque son minoría). La inclusión de métricas de complejidad (training time, test time) es crucial para evaluar la viabilidad de implementación en tiempo real.

Los resultados demuestran claramente que:
1. Todos los algoritmos logran rendimiento excepcional (> 98% en la mayoría de métricas para RF, SVM y ANN).
2. SVM tiene el test time más bajo (1.75 μs), dos órdenes de magnitud menor que los demás, lo que lo hace ideal para detección en tiempo real.
3. La extracción de características en P4 (metadata extraction) reduce drásticamente la latencia total de detección a menos de 200 μs, comparado con ~16 segundos en packet mirroring.

Sin embargo, podrían haberse incluido métricas adicionales como:
- Tasa de falsos positivos/negativos desglosada por tasa de ataque.
- Robustez ante ataques de baja tasa más sofisticados (slowloris, ataques de pulso).
- Consumo de recursos del switch P4 (memoria, uso de registros stateful).
- Escalabilidad: número máximo de flujos concurrentes que el switch puede manejar.

---

## Observaciones Críticas

El artículo de Musumeci et al. presenta una contribución técnica sólida e innovadora, pero considero que existen aspectos que podrían profundizarse o revisarse:

1. **Generalización a otros tipos de ataques:** El trabajo se enfoca exclusivamente en ataques TCP SYN flood. Aunque los autores mencionan como trabajo futuro la identificación de tipos de ataque con clasificadores multiclass, no se evalúa la efectividad del método contra otros vectores DDoS comunes como UDP flood, ICMP flood, HTTP flood, o ataques de amplificación DNS.
2. **Tráfico de fondo relativamente estático:** El tráfico de fondo se genera con parámetros fijos (13.5 Mbit/s TCP, 11.4 Mbit/s UDP, 5.1 Mbit/s IP) durante 15 minutos. En redes reales, el tráfico es mucho más dinámico y variable. No se evalúa cómo el modelo se comporta ante cambios súbitos en el patrón de tráfico legítimo (por ejemplo, picos de tráfico por eventos especiales).
3. **Ataque de baja tasa limitado:** Aunque se prueban tasas de ataque tan bajas como 4 kbit/s (15% de la tasa máxima), estas tasas siguen siendo relativamente constantes. No se evalúan ataques de "pulso" o "slow" que varían su intensidad a lo largo del tiempo para evadir detección.
4. **Dependencia del perfil IMIX:** El tráfico sigue la distribución IMIX (60-byte: 58.33%, 576-byte: 33.33%, 1500-byte: 8.33%). Aunque es un estándar de la industria, el rendimiento del clasificador podría variar significativamente con otros perfiles de tráfico (por ejemplo, dominado por video streaming con paquetes grandes o IoT con paquetes muy pequeños).
5. **Sobrecarga del plano de datos P4:** Aunque los autores mencionan que la extracción de características en P4 es eficiente, no se discute el impacto en el rendimiento de reenvío del switch cuando opera a línea rate (10 Gbps o más). Los registros stateful y el procesamiento adicional podrían afectar el throughput máximo del switch.
6. **Falta de mecanismo de mitigación activa:** El artículo se enfoca en la detección, pero no propone ni evalúa mecanismos de mitigación automática una vez detectado el ataque (por ejemplo, bloqueo de flujos, rate limiting dinámico, o redirección de tráfico). Los autores mencionan que las decisiones de reenvío (drop, forward to controller) están fuera del alcance del artículo.
7. **Escalabilidad de Correlated DAD:** Aunque Correlated DAD muestra mejor accuracy, no se discute el overhead de comunicación entre switches y el módulo centralizado. En una red con cientos de switches, el ancho de banda y la latencia de reportar características desde todos los switches podrían convertirse en cuellos de botella.
8. **Reentrenamiento del modelo:** No se discute con qué frecuencia debe reentrenarse el modelo ML ni cómo se maneja el concept drift (cambios en el comportamiento del tráfico legítimo a lo largo del tiempo).
9. **Seguridad del propio mecanismo de detección:** Un atacante sofisticado podría intentar:
   - Envenenar el modelo ML enviando tráfico que simule características legítimas.
   - Satuar los registros stateful del switch P4 para evadir la detección.
   - Identificar el patrón de sondas y adaptar el ataque para evadirlo.

---

## Relevancia para el Proyecto

Este artículo es fundamental porque demuestra la viabilidad de combinar **Machine Learning con planos de datos programables P4** para lograr detección de DDoS en tiempo real con latencias extremadamente bajas (< 200 μs). La arquitectura Correlated DAD ofrece una mejora significativa en la detección de ataques de baja tasa. Para un sistema SDN-ML, este trabajo proporciona una base sólida para implementar la extracción de características en el plano de datos, reduciendo la carga del controlador y mejorando la escalabilidad. Aunque se centra en TCP SYN flood, los principios son extensibles a otros tipos de ataques.

---

**Referencia:**  
Musumeci, F., Fidanci, A. C., Paolucci, F., Cugini, F., & Tornatore, M. (2022). Machine-Learning-Enabled DDoS Attacks Detection in P4 Programmable Networks. *Journal of Network and Systems Management*, 30(21), 1-27.