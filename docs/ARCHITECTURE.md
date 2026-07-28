# DSER Architecture

The model is implemented under `src/dser/models/`.

| Paper component | Implementation |
| --- | --- |
| Event-aware reference reconstruction | `EventAwareReferenceReconstructor` |
| Bidirectional event-guided PCD alignment | `BidirectionalEPCD` |
| Direct reference synthesis | `ReferenceFusion` |
| Prediction refinement | `TransformerDecoder` |
| Complete network | `DSER` |

The training loop is in `src/dser/engine/train.py`; datasets are in `src/dser/data/datasets.py`.
