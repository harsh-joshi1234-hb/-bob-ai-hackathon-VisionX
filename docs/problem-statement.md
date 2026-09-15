# Problem Statement

## The Semiconductor Yield Problem
In modern semiconductor manufacturing, yield optimization is a critical financial and operational challenge. Fabricating a single wafer involves hundreds of complex physical and chemical steps. Even minor deviations in equipment performance or environmental conditions can cause micro-defects on the wafer, rendering expensive silicon chips unusable and drastically reducing overall yield. 

## Wafer Defect Patterns and Process Signals
When defects occur, they often form distinct spatial patterns on the wafer map (e.g., edge rings, center clusters, scratch lines). Simultaneously, fabrication equipment generates massive volumes of high-frequency time-series data from hundreds of process and sensor signals (temperature, pressure, gas flow rates). These two data modalities—spatial defect patterns and tabular sensor metrics—are intrinsically linked but typically siloed in different analytical systems.

## The Bottleneck of Manual Root-Cause Investigation
When a defective batch is identified, process engineers must manually investigate the root cause. This involves visually inspecting wafer maps, identifying the defect pattern, and then manually cross-referencing that pattern against hundreds of thousands of data points from the process sensors to find the anomalous signal. This manual investigation is extremely time-consuming, prone to human error, and often requires deep domain expertise. While engineers are investigating, the manufacturing line may continue to produce defective wafers, or production might be halted entirely, leading to millions of dollars in lost throughput.

## Upcoming Batch Risk
Furthermore, traditional systems are primarily reactive. They alert engineers only *after* a wafer has been fully processed and tested. There is a lack of predictive capabilities to assess the risk of "upcoming batches" based on real-time sensor drift or subtle equipment degradation before the wafers are actually ruined.

## Why Early Detection Matters
Early detection and automated root-cause analysis are paramount. By instantly correlating wafer defect classifications with the exact anomalous process sensors (using techniques like SHAP), engineers can immediately apply corrective actions to the equipment. Predicting risks for upcoming batches allows for preventative maintenance, reducing scrapped wafers, maximizing equipment uptime, and saving millions in manufacturing costs.
