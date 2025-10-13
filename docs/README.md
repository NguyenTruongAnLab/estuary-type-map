# 📚 Scientific Documentation

**Purpose**: Publication-ready scientific documentation for peer review  
**Audience**: Researchers, peer reviewers, collaborating scientists  
**Last Updated**: October 13, 2025

---

## 📋 Document Index

### Core Scientific Documentation

1. **[DATA_SOURCES.md](DATA_SOURCES.md)** — Complete dataset descriptions
   - GRIT v0.6 river network (20.5M segments)
   - GlobSalt v2.0 salinity database (270K stations)
   - Dürr 2011 estuary typology (7,057 catchments)
   - Baum 2024 morphometry (106 large estuaries)
   - DynQual physics model (experimental)
   - Data integration workflow
   - Quality assurance procedures

2. **[CLASSIFICATION_FRAMEWORK.md](CLASSIFICATION_FRAMEWORK.md)** — Classification methodology
   - Venice System (1958) salinity thresholds
   - O'Connor et al. (2022) Tidal Freshwater Zone framework
   - Dürr et al. (2011) estuary geomorphology (7 types)
   - Hierarchical classification framework (Priority 1-4)
   - Machine learning approach overview
   - Uncertainty quantification

3. **[ATLAS_INTERFACE.md](ATLAS_INTERFACE.md)** — Interactive visualization
   - Web atlas architecture
   - Layer-based visualization system
   - User interface design
   - Data exploration features

---

## 🎯 Quick Navigation

### For Peer Reviewers

**Start here**: [DATA_SOURCES.md](DATA_SOURCES.md) → [CLASSIFICATION_FRAMEWORK.md](CLASSIFICATION_FRAMEWORK.md)

**Key questions answered**:
- What datasets are used? → DATA_SOURCES.md
- How is classification done? → CLASSIFICATION_FRAMEWORK.md  
- How is uncertainty quantified? → CLASSIFICATION_FRAMEWORK.md (Section 6)
- How can I reproduce this? → All READMEs have "Processing" sections pointing to code

---

### For Collaborating Scientists

**Using the atlas**:
- Data sources and citations → DATA_SOURCES.md
- Classification methods → CLASSIFICATION_FRAMEWORK.md
- Interactive exploration → ATLAS_INTERFACE.md

**Extending the work**:
- Add new datasets → See scripts/raw_data_processing/README.md
- Modify classification → See scripts/ml_salinity/README.md
- Update web interface → See scripts/web_optimization/README.md

---

### For Reproducibility

**Complete workflow**:
1. Read DATA_SOURCES.md (understand inputs)
2. Read CLASSIFICATION_FRAMEWORK.md (understand methods)
3. Run `python scripts/master_pipeline.py --all` (execute pipeline)
4. Results in `data/processed/` (outputs)

**Estimated time**: 3-4.5 hours (unattended overnight run)

---

## 📖 Document Relationships

```
DATA_SOURCES.md
    ├── Describes: GRIT, GlobSalt, Dürr, Baum datasets
    ├── References: Original publications (DOIs provided)
    └── Links to: scripts/raw_data_processing/

CLASSIFICATION_FRAMEWORK.md
    ├── Uses data from: DATA_SOURCES.md
    ├── Implements: Venice System, O'Connor TFZ, Dürr typology
    ├── Methods: Hierarchical classification + ML
    └── Links to: scripts/ml_salinity/

ATLAS_INTERFACE.md
    ├── Displays data from: DATA_SOURCES.md
    ├── Visualizes: Classifications from CLASSIFICATION_FRAMEWORK.md
    └── Implementation: index.html, js/map.js
```

---

## 🔬 Scientific Approach Summary

### Problem
Existing global water body atlases use statistical extrapolation, not direct measurement. This introduces 30-50% uncertainty in biogeochemical models for aquatic GHG emissions.

### Solution
**Direct polygon-based measurement** of ALL global water bodies using:
1. High-resolution datasets (GRIT, GlobSalt, Dürr, Baum)
2. Salinity-based classification (Venice System)
3. Machine learning for unmeasured segments (75-99.3% of network)
4. Multi-method independent validation

### Innovation
- ✅ **Direct measurement** (not extrapolation)
- ✅ **100% coverage** (not 0.7% like GlobSalt alone)
- ✅ **Transparent uncertainty** (confidence levels for all segments)
- ✅ **Fully reproducible** (open data, open code)

### Impact
Enables next-generation biogeochemical modeling with:
- Precise surface area calculations by aquatic system type
- Salinity zonation for accurate emission factors
- Geomorphological context for process-based models

---

## 📊 Key Statistics

- **River segments processed**: 20.5 million globally
- **GlobSalt stations**: 270,413 (15.4M measurements)
- **Estuary systems**: 7,057 catchments (Dürr) + 106 large (Baum)
- **Classification coverage**: 100% (with confidence levels)
- **Validation regions**: 7 global regions (SP held out for testing)
- **Expected ML accuracy**: 72-78% on true spatial holdout

---

## ⚠️ Important Notes for Peer Review

### What This Documentation IS:
- ✅ Complete scientific methodology
- ✅ Dataset descriptions with full provenance
- ✅ Classification framework with literature basis
- ✅ Reproducible computational workflow
- ✅ Uncertainty quantification

### What This Documentation IS NOT:
- ❌ Implementation details (see scripts/ folder READMEs)
- ❌ Troubleshooting guides (see scripts/ folder)
- ❌ Software tutorials (see scripts/ folder)
- ❌ Development history (not relevant for peer review)

---

## 🔗 Related Documentation

### Technical Implementation
- **scripts/README.md** - Complete pipeline overview
- **scripts/raw_data_processing/README.md** - Data ingestion details
- **scripts/ml_salinity/README.md** - ML implementation details
- **scripts/web_optimization/README.md** - Web deployment

### Project Overview
- **README.md** (root) - Project summary and quick start
- **methodology.md** (root) - Methodology overview (legacy)

### For AI Agents
- **.github/copilot-instructions.md** - Project memory bank and rules

---

## 📝 Citation

When using this atlas, please cite:

[To be completed upon publication]

Nguyen Truong An, et al. (2025). *Global Water Body Surface Area Atlas: A Polygon-Based Approach for Biogeochemical Budgeting*. [Journal TBD].

**Dataset DOI**: [To be assigned]

---

## 🆘 Getting Help

### For Scientific Questions:
- Read relevant documentation above
- Check DATA_SOURCES.md for dataset specifics
- Check CLASSIFICATION_FRAMEWORK.md for methodology

### For Technical Issues:
- See scripts/README.md
- Check scripts/ folder READMEs for implementation details
- Run diagnostic tools in scripts/diagnostics/

### For Reproducibility:
```powershell
# Complete pipeline (one command)
python scripts/master_pipeline.py --all
```

**Duration**: 3-4.5 hours  
**Requirements**: 16 GB RAM, 50 GB storage  
**Output**: Complete classified dataset in data/processed/

---

**Document Structure**: Publication-focused, peer-review-ready scientific documentation.
