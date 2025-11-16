# Kickplate Nesting Tool

This tool nests kickplates into finite stock sheets and offcuts.
Shelf algorithm. Grain logic. Offcuts-first. PDF label printing.

## Run
pip install -r requirements.txt  
streamlit run app.py

## Inputs
- CSV of plates (door,width,height,grain)
- Number of full sheets
- Offcut sizes

## Outputs
- Visual nested layouts
- PDF labels
- Material shortage warnings
