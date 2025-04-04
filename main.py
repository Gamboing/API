# python -m venv venv
# venv\Scripts\activate
# pip install -r requirements.txt
from utils import read_csv, write_csv, delete_csv, update_csv
from fastapi import FastAPI

app=FastAPI()
@app.get("/")
def hello_world():
    return {"message": "Welcome to the API"}

@app.get("/products/")
def get_products():
    return read_csv()

@app.post("/products/")
def add_product(name:str , price: float):
    products=read_csv()
    new_id=len(products)+1
    write_csv([new_id,name,price])
    return {"message": "Producto agregado", "id": new_id}

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    delete_csv(product_id)
    return {"message": "Producto eliminado"}

@app.put("/products/{product_id}")
def update_product(product_id: int, name: str, price: float):
    return update_csv(product_id, name, price)