# Requirements
- Support all *verification methods*:
  - **Test**: run automated tests, show & save results.
  - **Demonstration**: run procedures, show & save results.
  - **Inspection**: run procedures, show & save results.
  - **Analysis**: show reports. 
- Show a dashboard with historical test run data and number of tests
- Show requirements traceability and acceptance criteria coverage
  - Store requirements and acceptance criteria (.yaml)
  - Scan tests for coverage (e.g., pytest markers)
- Show test plan (.md)
- Version control the test framework and all tests in a single repository
- Containerize application and use K8s to manage availability

# Test Artifacts
## Test
File formats: 
- Python (.py)

## Demonstration
File formats: 
- YAML (.yaml)

## Inspection
File formats: 
- YAML (.yaml)

## Analysis
File formats: 
- Quarto (.qmd)
- Markdown (.md)
- Jupyter Notebood (.ipynb)